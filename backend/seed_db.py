import logging
from datetime import date, datetime, timedelta, timezone
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.user import User
from app.models.dealer import Dealer
from app.models.customer import Customer
from app.models.site import Site
from app.models.fleet_manager import FleetManager
from app.models.machine import Machine
from app.models.operator import Operator
from app.models.rental import Rental
from app.models.checkin_checkout import CheckinCheckout
from app.models.site_transfer import SiteTransfer
from app.models.equipment_usage import EquipmentUsage
from app.models.maintenance import MaintenanceHistory
from app.models.predictions import DemandPrediction, UtilizationPrediction
from app.models.notification import Notification

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def seed_database():
    db: Session = SessionLocal()
    try:
        logger.info("Starting database seeding...")

        # --- 1. USERS ---
        password = get_password_hash("password123")
        users_data = [
            User(email="admin@cat.com", password_hash=password, role="CatAdmin", name="Super Admin"),
            User(email="dealer1@cat.com", password_hash=password, role="Dealer", name="Alice Dealer"),
            User(email="dealer2@cat.com", password_hash=password, role="Dealer", name="Bob Dealer"),
            User(email="customer1@cat.com", password_hash=password, role="Customer", name="Charlie Construction"),
            User(email="customer2@cat.com", password_hash=password, role="Customer", name="Diana Builders"),
            User(email="fleet1@cat.com", password_hash=password, role="Fleet Manager", name="Edward Fleet"),
            User(email="fleet2@cat.com", password_hash=password, role="Fleet Manager", name="Fiona Fleet"),
        ]
        db.add_all(users_data)
        db.commit()
        for u in users_data: db.refresh(u)
        logger.info("Users seeded.")

        # --- 2. PROFILES (Dealers & Customers) ---
        dealers = [
            Dealer(user_id=users_data[1].id, company_name="Caterpillar Global", address="100 Cat Way"),
            Dealer(user_id=users_data[2].id, company_name="Regional Cat Rentals", address="200 Reg Ave")
        ]
        customers = [
            Customer(user_id=users_data[3].id, company_name="Mega Construction Inc."),
            Customer(user_id=users_data[4].id, company_name="BuildIt Right Corp.")
        ]
        db.add_all(dealers + customers)
        db.commit()
        for d in dealers: db.refresh(d)
        for c in customers: db.refresh(c)

        # --- 3. SITES & FLEET MANAGERS ---
        sites = [
            Site(customer_id=customers[0].id, site_code="S-001", site_name="Downtown Skyscraper Project"),
            Site(customer_id=customers[0].id, site_code="S-002", site_name="Highway 61 Expansion"),
            Site(customer_id=customers[1].id, site_code="S-003", site_name="Suburban Housing Dev")
        ]
        db.add_all(sites)
        db.commit()
        for s in sites: db.refresh(s)

        fleet_mgrs = [
            FleetManager(user_id=users_data[5].id, site_id=sites[0].id),
            FleetManager(user_id=users_data[6].id, site_id=sites[1].id)
        ]
        db.add_all(fleet_mgrs)
        db.commit()
        for fm in fleet_mgrs: db.refresh(fm)
        logger.info("Profiles, Sites, and Fleet Managers seeded.")

        # --- 4. MACHINES ---
        machines = [
            Machine(equipment_id="EX-001", dealer_id=dealers[0].id, equipment_type="Excavator", model="320 GC", status="RENTED"),
            Machine(equipment_id="EX-002", dealer_id=dealers[0].id, equipment_type="Excavator", model="336", status="AVAILABLE"),
            Machine(equipment_id="WL-001", dealer_id=dealers[1].id, equipment_type="Wheel Loader", model="950 GC", status="RENTED"),
            Machine(equipment_id="BD-001", dealer_id=dealers[0].id, equipment_type="Bulldozer", model="D6", status="MAINTENANCE")
        ]
        db.add_all(machines)
        db.commit()
        logger.info("Machines seeded.")

        # --- 5. OPERATORS ---
        operators = [
            Operator(operator_id="OP-001", customer_id=customers[0].id, operator_name="John Doe"),
            Operator(operator_id="OP-002", customer_id=customers[1].id, operator_name="Jane Smith")
        ]
        db.add_all(operators)
        db.commit()

        now = datetime.now(timezone.utc)
        today = now.date()

        # --- 6. RENTALS & LIFECYCLE ---
        
        # Scenario A: EX-001 (Active, transferred)
        rental_a = Rental(
            equipment_id="EX-001", customer_id=customers[0].id, site_id=sites[1].id, fleet_manager_id=fleet_mgrs[0].id,
            check_in_date=today - timedelta(days=5), expected_return_date=today + timedelta(days=10), rental_status="ACTIVE"
        )
        db.add(rental_a)
        db.commit()
        db.refresh(rental_a)
        
        # Checkout Event
        db.add(CheckinCheckout(rental_id=rental_a.id, performed_by=fleet_mgrs[0].id, action="CHECKOUT", timestamp=now - timedelta(days=5)))
        # Site Transfer
        db.add(SiteTransfer(rental_id=rental_a.id, equipment_id="EX-001", from_site_id=sites[0].id, to_site_id=sites[1].id, transferred_by=fleet_mgrs[0].id, transfer_date=now - timedelta(days=2)))
        # Usage
        for i in range(3):
            db.add(EquipmentUsage(rental_id=rental_a.id, equipment_id="EX-001", site_id=sites[0].id, usage_date=today - timedelta(days=i+2), engine_hours_per_day=8.0, idle_hours_per_day=2.0, rental_days=1, last_operator_id="OP-001"))

        # Scenario B: EX-002 (Completed, Maintenance)
        rental_b = Rental(
            equipment_id="EX-002", customer_id=customers[1].id, site_id=sites[2].id, fleet_manager_id=fleet_mgrs[1].id,
            check_in_date=today - timedelta(days=20), expected_return_date=today - timedelta(days=10), actual_return_date=today - timedelta(days=10), rental_status="COMPLETED"
        )
        db.add(rental_b)
        db.commit()
        db.refresh(rental_b)
        
        db.add(CheckinCheckout(rental_id=rental_b.id, performed_by=fleet_mgrs[1].id, action="CHECKOUT", timestamp=now - timedelta(days=20)))
        db.add(CheckinCheckout(rental_id=rental_b.id, performed_by=fleet_mgrs[1].id, action="CHECKIN", timestamp=now - timedelta(days=10)))
        db.add(MaintenanceHistory(equipment_id="EX-002", service_date=today - timedelta(days=5), service_type="Oil Change", remarks="Routine 500-hour service"))

        # Scenario C: WL-001 (Active)
        rental_c = Rental(
            equipment_id="WL-001", customer_id=customers[0].id, site_id=sites[1].id, fleet_manager_id=fleet_mgrs[1].id,
            check_in_date=today - timedelta(days=1), expected_return_date=today + timedelta(days=30), rental_status="ACTIVE"
        )
        db.add(rental_c)
        db.commit()
        db.refresh(rental_c)
        db.add(CheckinCheckout(rental_id=rental_c.id, performed_by=fleet_mgrs[1].id, action="CHECKOUT", timestamp=now - timedelta(days=1)))

        db.commit()
        logger.info("Rentals and historical events seeded.")

        # --- 7. PREDICTIONS & NOTIFICATIONS ---
        db.add(DemandPrediction(prediction_timestamp=now, equipment_type="Excavator", site_id=sites[0].id, prediction_period="Next Month", expected_demand=5))
        db.add(UtilizationPrediction(prediction_timestamp=now, equipment_id="BD-001", utilization_score=0.2, predicted_idle_hours=12.5, status="UNDERUTILIZED"))
        
        db.add(Notification(user_id=users_data[3].id, equipment_id="EX-001", notification_type="RENTAL_CREATED", title="New Rental Active", message="Excavator EX-001 has been dispatched."))
        db.add(Notification(user_id=users_data[6].id, equipment_id="EX-001", notification_type="MACHINE_TRANSFERRED", title="Machine Transferred to your site", message="EX-001 arrived at Highway 61 Expansion."))
        
        db.commit()
        logger.info("Predictions and Notifications seeded.")
        logger.info("✅ Database seeding complete!")

    except Exception as e:
        logger.error(f"Seeding failed: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
