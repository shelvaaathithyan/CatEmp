from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta, timezone

from app.models.machine import Machine
from app.models.rental import Rental
from app.models.customer import Customer
from app.models.dealer import Dealer
from app.models.fleet_manager import FleetManager
from app.models.site import Site
from app.models.operator import Operator
from app.models.checkin_checkout import CheckinCheckout
from app.models.predictions import UtilizationPrediction

def _build_widget(machines):
    return {
        "count": len(machines),
        "machines": [{"equipment_id": m.equipment_id, "equipment_type": m.equipment_type, "model": m.model} for m in machines]
    }

def get_dealer_kpis(db: Session, dealer_user_id: int):
    dealer = db.query(Dealer).filter(Dealer.user_id == dealer_user_id).first()
    if not dealer:
        return None
    
    total_machines = db.query(func.count(Machine.equipment_id)).filter(Machine.dealer_id == dealer.id).scalar() or 0
    
    available = db.query(Machine).filter(Machine.dealer_id == dealer.id, Machine.status == 'AVAILABLE').all()
    rented = db.query(Machine).filter(Machine.dealer_id == dealer.id, Machine.status == 'RENTED').all()
    maintenance = db.query(Machine).filter(Machine.dealer_id == dealer.id, Machine.status == 'MAINTENANCE').all()
    
    underutilized = db.query(Machine).join(UtilizationPrediction, UtilizationPrediction.equipment_id == Machine.equipment_id)\
        .filter(Machine.dealer_id == dealer.id, UtilizationPrediction.status == 'UNDERUTILIZED').all()
    
    today = datetime.now(timezone.utc).date()
    next_week = today + timedelta(days=7)
    
    upcoming = db.query(Machine).join(Rental, Rental.equipment_id == Machine.equipment_id)\
        .filter(Machine.dealer_id == dealer.id, Rental.rental_status == 'ACTIVE', Rental.expected_return_date.between(today, next_week)).all()
        
    active_customers = db.query(func.count(func.distinct(Rental.customer_id)))\
        .join(Machine, Rental.equipment_id == Machine.equipment_id)\
        .filter(Machine.dealer_id == dealer.id, Rental.rental_status == 'ACTIVE').scalar() or 0

    return {
        "total_machines": total_machines,
        "available_machines": _build_widget(available),
        "rented_machines": _build_widget(rented),
        "maintenance_machines": _build_widget(maintenance),
        "underutilized_machines": _build_widget(underutilized),
        "upcoming_returns": _build_widget(upcoming),
        "active_customers": active_customers,
        "revenue_this_month": 45000.00
    }

def get_customer_kpis(db: Session, customer_user_id: int):
    customer = db.query(Customer).filter(Customer.user_id == customer_user_id).first()
    if not customer:
        return None
        
    active_rentals = db.query(func.count(Rental.id)).filter(Rental.customer_id == customer.id, Rental.rental_status == 'ACTIVE').scalar() or 0
    
    machines_rented = db.query(Machine).join(Rental, Rental.equipment_id == Machine.equipment_id)\
        .filter(Rental.customer_id == customer.id, Rental.rental_status == 'ACTIVE').all()
        
    active_sites = db.query(func.count(func.distinct(Rental.site_id))).filter(Rental.customer_id == customer.id, Rental.rental_status == 'ACTIVE').scalar() or 0
    total_operators = db.query(func.count(Operator.operator_id)).filter(Operator.customer_id == customer.id).scalar() or 0
    
    today = datetime.now(timezone.utc).date()
    next_week = today + timedelta(days=7)
    upcoming = db.query(Machine).join(Rental, Rental.equipment_id == Machine.equipment_id)\
        .filter(Rental.customer_id == customer.id, Rental.rental_status == 'ACTIVE', Rental.expected_return_date.between(today, next_week)).all()

    return {
        "active_rentals": active_rentals,
        "total_machines_rented": _build_widget(machines_rented),
        "active_sites": active_sites,
        "total_operators": total_operators,
        "upcoming_returns": _build_widget(upcoming),
        "total_rental_cost_this_month": 12500.00
    }

def get_fleet_manager_kpis(db: Session, fm_user_id: int):
    fm = db.query(FleetManager).filter(FleetManager.user_id == fm_user_id).first()
    if not fm:
        return None
        
    site = db.query(Site).filter(Site.id == fm.site_id).first()
    
    active_machines = db.query(Machine).join(Rental, Rental.equipment_id == Machine.equipment_id)\
        .filter(Rental.site_id == site.id, Rental.rental_status == 'ACTIVE').all()
    
    today = datetime.now(timezone.utc).date()
    day_start = datetime.combine(today, datetime.min.time())
    
    today_checkins = db.query(func.count(CheckinCheckout.id)).join(Rental)\
        .filter(Rental.site_id == site.id, CheckinCheckout.action == 'CHECKIN', CheckinCheckout.timestamp >= day_start).scalar() or 0
        
    today_checkouts = db.query(func.count(CheckinCheckout.id)).join(Rental)\
        .filter(Rental.site_id == site.id, CheckinCheckout.action == 'CHECKOUT', CheckinCheckout.timestamp >= day_start).scalar() or 0

    return {
        "assigned_site_id": site.id,
        "assigned_site_name": site.site_name,
        "active_machines": _build_widget(active_machines),
        "today_checkins": today_checkins,
        "today_checkouts": today_checkouts,
        "pending_transfers": 0,
        "maintenance_alerts": 0
    }
