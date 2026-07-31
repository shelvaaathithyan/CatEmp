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
from app.models.predictions import UtilizationPrediction, MaintenancePrediction, AnomalyPrediction, DemandPrediction
from app.models.site_transfer import SiteTransfer

def _build_widget(machines):
    return {
        "count": len(machines),
        "machines": [{"equipment_id": m.equipment_id, "equipment_type": m.equipment_type, "model": m.model} for m in machines]
    }

def _build_rental_widget(machine_rental_tuples):
    return {
        "count": len(machine_rental_tuples),
        "machines": [{"equipment_id": m.equipment_id, "equipment_type": m.equipment_type, "model": m.model, "rental_id": r.id, "expected_return_date": r.expected_return_date.isoformat() if r.expected_return_date else None} for m, r in machine_rental_tuples]
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

    # Calculate dealer revenue trend (last 6 months)
    dealer_rentals = db.query(Rental).join(Machine, Rental.equipment_id == Machine.equipment_id).filter(
        Machine.dealer_id == dealer.id,
        Rental.check_in_date != None
    ).all()

    months_list = []
    current_date = today
    for i in range(6):
        months_list.append(current_date.replace(day=1))
        first_of_month = current_date.replace(day=1)
        current_date = first_of_month - timedelta(days=1)
    months_list.reverse()
    
    monthly_revenue = {m.strftime("%b"): 0.0 for m in months_list}
    start_date = months_list[0]
    
    revenue_this_month = 0.0

    for r in dealer_rentals:
        if r.rental_cost and r.check_in_date:
            if r.check_in_date >= start_date:
                month_str = r.check_in_date.strftime("%b")
                if month_str in monthly_revenue:
                    monthly_revenue[month_str] += float(r.rental_cost)
            if r.check_in_date.year == today.year and r.check_in_date.month == today.month:
                revenue_this_month += float(r.rental_cost)
                
    revenue_trend_chart = [{"month": k, "revenue": v} for k, v in monthly_revenue.items()]

    return {
        "total_machines": total_machines,
        "available_machines": _build_widget(available),
        "rented_machines": _build_widget(rented),
        "maintenance_machines": _build_widget(maintenance),
        "underutilized_machines": _build_widget(underutilized),
        "upcoming_returns": _build_widget(upcoming),
        "active_customers": active_customers,
        "revenue_this_month": revenue_this_month,
        "actionable_insights": actionable_insights,
        "fleet_status_chart": [
            {"name": "Rented", "value": len(rented), "fill": "#f1c40f"}, # Cat Yellow
            {"name": "Available", "value": len(available), "fill": "#bdc3c7"},
            {"name": "Maintenance", "value": len(maintenance), "fill": "#e74c3c"}
        ],
        "revenue_trend_chart": revenue_trend_chart
    }

def get_customer_kpis(db: Session, customer_user_id: int):
    customer = db.query(Customer).filter(Customer.user_id == customer_user_id).first()
    if not customer:
        return None
        
    active_rentals_count = db.query(func.count(Rental.id)).filter(Rental.customer_id == customer.id, Rental.rental_status == 'ACTIVE').scalar() or 0
    
    machines_rented = db.query(Machine, Rental).join(Rental, Rental.equipment_id == Machine.equipment_id)\
        .filter(Rental.customer_id == customer.id, Rental.rental_status == 'ACTIVE').all()
        
    active_sites = db.query(func.count(func.distinct(Rental.site_id))).filter(Rental.customer_id == customer.id, Rental.rental_status == 'ACTIVE').scalar() or 0
    total_operators = db.query(func.count(Operator.operator_id)).filter(Operator.customer_id == customer.id).scalar() or 0
    
    today = datetime.now(timezone.utc).date()
    next_week = today + timedelta(days=7)
    upcoming = db.query(Machine, Rental).join(Rental, Rental.equipment_id == Machine.equipment_id)\
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

    # Build site distribution chart
    site_distribution = {}
    active_site_rentals = db.query(Rental, Site).join(Site, Site.id == Rental.site_id).filter(Rental.customer_id == customer.id, Rental.rental_status == 'ACTIVE').all()
    for r, s in active_site_rentals:
        site_distribution[s.site_name] = site_distribution.get(s.site_name, 0) + 1
        
    colors = ["#f1c40f", "#e67e22", "#e74c3c", "#3498db", "#9b59b6", "#2ecc71"]
    fleet_status_chart = []
    for i, (site_name, count) in enumerate(site_distribution.items()):
        fleet_status_chart.append({
            "name": site_name,
            "value": count,
            "fill": colors[i % len(colors)]
        })

    # Calculate rental costs trend (last 6 months)
    historical_rentals = db.query(Rental).filter(
        Rental.customer_id == customer.id,
        Rental.check_in_date != None
    ).all()

    months_list = []
    current_date = today
    for i in range(6):
        months_list.append(current_date.replace(day=1))
        first_of_month = current_date.replace(day=1)
        current_date = first_of_month - timedelta(days=1)
    months_list.reverse()
    
    monthly_costs = {m.strftime("%b"): 0.0 for m in months_list}
    start_date = months_list[0]
    
    total_rental_cost_this_month = 0.0

    for r in historical_rentals:
        if r.rental_cost and r.check_in_date:
            if r.check_in_date >= start_date:
                month_str = r.check_in_date.strftime("%b")
                if month_str in monthly_costs:
                    monthly_costs[month_str] += float(r.rental_cost)
            if r.check_in_date.year == today.year and r.check_in_date.month == today.month:
                total_rental_cost_this_month += float(r.rental_cost)

    rental_costs_trend = [{"month": k, "cost": v} for k, v in monthly_costs.items()]

    return {
        "active_rentals": active_rentals_count,
        "total_machines_rented": _build_rental_widget(machines_rented),
        "active_sites": active_sites,
        "total_operators": total_operators,
        "upcoming_returns": _build_rental_widget(upcoming),
        "total_rental_cost_this_month": total_rental_cost_this_month,
        "actionable_insights": actionable_insights,
        "machines_by_site_chart": fleet_status_chart,
        "rental_costs_trend": rental_costs_trend
    }

def get_fleet_manager_kpis(db: Session, fm_user_id: int):
    fm = db.query(FleetManager).filter(FleetManager.user_id == fm_user_id).first()
    if not fm:
        return None
        
    site = db.query(Site).filter(Site.id == fm.site_id).first()
    
    active_machines_raw = db.query(Machine, Rental).join(Rental, Rental.equipment_id == Machine.equipment_id)\
        .filter(Rental.site_id == site.id, Rental.rental_status == 'ACTIVE').all()
    
    # We need to build the rental widget so they can be clicked
    active_machines = active_machines_raw
    
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

    # 3. Pending Maintenance (Dealer initiated)
    maint_preds = db.query(MaintenancePrediction, Rental)\
        .join(Rental, Rental.equipment_id == MaintenancePrediction.equipment_id)\
        .filter(Rental.site_id == site.id, Rental.rental_status == 'ACTIVE', MaintenancePrediction.predicted_service_date <= today + timedelta(days=5))\
        .order_by(MaintenancePrediction.prediction_timestamp.desc()).all()
        
    maintenance_alerts = 0
    seen_maint = set()
    for mp, r in maint_preds:
        if mp.equipment_id not in seen_maint:
            seen_maint.add(mp.equipment_id)
            maintenance_alerts += 1
            actionable_insights.append({
                "id": f"FM_MAINT_{mp.equipment_id}_{mp.id}",
                "type": "MAINTENANCE",
                "equipment_id": mp.equipment_id,
                "message": f"Maintenance scheduled by dealer for {mp.predicted_service_date}. Plan downtime.",
                "action_label": "Acknowledge"
            })
            
    # Calculate Pending Transfers
    pending_transfers = db.query(func.count(SiteTransfer.id)).filter(SiteTransfer.to_site_id == site.id, SiteTransfer.transfer_date >= today).scalar() or 0

    # Calculate 7-Day Usage Trend
    usage_trend_chart = []
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        daily_usage = db.query(func.sum(EquipmentUsage.engine_hours_per_day))\
            .filter(EquipmentUsage.site_id == site.id, EquipmentUsage.usage_date == d).scalar() or 0
        usage_trend_chart.append({"date": d.strftime("%b %d"), "hours": float(daily_usage)})

    # Calculate Machine Status Chart based on Utilization Prediction or hardcode a fallback
    status_counts = {"Running": 0, "Idle": 0, "Maintenance": 0}
    for m, r in active_machines_raw:
        if m.status == 'MAINTENANCE' or m.equipment_id in seen_maint:
            status_counts["Maintenance"] += 1
        elif m.equipment_id in seen_idle:
            status_counts["Idle"] += 1
        else:
            status_counts["Running"] += 1
            
    machine_status_chart = [
        {"name": "Running", "value": status_counts["Running"], "fill": "#2ecc71"},
        {"name": "Idle", "value": status_counts["Idle"], "fill": "#f1c40f"},
        {"name": "Maintenance", "value": status_counts["Maintenance"], "fill": "#e74c3c"}
    ]
    
    # Top Priority Predictions
    demand_preds = db.query(DemandPrediction)\
        .filter(DemandPrediction.site_id == site.id)\
        .order_by(DemandPrediction.prediction_timestamp.desc()).limit(3).all()
        
    prediction_insights = []
    for dp in demand_preds:
        prediction_insights.append({
            "type": "DEMAND",
            "equipment_type": dp.equipment_type,
            "expected_demand": dp.expected_demand,
            "period": dp.prediction_period
        })

    return {
        "assigned_site_id": site.id,
        "assigned_site_name": site.site_name,
        "active_machines": _build_rental_widget(active_machines),
        "today_checkins": today_checkins,
        "today_checkouts": today_checkouts,
        "pending_transfers": pending_transfers,
        "maintenance_alerts": maintenance_alerts,
        "actionable_insights": actionable_insights,
        "machine_status_chart": machine_status_chart,
        "usage_trend_chart": usage_trend_chart,
        "prediction_insights": prediction_insights
    }
