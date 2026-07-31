from sqlalchemy.orm import Session
from app.models.rental import Rental
from app.models.site_transfer import SiteTransfer
from app.models.checkin_checkout import CheckinCheckout
from app.models.equipment_usage import EquipmentUsage
from app.models.maintenance import MaintenanceHistory

class TimelineService:
    @staticmethod
    def get_machine_timeline(db: Session, equipment_id: str) -> dict:
        """Aggregates all historical events for a given machine and sorts them chronologically."""
        events = []
        
        # Rentals
        rentals = db.query(Rental).filter(Rental.equipment_id == equipment_id).all()
        for r in rentals:
            events.append({
                "type": "RENTAL_CREATED",
                "timestamp": r.created_at,
                "details": f"Rental {r.id} created for Customer {r.customer_id}"
            })
            
        # Site Transfers
        transfers = db.query(SiteTransfer).filter(SiteTransfer.equipment_id == equipment_id).all()
        for t in transfers:
            events.append({
                "type": "SITE_TRANSFER",
                "timestamp": t.transfer_date,
                "details": f"Transferred to site {t.to_site_id} by {t.transferred_by}"
            })
            
        # Check-in / Check-out
        # Filter by rentals of this machine
        rental_ids = [r.id for r in rentals]
        if rental_ids:
            checks = db.query(CheckinCheckout).filter(CheckinCheckout.rental_id.in_(rental_ids)).all()
            for c in checks:
                events.append({
                    "type": f"ACTION_{c.action.upper()}",
                    "timestamp": c.timestamp,
                    "details": f"Action performed by {c.performed_by}"
                })
                
        # Maintenance
        maintenance = db.query(MaintenanceHistory).filter(MaintenanceHistory.equipment_id == equipment_id).all()
        for m in maintenance:
            events.append({
                "type": "MAINTENANCE",
                # convert date to datetime for sorting
                "timestamp": m.service_date,
                "details": f"Service type: {m.service_type}"
            })
            
        # Sort all events chronologically
        # Note: Mixing datetime and date can raise exceptions, ensuring all are comparable
        def get_sort_key(event):
            ts = event["timestamp"]
            import datetime
            if not ts:
                return datetime.datetime.min.replace(tzinfo=datetime.timezone.utc)
            if isinstance(ts, datetime.datetime):
                if ts.tzinfo is None:
                    return ts.replace(tzinfo=datetime.timezone.utc)
                return ts
            elif isinstance(ts, datetime.date):
                return datetime.datetime.combine(ts, datetime.datetime.min.time()).replace(tzinfo=datetime.timezone.utc)
            return ts
            
        events.sort(key=get_sort_key)
        
        return {
            "equipment_id": equipment_id,
            "timeline": events
        }

timeline_service = TimelineService()
