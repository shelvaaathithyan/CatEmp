import logging
from datetime import date, datetime, timedelta, timezone
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.dealer import Dealer
from app.models.customer import Customer
from app.models.site import Site
from app.models.fleet_manager import FleetManager
from app.models.machine import Machine
from app.models.rental import Rental
from app.models.checkin_checkout import CheckinCheckout
from app.models.site_transfer import SiteTransfer
from app.models.equipment_usage import EquipmentUsage
from app.models.maintenance import MaintenanceHistory
from app.models.predictions import MaintenancePrediction

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def seed_new_machines():
    db: Session = SessionLocal()
    try:
        logger.info("Starting to seed additional machines...")
        
        dealers = db.query(Dealer).order_by(Dealer.id).all()
        customers = db.query(Customer).order_by(Customer.id).all()
        sites = db.query(Site).order_by(Site.id).all()
        fleet_mgrs = db.query(FleetManager).order_by(FleetManager.id).all()

        now = datetime.now(timezone.utc)
        today = now.date()

        existing_machines = [m.equipment_id for m in db.query(Machine.equipment_id).all()]
        
        machines_to_add = []
        
        if "EX-003" not in existing_machines: machines_to_add.append(Machine(equipment_id="EX-003", dealer_id=dealers[0].id, equipment_type="Excavator", model="320 GC", status="RENTED"))
        if "EX-004" not in existing_machines: machines_to_add.append(Machine(equipment_id="EX-004", dealer_id=dealers[1].id, equipment_type="Excavator", model="336", status="RENTED"))
        if "WL-002" not in existing_machines: machines_to_add.append(Machine(equipment_id="WL-002", dealer_id=dealers[1].id, equipment_type="Wheel Loader", model="950 GC", status="MAINTENANCE"))
        if "BD-002" not in existing_machines: machines_to_add.append(Machine(equipment_id="BD-002", dealer_id=dealers[0].id, equipment_type="Bulldozer", model="D6", status="RENTED"))
        if "AT-001" not in existing_machines: machines_to_add.append(Machine(equipment_id="AT-001", dealer_id=dealers[0].id, equipment_type="Articulated Truck", model="745", status="RENTED"))
        if "MG-001" not in existing_machines: machines_to_add.append(Machine(equipment_id="MG-001", dealer_id=dealers[1].id, equipment_type="Motor Grader", model="140 GC", status="RENTED"))
        
        if machines_to_add:
            db.add_all(machines_to_add)
            db.commit()
            logger.info(f"Added {len(machines_to_add)} new machines.")

        c_len, s_len, fm_len = len(customers), len(sites), len(fleet_mgrs)

        # EX-003
        rental_f = Rental(equipment_id="EX-003", customer_id=customers[0%c_len].id, site_id=sites[0%s_len].id, fleet_manager_id=fleet_mgrs[0%fm_len].id, check_in_date=today - timedelta(days=8), expected_return_date=today + timedelta(days=5), rental_status="ACTIVE")
        db.add(rental_f)
        db.commit()
        db.refresh(rental_f)
        db.add(CheckinCheckout(rental_id=rental_f.id, performed_by=fleet_mgrs[0%fm_len].id, action="CHECKOUT", timestamp=now - timedelta(days=8)))
        for i in range(4): db.add(EquipmentUsage(rental_id=rental_f.id, equipment_id="EX-003", site_id=sites[0%s_len].id, usage_date=today - timedelta(days=i+1), engine_hours_per_day=9.5, idle_hours_per_day=1.5, rental_days=1, last_operator_id="OP-001"))

        # EX-004
        rental_g = Rental(equipment_id="EX-004", customer_id=customers[1%c_len].id, site_id=sites[1%s_len].id, fleet_manager_id=fleet_mgrs[1%fm_len].id, check_in_date=today - timedelta(days=12), expected_return_date=today + timedelta(days=2), rental_status="ACTIVE")
        db.add(rental_g)
        db.commit()
        db.refresh(rental_g)
        db.add(CheckinCheckout(rental_id=rental_g.id, performed_by=fleet_mgrs[1%fm_len].id, action="CHECKOUT", timestamp=now - timedelta(days=12)))
        db.add(SiteTransfer(rental_id=rental_g.id, equipment_id="EX-004", from_site_id=sites[0%s_len].id, to_site_id=sites[1%s_len].id, transferred_by=fleet_mgrs[1%fm_len].id, transfer_date=now - timedelta(days=5)))
        for i in range(4): db.add(EquipmentUsage(rental_id=rental_g.id, equipment_id="EX-004", site_id=sites[1%s_len].id, usage_date=today - timedelta(days=i+1), engine_hours_per_day=8.0, idle_hours_per_day=2.5, rental_days=1, last_operator_id="OP-002"))

        # WL-002
        rental_h = Rental(equipment_id="WL-002", customer_id=customers[0%c_len].id, site_id=sites[1%s_len].id, fleet_manager_id=fleet_mgrs[1%fm_len].id, check_in_date=today - timedelta(days=30), expected_return_date=today + timedelta(days=15), rental_status="ACTIVE")
        db.add(rental_h)
        db.commit()
        db.refresh(rental_h)
        db.add(MaintenanceHistory(equipment_id="WL-002", service_date=today - timedelta(days=1), service_type="Hydraulics", remarks="Major hydraulic fluid leak"))
        for i in range(4): db.add(EquipmentUsage(rental_id=rental_h.id, equipment_id="WL-002", site_id=sites[1%s_len].id, usage_date=today - timedelta(days=i+1), engine_hours_per_day=2.0, idle_hours_per_day=6.0, rental_days=1, last_operator_id="OP-001"))

        # BD-002
        rental_i = Rental(equipment_id="BD-002", customer_id=customers[1%c_len].id, site_id=sites[0%s_len].id, fleet_manager_id=fleet_mgrs[0%fm_len].id, check_in_date=today - timedelta(days=15), expected_return_date=today + timedelta(days=10), rental_status="ACTIVE")
        db.add(rental_i)
        db.commit()
        db.refresh(rental_i)
        db.add(SiteTransfer(rental_id=rental_i.id, equipment_id="BD-002", from_site_id=sites[1%s_len].id, to_site_id=sites[0%s_len].id, transferred_by=fleet_mgrs[0%fm_len].id, transfer_date=now - timedelta(days=1)))

        # AT-001
        rental_j = Rental(equipment_id="AT-001", customer_id=customers[0%c_len].id, site_id=sites[0%s_len].id, fleet_manager_id=fleet_mgrs[0%fm_len].id, check_in_date=today - timedelta(days=6), expected_return_date=today + timedelta(days=20), rental_status="ACTIVE")
        db.add(rental_j)
        db.commit()
        db.refresh(rental_j)
        db.add(CheckinCheckout(rental_id=rental_j.id, performed_by=fleet_mgrs[0%fm_len].id, action="CHECKOUT", timestamp=now - timedelta(days=6)))

        # MG-001
        rental_k = Rental(equipment_id="MG-001", customer_id=customers[1%c_len].id, site_id=sites[1%s_len].id, fleet_manager_id=fleet_mgrs[1%fm_len].id, check_in_date=today - timedelta(days=3), expected_return_date=today + timedelta(days=8), rental_status="ACTIVE")
        db.add(rental_k)
        db.commit()
        db.refresh(rental_k)
        db.add(SiteTransfer(rental_id=rental_k.id, equipment_id="MG-001", from_site_id=sites[0%s_len].id, to_site_id=sites[1%s_len].id, transferred_by=fleet_mgrs[1%fm_len].id, transfer_date=now + timedelta(days=1)))

        maint_preds = [
            MaintenancePrediction(equipment_id="WL-002", prediction_timestamp=now, maintenance_probability=0.91, predicted_service_date=today + timedelta(days=2), confidence=0.96),
            MaintenancePrediction(equipment_id="EX-003", prediction_timestamp=now, maintenance_probability=0.25, predicted_service_date=today + timedelta(days=40), confidence=0.80),
        ]
        db.add_all(maint_preds)

        db.commit()
        logger.info("Additional Rentals, Transfers, and Usage seeded perfectly.")

    except Exception as e:
        logger.error(f"Seeding failed: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_new_machines()
