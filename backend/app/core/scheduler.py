from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.core.rabbitmq import rabbitmq
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.rental import Rental
from app.models.machine import Machine
from datetime import datetime, timezone, timedelta
import asyncio
from app.models.fleet_manager import FleetManager
from app.models.predictions import UtilizationPrediction

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

async def check_rental_expiring_tomorrow():
    """Job that checks for rentals expiring exactly tomorrow and notifies stakeholders."""
    print("Running scheduled job: check_rental_expiring_tomorrow")
    db: Session = SessionLocal()
    try:
        tomorrow = datetime.now(timezone.utc).date() + timedelta(days=1)
        expiring_rentals = db.query(Rental).filter(
            Rental.rental_status == "ACTIVE",
            Rental.expected_return_date == tomorrow
        ).all()
        
        for rental in expiring_rentals:
            machine = rental.machine
            
            # 1. Notify Customer
            if rental.customer:
                await rabbitmq.publish_message({
                    "user_id": rental.customer.user_id,
                    "title": "Rental Expiring Tomorrow",
                    "message": f"Your rental for {machine.model} ({machine.equipment_id}) expires tomorrow. Please prepare for return.",
                    "equipment_id": machine.equipment_id,
                    "priority": "HIGH",
                    "notification_type": "ALERT"
                })
                
            # 2. Notify Dealer
            if machine.dealer:
                await rabbitmq.publish_message({
                    "user_id": machine.dealer.user_id,
                    "title": "Rental Return Expected",
                    "message": f"Rental for {machine.model} ({machine.equipment_id}) expires tomorrow. Prepare for inventory intake.",
                    "equipment_id": machine.equipment_id,
                    "priority": "HIGH",
                    "notification_type": "LOGISTICS"
                })
                
            # 3. Notify Fleet Manager
            if rental.site_id:
                fleet_managers = db.query(FleetManager).filter(FleetManager.site_id == rental.site_id).all()
                for fm in fleet_managers:
                    await rabbitmq.publish_message({
                        "user_id": fm.user_id,
                        "title": "Machine Return Deadline",
                        "message": f"Machine {machine.equipment_id} at your site is scheduled for return tomorrow.",
                        "equipment_id": machine.equipment_id,
                        "priority": "HIGH",
                        "notification_type": "ALERT"
                    })
    except Exception as e:
        print(f"Error in check_rental_expiring_tomorrow: {e}")
    finally:
        db.close()

async def check_over_utilization():
    """Job that checks for machine over-utilization and notifies stakeholders."""
    print("Running scheduled job: check_over_utilization")
    db: Session = SessionLocal()
    try:
        # Get active rentals
        active_rentals = db.query(Rental).filter(Rental.rental_status == "ACTIVE").all()
        
        for rental in active_rentals:
            machine = rental.machine
            
            # Check latest utilization score for this machine
            latest_pred = db.query(UtilizationPrediction)\
                .filter(UtilizationPrediction.equipment_id == machine.equipment_id)\
                .order_by(UtilizationPrediction.prediction_timestamp.desc())\
                .first()
                
            if latest_pred and latest_pred.utilization_score and float(latest_pred.utilization_score) >= 0.90:
                print(f"Machine {machine.equipment_id} is over-utilized (Score: {latest_pred.utilization_score}). Sending alerts.")
                
                # 1. Notify Customer
                if rental.customer:
                    await rabbitmq.publish_message({
                        "user_id": rental.customer.user_id,
                        "title": "Machine Over-Utilization Alert",
                        "message": f"Your rented machine {machine.equipment_id} ({machine.model}) has reached {float(latest_pred.utilization_score)*100:.1f}% utilization. Please monitor usage to avoid penalties.",
                        "equipment_id": machine.equipment_id,
                        "priority": "HIGH",
                        "notification_type": "ALERT"
                    })
                    
                # 2. Notify Dealer
                if machine.dealer:
                    await rabbitmq.publish_message({
                        "user_id": machine.dealer.user_id,
                        "title": "Machine Over-Utilization Alert",
                        "message": f"Machine {machine.equipment_id} ({machine.model}) is operating at {float(latest_pred.utilization_score)*100:.1f}% utilization.",
                        "equipment_id": machine.equipment_id,
                        "priority": "MEDIUM",
                        "notification_type": "ALERT"
                    })
                    
                # 3. Notify Fleet Manager
                if rental.site_id:
                    fleet_managers = db.query(FleetManager).filter(FleetManager.site_id == rental.site_id).all()
                    for fm in fleet_managers:
                        await rabbitmq.publish_message({
                            "user_id": fm.user_id,
                            "title": "High Utilization Warning",
                            "message": f"Machine {machine.equipment_id} at your site is over-utilized ({float(latest_pred.utilization_score)*100:.1f}%). Consider transferring additional equipment.",
                            "equipment_id": machine.equipment_id,
                            "priority": "HIGH",
                            "notification_type": "ALERT"
                        })
    except Exception as e:
        print(f"Error in check_over_utilization: {e}")
    finally:
        db.close()

def start_scheduler():
    # Run overdue check every day at midnight
    scheduler.add_job(check_overdue_rentals, 'cron', hour=0, minute=0)
    # Run maintenance check at 1 AM
    scheduler.add_job(check_maintenance_due, 'cron', hour=1, minute=0)
    # Run 1-day rental expiration warning at 8 AM
    scheduler.add_job(check_rental_expiring_tomorrow, 'cron', hour=8, minute=0)
    
    # Run over-utilization check every 2 hours
    scheduler.add_job(check_over_utilization, 'interval', hours=2)
    
    # For testing/hackathon purposes, we can also add an interval job
    # scheduler.add_job(check_overdue_rentals, 'interval', minutes=5)
    
    scheduler.start()
    print("APScheduler started.")
