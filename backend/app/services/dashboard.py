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
from app.models.equipment_usage import EquipmentUsage
from app.models.predictions import UtilizationPrediction, MaintenancePrediction, AnomalyPrediction

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
    
    underutilized_subquery = db.query(UtilizationPrediction.equipment_id).filter(UtilizationPrediction.status == 'UNDERUTILIZED').distinct().subquery()
    underutilized = db.query(Machine).filter(Machine.dealer_id == dealer.id, Machine.equipment_id.in_(underutilized_subquery)).all()
    
    today = datetime.now(timezone.utc).date()
    next_week = today + timedelta(days=7)
    
    upcoming = db.query(Machine).join(Rental, Rental.equipment_id == Machine.equipment_id)\
        .filter(Machine.dealer_id == dealer.id, Rental.rental_status == 'ACTIVE', Rental.expected_return_date.between(today, next_week)).all()
        
    active_customers = db.query(func.count(func.distinct(Rental.customer_id)))\
        .join(Machine, Rental.equipment_id == Machine.equipment_id)\
        .filter(Machine.dealer_id == dealer.id, Rental.rental_status == 'ACTIVE').scalar() or 0

    actionable_insights = []

    # 1. Expiring Rentals
    for m, r, c in db.query(Machine, Rental, Customer)\
        .join(Rental, Rental.equipment_id == Machine.equipment_id)\
        .join(Customer, Customer.id == Rental.customer_id)\
        .filter(Machine.dealer_id == dealer.id, Rental.rental_status == 'ACTIVE', Rental.expected_return_date.between(today, today + timedelta(days=5))).all():
        actionable_insights.append({
            "id": f"EXP_{m.equipment_id}_{r.id}",
            "type": "EXPIRING_RENTAL",
            "equipment_id": m.equipment_id,
            "message": f"Rental for {m.model} expires on {r.expected_return_date}.",
            "customer_user_id": c.user_id,
            "customer_name": f"Customer {c.user_id}",
            "action_label": None
        })

    # 2. Maintenance Due
    # Use outer join for rentals so we see maintenance for ALL dealer machines, rented or not.
    maintenance_preds = db.query(MaintenancePrediction, Machine, Rental, Customer)\
        .join(Machine, Machine.equipment_id == MaintenancePrediction.equipment_id)\
        .outerjoin(Rental, (Rental.equipment_id == Machine.equipment_id) & (Rental.rental_status == 'ACTIVE'))\
        .outerjoin(Customer, Customer.id == Rental.customer_id)\
        .filter(Machine.dealer_id == dealer.id)\
        .filter((MaintenancePrediction.maintenance_probability > 0.8) | (MaintenancePrediction.predicted_service_date.between(today, today + timedelta(days=5))))\
        .order_by(MaintenancePrediction.prediction_timestamp.desc()).all()
    
    seen_maint = set()
    for mp, m, r, c in maintenance_preds:
        if mp.equipment_id not in seen_maint:
            seen_maint.add(mp.equipment_id)
            
            # Format message based on whether it's probability-based or date-based
            if mp.predicted_service_date and mp.predicted_service_date <= today + timedelta(days=5):
                msg = f"Routine service predicted by {mp.predicted_service_date}."
            else:
                msg = f"High maintenance probability ({float(mp.maintenance_probability)*100:.0f}%)."
                
            # Determine Action
            action_label = "Schedule Internal Service"
            if c and r:
                # If the machine is rented, notify customer ONLY IF the rental overlaps the service date
                # (or if it's an immediate probability alert)
                if not mp.predicted_service_date or (mp.predicted_service_date and r.expected_return_date >= mp.predicted_service_date):
                    action_label = f"Notify {c.company_name}"

            actionable_insights.append({
                "id": f"MAINT_{mp.equipment_id}_{mp.id}",
                "type": "MAINTENANCE",
                "equipment_id": mp.equipment_id,
                "message": msg,
                "customer_user_id": c.user_id if c else None,
                "customer_name": c.company_name if c else None,
                "action_label": action_label
            })

    # 3. Anomalies
    anomaly_preds = db.query(AnomalyPrediction, Machine, Rental, Customer)\
        .join(Machine, Machine.equipment_id == AnomalyPrediction.equipment_id)\
        .outerjoin(Rental, (Rental.equipment_id == Machine.equipment_id) & (Rental.rental_status == 'ACTIVE'))\
        .outerjoin(Customer, Customer.id == Rental.customer_id)\
        .filter(Machine.dealer_id == dealer.id, AnomalyPrediction.anomaly_score > 0.8)\
        .order_by(AnomalyPrediction.prediction_timestamp.desc()).all()
    
    seen_anom = set()
    for ap, m, r, c in anomaly_preds:
        if ap.equipment_id not in seen_anom:
            seen_anom.add(ap.equipment_id)
            actionable_insights.append({
                "id": f"ANOM_{ap.equipment_id}_{ap.id}",
                "type": "ANOMALY",
                "equipment_id": ap.equipment_id,
                "message": f"Anomaly detected (Score: {float(ap.anomaly_score):.2f}). Something is off.",
                "customer_user_id": c.user_id if c else None,
                "customer_name": c.company_name if c else None,
                "action_label": f"Notify {c.company_name}" if c else "Inspect Machine"
            })

    return {
        "total_machines": total_machines,
        "available_machines": _build_widget(available),
        "rented_machines": _build_widget(rented),
        "maintenance_machines": _build_widget(maintenance),
        "underutilized_machines": _build_widget(underutilized),
        "upcoming_returns": _build_widget(upcoming),
        "active_customers": active_customers,
        "revenue_this_month": 45000.00,
        "actionable_insights": actionable_insights
    }

