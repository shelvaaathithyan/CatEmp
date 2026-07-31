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
from app.models.predictions import DemandPrediction, UtilizationPrediction, MaintenancePrediction
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
            User(email="customera@cat.com", password_hash=password, role="Customer", name="Customer A"),
            User(email="customerb@cat.com", password_hash=password, role="Customer", name="Customer B"),
            User(email="fleeta@cat.com", password_hash=password, role="Fleet Manager", name="Fleet A"),
            User(email="fleetb@cat.com", password_hash=password, role="Fleet Manager", name="Fleet B"),
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
            Customer(user_id=users_data[4].id, company_name="BuildIt Right Corp."),
            Customer(user_id=users_data[7].id, company_name="Customer A Company"),
            Customer(user_id=users_data[8].id, company_name="Customer B Company")
        ]
        db.add_all(dealers + customers)
        db.commit()
        for d in dealers: db.refresh(d)
        for c in customers: db.refresh(c)

        # --- 3. SITES & FLEET MANAGERS ---
        sites = [
            Site(customer_id=customers[0].id, site_code="S-001", site_name="Downtown Skyscraper Project"),
            Site(customer_id=customers[0].id, site_code="S-002", site_name="Highway 61 Expansion"),
            Site(customer_id=customers[1].id, site_code="S-003", site_name="Suburban Housing Dev"),
            Site(customer_id=customers[2].id, site_code="S-004", site_name="Site A"),
            Site(customer_id=customers[3].id, site_code="S-005", site_name="Site B")
        ]
        db.add_all(sites)
        db.commit()
        for s in sites: db.refresh(s)

        fleet_mgrs = [
            FleetManager(user_id=users_data[5].id, site_id=sites[0].id),
            FleetManager(user_id=users_data[6].id, site_id=sites[1].id),
            FleetManager(user_id=users_data[9].id, site_id=sites[3].id),
            FleetManager(user_id=users_data[10].id, site_id=sites[4].id)
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
            Machine(equipment_id="BD-001", dealer_id=dealers[0].id, equipment_type="Bulldozer", model="D6", status="MAINTENANCE"),
            Machine(equipment_id="NEW-001", dealer_id=dealers[0].id, equipment_type="Excavator", model="320 GC", status="RENTED"),
            Machine(equipment_id="NEW-002", dealer_id=dealers[1].id, equipment_type="Excavator", model="320 GC", status="RENTED"),
            Machine(equipment_id="EX-003", dealer_id=dealers[0].id, equipment_type="Excavator", model="320 GC", status="RENTED"),
            Machine(equipment_id="EX-004", dealer_id=dealers[1].id, equipment_type="Excavator", model="336", status="RENTED"),
            Machine(equipment_id="WL-002", dealer_id=dealers[1].id, equipment_type="Wheel Loader", model="950 GC", status="MAINTENANCE"),
            Machine(equipment_id="BD-002", dealer_id=dealers[0].id, equipment_type="Bulldozer", model="D6", status="RENTED"),
            Machine(equipment_id="AT-001", dealer_id=dealers[0].id, equipment_type="Articulated Truck", model="745", status="RENTED"),
            Machine(equipment_id="MG-001", dealer_id=dealers[1].id, equipment_type="Motor Grader", model="140 GC", status="RENTED")
        ]
        db.add_all(machines)
        db.commit()
        logger.info("Machines seeded.")

        # --- 5. OPERATORS ---
        operators = [
            Operator(operator_id="OP-001", customer_id=customers[0].id, operator_name="John Doe"),
            Operator(operator_id="OP-002", customer_id=customers[1].id, operator_name="Jane Smith"),
            Operator(operator_id="OP-003", customer_id=customers[2].id, operator_name="Mike Johnson"),
            Operator(operator_id="OP-004", customer_id=customers[3].id, operator_name="Sarah Williams")
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
        
        # Usage for rental_b (Diana Builders)
        for i in range(5):
            db.add(EquipmentUsage(rental_id=rental_b.id, equipment_id="EX-002", site_id=sites[2].id, usage_date=today - timedelta(days=20-i), engine_hours_per_day=7.5, idle_hours_per_day=2.5, rental_days=i+1, last_operator_id="OP-002"))

        # Scenario C: WL-001 (Active)
        rental_c = Rental(
            equipment_id="WL-001", customer_id=customers[0].id, site_id=sites[1].id, fleet_manager_id=fleet_mgrs[1].id,
            check_in_date=today - timedelta(days=1), expected_return_date=today + timedelta(days=30), rental_status="ACTIVE"
        )
        db.add(rental_c)
        db.commit()
        db.refresh(rental_c)
        db.add(CheckinCheckout(rental_id=rental_c.id, performed_by=fleet_mgrs[1].id, action="CHECKOUT", timestamp=now - timedelta(days=1)))

        # Scenario D: customerA / fleetA / dealer1
        rental_d = Rental(
            equipment_id="NEW-001", customer_id=customers[2].id, site_id=sites[3].id, fleet_manager_id=fleet_mgrs[2].id,
            check_in_date=today - timedelta(days=5), expected_return_date=today + timedelta(days=10), rental_status="ACTIVE"
        )
        db.add(rental_d)
        
        # Scenario E: customerB / fleetB / dealer2
        rental_e = Rental(
            equipment_id="NEW-002", customer_id=customers[3].id, site_id=sites[4].id, fleet_manager_id=fleet_mgrs[3].id,
            check_in_date=today - timedelta(days=5), expected_return_date=today + timedelta(days=10), rental_status="ACTIVE"
        )
        db.add(rental_e)

        # ----------------------------------------------------
        # --- NEW SCENARIOS FOR EXTENDED TELEMETRY MACHINES ---
        # ----------------------------------------------------
        # EX-003 (customerA / fleetA / dealer1)
        rental_f = Rental(
            equipment_id="EX-003", customer_id=customers[2].id, site_id=sites[3].id, fleet_manager_id=fleet_mgrs[2].id,
            check_in_date=today - timedelta(days=8), expected_return_date=today + timedelta(days=5), rental_status="ACTIVE"
        )
        db.add(rental_f)
        db.commit()
        db.refresh(rental_f)
        db.add(CheckinCheckout(rental_id=rental_f.id, performed_by=fleet_mgrs[2].id, action="CHECKOUT", timestamp=now - timedelta(days=8)))
        # Usage for EX-003
        for i in range(4):
            db.add(EquipmentUsage(rental_id=rental_f.id, equipment_id="EX-003", site_id=sites[3].id, usage_date=today - timedelta(days=i+1), engine_hours_per_day=9.5, idle_hours_per_day=1.5, rental_days=1, last_operator_id="OP-003"))

        # EX-004 (customerB / fleetB / dealer2)
        rental_g = Rental(
            equipment_id="EX-004", customer_id=customers[3].id, site_id=sites[4].id, fleet_manager_id=fleet_mgrs[3].id,
            check_in_date=today - timedelta(days=12), expected_return_date=today + timedelta(days=2), rental_status="ACTIVE"
        )
        db.add(rental_g)
        db.commit()
        db.refresh(rental_g)
        db.add(CheckinCheckout(rental_id=rental_g.id, performed_by=fleet_mgrs[3].id, action="CHECKOUT", timestamp=now - timedelta(days=12)))
        db.add(SiteTransfer(rental_id=rental_g.id, equipment_id="EX-004", from_site_id=sites[2].id, to_site_id=sites[4].id, transferred_by=fleet_mgrs[3].id, transfer_date=now - timedelta(days=5)))
        # Usage for EX-004
        for i in range(4):
            db.add(EquipmentUsage(rental_id=rental_g.id, equipment_id="EX-004", site_id=sites[4].id, usage_date=today - timedelta(days=i+1), engine_hours_per_day=8.0, idle_hours_per_day=2.5, rental_days=1, last_operator_id="OP-004"))

        # WL-002 (customer 1 / site 2 / dealer 2) - Maintenance
        rental_h = Rental(
            equipment_id="WL-002", customer_id=customers[0].id, site_id=sites[1].id, fleet_manager_id=fleet_mgrs[1].id,
            check_in_date=today - timedelta(days=30), expected_return_date=today + timedelta(days=15), rental_status="ACTIVE"
        )
        db.add(rental_h)
        db.commit()
        db.refresh(rental_h)
        db.add(MaintenanceHistory(equipment_id="WL-002", service_date=today - timedelta(days=1), service_type="Hydraulics", remarks="Major hydraulic fluid leak"))
        # Usage for WL-002
        for i in range(4):
            db.add(EquipmentUsage(rental_id=rental_h.id, equipment_id="WL-002", site_id=sites[1].id, usage_date=today - timedelta(days=i+1), engine_hours_per_day=2.0, idle_hours_per_day=6.0, rental_days=1, last_operator_id="OP-001"))

        # BD-002 (customerA / fleetA / dealer 1)
        rental_i = Rental(
            equipment_id="BD-002", customer_id=customers[2].id, site_id=sites[3].id, fleet_manager_id=fleet_mgrs[2].id,
            check_in_date=today - timedelta(days=15), expected_return_date=today + timedelta(days=10), rental_status="ACTIVE"
        )
        db.add(rental_i)
        db.commit()
        db.refresh(rental_i)
        db.add(SiteTransfer(rental_id=rental_i.id, equipment_id="BD-002", from_site_id=sites[0].id, to_site_id=sites[3].id, transferred_by=fleet_mgrs[2].id, transfer_date=now - timedelta(days=1)))
        
        # AT-001 (customer 0 / fleet 0 / dealer 1)
        rental_j = Rental(
            equipment_id="AT-001", customer_id=customers[0].id, site_id=sites[0].id, fleet_manager_id=fleet_mgrs[0].id,
            check_in_date=today - timedelta(days=6), expected_return_date=today + timedelta(days=20), rental_status="ACTIVE"
        )
        db.add(rental_j)
        db.commit()
        db.refresh(rental_j)
        db.add(CheckinCheckout(rental_id=rental_j.id, performed_by=fleet_mgrs[0].id, action="CHECKOUT", timestamp=now - timedelta(days=6)))

        # MG-001 (customer B / fleet B / dealer 2)
        rental_k = Rental(
            equipment_id="MG-001", customer_id=customers[3].id, site_id=sites[4].id, fleet_manager_id=fleet_mgrs[3].id,
            check_in_date=today - timedelta(days=3), expected_return_date=today + timedelta(days=8), rental_status="ACTIVE"
        )
        db.add(rental_k)
        db.commit()
        db.refresh(rental_k)
        db.add(SiteTransfer(rental_id=rental_k.id, equipment_id="MG-001", from_site_id=sites[1].id, to_site_id=sites[4].id, transferred_by=fleet_mgrs[3].id, transfer_date=now + timedelta(days=1)))


        db.commit()
        for r in [rental_d, rental_e]: db.refresh(r)
        
        # --- 6b. USAGE DATA FOR NEW RENTALS ---
        db.add(EquipmentUsage(rental_id=rental_d.id, equipment_id="NEW-001", site_id=sites[3].id, usage_date=today - timedelta(days=1), engine_hours_per_day=8.2, idle_hours_per_day=1.5, rental_days=4, last_operator_id="OP-003"))
        db.add(EquipmentUsage(rental_id=rental_e.id, equipment_id="NEW-002", site_id=sites[4].id, usage_date=today - timedelta(days=1), engine_hours_per_day=7.5, idle_hours_per_day=2.0, rental_days=4, last_operator_id="OP-004"))
        db.commit()
        logger.info("Rentals and historical events seeded.")

        # --- 7. PREDICTIONS & NOTIFICATIONS ---

        # Demand Predictions
        demand_preds = [
            DemandPrediction(prediction_timestamp=now, equipment_type="CAT 320 GC (Excavator)", site_id=sites[0].id, prediction_period="Next 30 Days", expected_demand=5),
            DemandPrediction(prediction_timestamp=now, equipment_type="CAT 950 GC (Wheel Loader)", site_id=sites[0].id, prediction_period="Next 30 Days", expected_demand=3),
            DemandPrediction(prediction_timestamp=now, equipment_type="CAT D6 LMT (Bulldozer)", site_id=sites[1].id, prediction_period="Next 30 Days", expected_demand=2),
            DemandPrediction(prediction_timestamp=now, equipment_type="CAT 777 OHT (Off-Highway Truck)", site_id=sites[1].id, prediction_period="Next 30 Days", expected_demand=7),
            DemandPrediction(prediction_timestamp=now, equipment_type="CAT 320 GC (Excavator)", site_id=sites[2].id, prediction_period="Next 30 Days", expected_demand=4),
            DemandPrediction(prediction_timestamp=now, equipment_type="CAT 950 GC (Wheel Loader)", site_id=sites[2].id, prediction_period="Next 30 Days", expected_demand=6),
            DemandPrediction(prediction_timestamp=now - timedelta(days=30), equipment_type="CAT 320 GC (Excavator)", site_id=sites[0].id, prediction_period="Next 30 Days", expected_demand=4),
            DemandPrediction(prediction_timestamp=now - timedelta(days=30), equipment_type="CAT 950 GC (Wheel Loader)", site_id=sites[1].id, prediction_period="Next 30 Days", expected_demand=2),
        ]
        db.add_all(demand_preds)

        # Utilization Predictions
        util_preds = [
            UtilizationPrediction(prediction_timestamp=now, equipment_id="EX-001", utilization_score=0.81, predicted_idle_hours=45.6, status="Running"),
            UtilizationPrediction(prediction_timestamp=now, equipment_id="EX-002", utilization_score=0.13, predicted_idle_hours=195.0, status="Idle"),
            UtilizationPrediction(prediction_timestamp=now, equipment_id="WL-001", utilization_score=0.82, predicted_idle_hours=45.0, status="Running"),
            UtilizationPrediction(prediction_timestamp=now, equipment_id="BD-001", utilization_score=0.20, predicted_idle_hours=160.0, status="Idle"),
            UtilizationPrediction(prediction_timestamp=now, equipment_id="NEW-001", utilization_score=0.75, predicted_idle_hours=60.0, status="Running"),
            UtilizationPrediction(prediction_timestamp=now, equipment_id="NEW-002", utilization_score=0.65, predicted_idle_hours=84.0, status="Running"),
        ]
        db.add_all(util_preds)

        # Maintenance Predictions
        maint_preds = [
            MaintenancePrediction(equipment_id="EX-001", prediction_timestamp=now, maintenance_probability=0.15, predicted_service_date=today + timedelta(days=45), confidence=0.88),
            MaintenancePrediction(equipment_id="EX-002", prediction_timestamp=now, maintenance_probability=0.85, predicted_service_date=today + timedelta(days=5), confidence=0.92),
            MaintenancePrediction(equipment_id="WL-001", prediction_timestamp=now, maintenance_probability=0.35, predicted_service_date=today + timedelta(days=30), confidence=0.78),
            MaintenancePrediction(equipment_id="BD-001", prediction_timestamp=now, maintenance_probability=0.72, predicted_service_date=today + timedelta(days=8), confidence=0.90),
            MaintenancePrediction(equipment_id="NEW-002", prediction_timestamp=now, maintenance_probability=0.45, predicted_service_date=today + timedelta(days=20), confidence=0.82),
            MaintenancePrediction(equipment_id="WL-002", prediction_timestamp=now, maintenance_probability=0.91, predicted_service_date=today + timedelta(days=2), confidence=0.96),
            MaintenancePrediction(equipment_id="EX-003", prediction_timestamp=now, maintenance_probability=0.25, predicted_service_date=today + timedelta(days=40), confidence=0.80),
        ]
        db.add_all(maint_preds)
        
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
