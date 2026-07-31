from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class ActionableInsight(BaseModel):
    id: str
    type: str # "EXPIRING_RENTAL", "MAINTENANCE", "ANOMALY"
    equipment_id: str
    message: str
    customer_user_id: Optional[int] = None
    customer_name: Optional[str] = None
    action_label: Optional[str] = None
    target_user_id: Optional[int] = None

class MachineWidgetSummary(BaseModel):
    equipment_id: str
    equipment_type: str
    model: str
    rental_id: Optional[int] = None

class WidgetData(BaseModel):
    count: int
    machines: List[MachineWidgetSummary]

class FleetStatusChartData(BaseModel):
    name: str
    value: int
    fill: str

class RevenueChartData(BaseModel):
    month: str
    revenue: float

class DealerDashboardResponse(BaseModel):
    total_machines: int
    available_machines: WidgetData
    rented_machines: WidgetData
    maintenance_machines: WidgetData
    underutilized_machines: WidgetData
    upcoming_returns: WidgetData
    active_customers: int
    revenue_this_month: float
    actionable_insights: List[ActionableInsight] = []
    fleet_status_chart: List[FleetStatusChartData] = []
    revenue_trend_chart: List[RevenueChartData] = []

class CustomerDashboardResponse(BaseModel):
    active_rentals: int
    total_machines_rented: WidgetData
    active_sites: int
    total_operators: int
    upcoming_returns: WidgetData
    total_rental_cost_this_month: float
    actionable_insights: List[ActionableInsight] = []
    machines_by_site_chart: List[FleetStatusChartData] = []
    rental_costs_trend: List[Dict[str, Any]] = []

class FleetManagerDashboardResponse(BaseModel):
    assigned_site_id: int
    assigned_site_name: str
    active_machines: WidgetData
    today_checkins: int
    today_checkouts: int
    pending_transfers: int
    maintenance_alerts: int
    actionable_insights: List[ActionableInsight] = []
