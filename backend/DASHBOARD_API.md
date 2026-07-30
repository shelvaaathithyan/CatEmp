# Dashboard Analytics API Documentation

This document outlines the API endpoints designed to power the three main role-based dashboards in the Smart Rental Tracking System. 

These endpoints are highly optimized; they perform SQL aggregations on the backend to return exactly the Key Performance Indicators (KPIs) needed for the frontend summary cards instantly, without the frontend having to download thousands of raw rows.

---

## General Information
- **Base URL**: `/api/v1/dashboards`
- **Authentication**: All endpoints require a valid JWT Access Token passed in the `Authorization` header (`Bearer <token>`).
- **Role-Based Access**: Each endpoint strictly enforces role checks. A Customer cannot access the Dealer dashboard endpoint, and vice versa.

---

## 1. Dealer Dashboard API

**Endpoint**: `GET /api/v1/dashboards/dealer`  
**Allowed Roles**: `CatAdmin`, `Dealer`

**Description**: 
Retrieves fleet-wide aggregations for the dealer. It calculates how many machines they own, how many are rented vs available, and how many are under maintenance or underutilized.

**Expected Response**:
```json
{
  "total_machines": 150,
  "available_machines": {
    "count": 1,
    "machines": [
      {
        "equipment_id": "EX-002",
        "equipment_type": "Excavator",
        "model": "336"
      }
    ]
  },
  "rented_machines": {
    "count": 2,
    "machines": [
      {
        "equipment_id": "EX-001",
        "equipment_type": "Excavator",
        "model": "320 GC"
      }
    ]
  },
  "maintenance_machines": {
    "count": 1,
    "machines": []
  },
  "underutilized_machines": {
    "count": 0,
    "machines": []
  },
  "upcoming_returns": {
    "count": 0,
    "machines": []
  },
  "active_customers": 34,
  "revenue_this_month": 45000.00
}
```

---

## 2. Customer Dashboard API

**Endpoint**: `GET /api/v1/dashboards/customer`  
**Allowed Roles**: `CatAdmin`, `Customer`

**Description**: 
Retrieves project-level aggregations for a customer. It summarizes their active rental contracts, how many distinct sites they are operating on, and the number of operators they manage.

**Expected Response**:
```json
{
  "active_rentals": 12,
  "total_machines_rented": {
    "count": 2,
    "machines": [
      {
        "equipment_id": "EX-001",
        "equipment_type": "Excavator",
        "model": "320 GC"
      }
    ]
  },
  "active_sites": 3,
  "total_operators": 45,
  "upcoming_returns": {
    "count": 1,
    "machines": []
  },
  "total_rental_cost_this_month": 12500.00
}
```

---

## 3. Fleet Manager Dashboard API

**Endpoint**: `GET /api/v1/dashboards/fleet-manager`  
**Allowed Roles**: `CatAdmin`, `Fleet Manager`

**Description**: 
Retrieves site-specific metrics for the Fleet Manager. It is tightly scoped to the specific `Site` the Fleet Manager is assigned to, showing daily operations like how many check-ins occurred today.

**Expected Response**:
```json
{
  "assigned_site_id": 1,
  "assigned_site_name": "Downtown Skyscraper Project",
  "active_machines": {
    "count": 1,
    "machines": [
      {
        "equipment_id": "EX-001",
        "equipment_type": "Excavator",
        "model": "320 GC"
      }
    ]
  },
  "today_checkins": 2,
  "today_checkouts": 3,
  "pending_transfers": 1,
  "maintenance_alerts": 0
}
```

---

## 💡 Frontend Implementation Note
To build the complete dashboards as requested:
1. Call the relevant summary endpoint above to paint the top KPI cards instantly.
2. Make concurrent requests to the filtered list endpoints (e.g., `GET /api/v1/machines?status=RENTED` or `GET /api/v1/rentals?rental_status=ACTIVE`) to populate the heavy data tables below the cards.
