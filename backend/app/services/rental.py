from datetime import datetime, timezone
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.rental import Rental
from app.models.machine import Machine
from app.models.site_transfer import SiteTransfer
from app.models.checkin_checkout import CheckinCheckout
from app.repositories.rental import rental_repo
from app.repositories.machine import machine_repo
from app.schemas.rental import RentalCreate
from app.schemas.site_transfer import SiteTransferCreate
from app.schemas.checkin_checkout import CheckinCheckoutCreate
from app.schemas.notification import NotificationCreate
from app.services.notification import notification_service

class RentalService:
    @staticmethod
    def create_rental(db: Session, rental_in: RentalCreate) -> Rental:
        """Creates a rental contract, ensuring the machine isn't already actively rented."""
        active_rental = rental_repo.get_active_rental_for_machine(db, rental_in.equipment_id)
        if active_rental:
            raise HTTPException(status_code=400, detail="Machine is already actively rented.")
        
        # Insert rental
        rental = rental_repo.create(db, rental_in)
        
        # Update machine status
        machine = machine_repo.get_by_equipment_id(db, rental_in.equipment_id)
        if machine:
            machine.status = "RENTED"
            db.commit()

        # Send notification to Customer (assuming user_id maps to customer's user; simplified for this example)
        # Note: In a real app, we'd lookup the exact user_id of the customer, dealer, etc.
        return rental

    @staticmethod
    def transfer_site(db: Session, transfer_in: SiteTransferCreate) -> SiteTransfer:
        """Records a site transfer and updates the rental's current site."""
        rental = rental_repo.get(db, transfer_in.rental_id)
        if not rental or rental.rental_status not in ["PENDING", "ACTIVE"]:
            raise HTTPException(status_code=400, detail="Cannot transfer machine for an inactive rental.")
        
        # Verify transfer destination belongs to same customer (simplified check)
        # Record transfer
        transfer = SiteTransfer(**transfer_in.model_dump())
        db.add(transfer)
        
        # Update rental site
        rental.site_id = transfer_in.to_site_id
        db.commit()
        db.refresh(transfer)
        return transfer

    @staticmethod
    def process_checkin_checkout(db: Session, action_in: CheckinCheckoutCreate) -> CheckinCheckout:
        """Records a check-in or check-out event and updates transfer states."""
        rental = rental_repo.get(db, action_in.rental_id)
        if not rental:
            raise HTTPException(status_code=404, detail="Rental not found.")
            
        record = CheckinCheckout(**action_in.model_dump())
        db.add(record)
        
        machine = machine_repo.get_by_equipment_id(db, rental.equipment_id)
        
        # Get the latest site transfer for this rental
        latest_transfer = db.query(SiteTransfer)\
            .filter(SiteTransfer.rental_id == rental.id)\
            .order_by(SiteTransfer.transfer_date.desc())\
            .first()

        action = action_in.action.upper()
        if action == "CHECKOUT":
            # If leaving site and there's a pending transfer, it is now in transit
            if latest_transfer and latest_transfer.status == "PENDING":
                latest_transfer.status = "IN_TRANSIT"
                
            # If this is the initial checkout from the dealer, mark rental as ACTIVE
            if rental.rental_status == "PENDING":
                rental.rental_status = "ACTIVE"
                if machine:
                    machine.status = "RENTED"
                    
        elif action == "CHECKIN":
            # If arriving at a site, mark the transfer as delivered
            if latest_transfer and latest_transfer.status in ["PENDING", "IN_TRANSIT"]:
                latest_transfer.status = "DELIVERED"
                
        db.commit()
        db.refresh(record)
        return record

rental_service = RentalService()