def get_customer_kpis(db: Session, customer_user_id: int):
    customer = db.query(Customer).filter(Customer.user_id == customer_user_id).first()
    if not customer:
        return None
        
    active_rentals_count = db.query(func.count(Rental.id)).filter(Rental.customer_id == customer.id, Rental.rental_status == 'ACTIVE').scalar() or 0
    
    machines_rented = db.query(Machine).join(Rental, Rental.equipment_id == Machine.equipment_id)\
        .filter(Rental.customer_id == customer.id, Rental.rental_status == 'ACTIVE').all()
        
    active_sites = db.query(func.count(func.distinct(Rental.site_id))).filter(Rental.customer_id == customer.id, Rental.rental_status == 'ACTIVE').scalar() or 0
    total_operators = db.query(func.count(Operator.operator_id)).filter(Operator.customer_id == customer.id).scalar() or 0
    
    today = datetime.now(timezone.utc).date()
    next_week = today + timedelta(days=7)
    upcoming = db.query(Machine).join(Rental, Rental.equipment_id == Machine.equipment_id)\
        .filter(Rental.customer_id == customer.id, Rental.rental_status == 'ACTIVE', Rental.expected_return_date.between(today, next_week)).all()

    actionable_insights = []
    
    # 1. Over-utilization Warning
    active_rentals = db.query(Rental).filter(Rental.customer_id == customer.id, Rental.rental_status == 'ACTIVE').all()
    for r in active_rentals:
        usage = db.query(EquipmentUsage).filter(EquipmentUsage.rental_id == r.id).order_by(EquipmentUsage.usage_date.desc()).first()
        if usage and usage.engine_hours_per_day and usage.engine_hours_per_day > 9.6:
            site = db.query(Site).filter(Site.id == r.site_id).first()
            fm = db.query(FleetManager).filter(FleetManager.site_id == r.site_id).first()
            fm_user_id = fm.user_id if fm else None
            actionable_insights.append({
                "id": f"UTIL_{r.equipment_id}_{usage.id}",
                "type": "OVERUTILIZATION",
                "equipment_id": r.equipment_id,
                "message": f"Machine at '{site.site_name}' has exceeded its recommended daily operating hours ({float(usage.engine_hours_per_day)} hrs). This may incur dealer penalty fees.",
                "customer_user_id": customer.user_id,
                "target_user_id": fm_user_id,
                "action_label": "Alert Site Manager" if fm_user_id else None
            })

    # 2. Idle Equipment
    idle_preds = db.query(UtilizationPrediction, Rental, Site, FleetManager)\
        .join(Rental, Rental.equipment_id == UtilizationPrediction.equipment_id)\
        .join(Site, Site.id == Rental.site_id)\
        .outerjoin(FleetManager, FleetManager.site_id == Site.id)\
        .filter(Rental.customer_id == customer.id, Rental.rental_status == 'ACTIVE', UtilizationPrediction.status == 'Idle')\
        .order_by(UtilizationPrediction.prediction_timestamp.desc()).all()
    
    seen_idle = set()
    for ip, r, site, fm in idle_preds:
        if ip.equipment_id not in seen_idle:
            seen_idle.add(ip.equipment_id)
            fm_user_id = fm.user_id if fm else None
            actionable_insights.append({
                "id": f"IDLE_{ip.equipment_id}_{ip.id}",
                "type": "IDLE_EQUIPMENT",
                "equipment_id": ip.equipment_id,
                "message": f"You are paying rent on a machine at '{site.site_name}' that is flagged as idle.",
                "customer_user_id": customer.user_id,
                "target_user_id": fm_user_id,
                "action_label": "Alert Site Manager" if fm_user_id else "Initiate Return"
            })

    # 3. Pending Dealer Actions (Maintenance)
    maint_preds = db.query(MaintenancePrediction, Rental, Site, FleetManager)\
        .join(Rental, Rental.equipment_id == MaintenancePrediction.equipment_id)\
        .join(Site, Site.id == Rental.site_id)\
        .outerjoin(FleetManager, FleetManager.site_id == Site.id)\
        .filter(Rental.customer_id == customer.id, Rental.rental_status == 'ACTIVE', MaintenancePrediction.predicted_service_date <= today + timedelta(days=5))\
        .order_by(MaintenancePrediction.prediction_timestamp.desc()).all()

    seen_maint = set()
    for mp, r, site, fm in maint_preds:
        if mp.equipment_id not in seen_maint:
            seen_maint.add(mp.equipment_id)
            fm_user_id = fm.user_id if fm else None
            actionable_insights.append({
                "id": f"CMAINT_{mp.equipment_id}_{mp.id}",
                "type": "MAINTENANCE",
                "equipment_id": mp.equipment_id,
                "message": f"Your dealer has scheduled mandatory maintenance for {mp.predicted_service_date}.",
                "customer_user_id": customer.user_id,
                "target_user_id": fm_user_id,
                "action_label": "Acknowledge (Alert Operators)" if fm_user_id else None
            })

    return {
        "active_rentals": active_rentals_count,
        "total_machines_rented": _build_widget(machines_rented),
        "active_sites": active_sites,
        "total_operators": total_operators,
        "upcoming_returns": _build_widget(upcoming),
        "total_rental_cost_this_month": 12500.00,
        "actionable_insights": actionable_insights
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
        .filter(Rental.site_id == site.id, CheckinCheckout.action.in_(['CHECKIN', 'CHECK-IN', 'CHECK_IN']), CheckinCheckout.timestamp >= day_start).scalar() or 0
        
    today_checkouts = db.query(func.count(CheckinCheckout.id)).join(Rental)\
        .filter(Rental.site_id == site.id, CheckinCheckout.action.in_(['CHECKOUT', 'CHECK-OUT', 'CHECK_OUT']), CheckinCheckout.timestamp >= day_start).scalar() or 0

    actionable_insights = []
    
    active_rentals = db.query(Rental).filter(Rental.site_id == site.id, Rental.rental_status == 'ACTIVE').all()
    
    # 1. Over-utilization Warning
    for r in active_rentals:
        usage = db.query(EquipmentUsage).filter(EquipmentUsage.rental_id == r.id).order_by(EquipmentUsage.usage_date.desc()).first()
        if usage and usage.engine_hours_per_day and usage.engine_hours_per_day > 9.6:
            actionable_insights.append({
                "id": f"FM_UTIL_{r.equipment_id}_{usage.id}",
                "type": "OVERUTILIZATION",
                "equipment_id": r.equipment_id,
                "message": f"Machine {r.equipment_id} has exceeded its recommended daily operating hours ({float(usage.engine_hours_per_day)} hrs). Prevent penalty fees.",
                "action_label": "Stop Machine"
            })

    # 2. Idle Equipment (Under-utilization)
    idle_preds = db.query(UtilizationPrediction, Rental)\
        .join(Rental, Rental.equipment_id == UtilizationPrediction.equipment_id)\
        .filter(Rental.site_id == site.id, Rental.rental_status == 'ACTIVE', UtilizationPrediction.status.in_(['Idle', 'UNDERUTILIZED']))\
        .order_by(UtilizationPrediction.prediction_timestamp.desc()).all()
    
    seen_idle = set()
    for ip, r in idle_preds:
        if ip.equipment_id not in seen_idle:
            seen_idle.add(ip.equipment_id)
            actionable_insights.append({
                "id": f"FM_IDLE_{ip.equipment_id}_{ip.id}",
                "type": "IDLE_EQUIPMENT",
                "equipment_id": ip.equipment_id,
                "message": f"Machine {ip.equipment_id} is sitting idle and burning budget. Consider reallocation.",
                "action_label": "Schedule Site Transfer"
            })

    return {
        "assigned_site_id": site.id,
        "assigned_site_name": site.site_name,
        "active_machines": _build_widget(active_machines),
        "today_checkins": today_checkins,
        "today_checkouts": today_checkouts,
        "pending_transfers": 0,
        "maintenance_alerts": 0,
        "actionable_insights": actionable_insights
    }
