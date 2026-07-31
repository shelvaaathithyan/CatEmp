import random
from datetime import datetime, timedelta, timezone
from app.core.database import SessionLocal
from app.models.rental import Rental
from app.models.customer import Customer
from app.models.dealer import Dealer
from app.models.machine import Machine
from app.models.site import Site
from app.models.fleet_manager import FleetManager

def add_historical_data():
    db = SessionLocal()
    try:
        customers = db.query(Customer).all()
        dealers = db.query(Dealer).all()
        sites = db.query(Site).all()
        fleet_mgrs = db.query(FleetManager).all()
        machines = db.query(Machine).all()
        
        if not customers or not dealers or not machines:
            print("Database is empty. Please run seed_db.py first.")
            return

        now = datetime.now(timezone.utc)
        
        print("Adding historical rentals for trend charts...")
        
        for c in customers:
            # Add 2-3 rentals per month for the last 6 months
            for month_offset in range(6):
                date_in_month = now - timedelta(days=month_offset * 30 + 15)
                
                num_rentals = random.randint(1, 3)
                for _ in range(num_rentals):
                    machine = random.choice(machines)
                    site = random.choice([s for s in sites if s.customer_id == c.id]) if any(s.customer_id == c.id for s in sites) else random.choice(sites)
                    fm = random.choice([f for f in fleet_mgrs if f.site_id == site.id]) if any(f.site_id == site.id for f in fleet_mgrs) else random.choice(fleet_mgrs)
                    
                    cost = round(random.uniform(1500.0, 5000.0), 2)
                    
                    rental = Rental(
                        equipment_id=machine.equipment_id,
                        customer_id=c.id,
                        site_id=site.id,
                        fleet_manager_id=fm.id,
                        check_in_date=date_in_month.date(),
                        expected_return_date=(date_in_month + timedelta(days=random.randint(5, 20))).date(),
                        actual_return_date=(date_in_month + timedelta(days=random.randint(5, 20))).date(),
                        rental_cost=cost,
                        rental_status="COMPLETED"
                    )
                    db.add(rental)
        
        db.commit()
        print("Historical rentals successfully added to the database!")
        
    except Exception as e:
        print(f"Failed: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_historical_data()
