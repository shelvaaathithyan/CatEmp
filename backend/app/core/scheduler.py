from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.core.rabbitmq import rabbitmq
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.rental import Rental
from app.models.machine import Machine
from datetime import datetime, timezone
import asyncio

scheduler = AsyncIOScheduler()

async def check_overdue_rentals():
    """Job that checks for overdue rentals and pushes notification events."""
    print("Running scheduled job: check_overdue_rentals")
    db: Session = SessionLocal()
    try:
        today = datetime.now(timezone.utc).date()
        overdue_rentals = db.query(Rental).filter(
            Rental.rental_status == "ACTIVE",
            Rental.expected_return_date < today
        ).all()
        
        for rental in overdue_rentals:
            # Notify the customer
            payload = {
                "user_id": rental.customer.user_id,
                "title": "Overdue Rental",
                "message": f"Your rental for {rental.equipment_id} is overdue since {rental.expected_return_date}.",
                "equipment_id": rental.equipment_id,
                "priority": "HIGH",
                "notification_type": "ALERT"
            }
            await rabbitmq.publish_message(payload)
    except Exception as e:
        print(f"Error in check_overdue_rentals: {e}")
    finally:
        db.close()

async def check_maintenance_due():
    """Job that checks for machines needing maintenance."""
    print("Running scheduled job: check_maintenance_due")
    db: Session = SessionLocal()
    try:
        maintenance_machines = db.query(Machine).filter(Machine.status == "MAINTENANCE").all()
        
        for machine in maintenance_machines:
            # Notify the dealer
            payload = {
                "user_id": machine.dealer.user_id,
                "title": "Maintenance Required",
                "message": f"Machine {machine.equipment_id} is flagged for maintenance.",
                "equipment_id": machine.equipment_id,
                "priority": "MEDIUM",
                "notification_type": "MAINTENANCE"
            }
            await rabbitmq.publish_message(payload)
    except Exception as e:
        print(f"Error in check_maintenance_due: {e}")
    finally:
        db.close()

def start_scheduler():
    # Run overdue check every day (or every minute for testing)
    scheduler.add_job(check_overdue_rentals, 'cron', hour=0, minute=0)
    # Run maintenance check
    scheduler.add_job(check_maintenance_due, 'cron', hour=1, minute=0)
    
    # For testing/hackathon purposes, we can also add an interval job
    # scheduler.add_job(check_overdue_rentals, 'interval', minutes=5)
    
    scheduler.start()
    print("APScheduler started.")
