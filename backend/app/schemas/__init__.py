from .user import UserBase, UserCreate, UserResponse
from .dealer import DealerBase, DealerCreate, DealerResponse
from .customer import CustomerBase, CustomerCreate, CustomerResponse
from .site import SiteBase, SiteCreate, SiteResponse
from .fleet_manager import FleetManagerBase, FleetManagerCreate, FleetManagerResponse
from .machine import MachineBase, MachineCreate, MachineResponse
from .rental import RentalBase, RentalCreate, RentalUpdate, RentalResponse
from .operator import OperatorBase, OperatorCreate, OperatorResponse
from .site_transfer import SiteTransferBase, SiteTransferCreate, SiteTransferResponse
from .checkin_checkout import CheckinCheckoutBase, CheckinCheckoutCreate, CheckinCheckoutResponse
from .equipment_usage import EquipmentUsageBase, EquipmentUsageCreate, EquipmentUsageResponse
from .maintenance import MaintenanceHistoryBase, MaintenanceHistoryCreate, MaintenanceHistoryResponse
from .predictions import (
    MaintenancePredictionBase, MaintenancePredictionCreate, MaintenancePredictionResponse,
    UtilizationPredictionBase, UtilizationPredictionCreate, UtilizationPredictionResponse,
    DemandPredictionBase, DemandPredictionCreate, DemandPredictionResponse
)
from .notification import NotificationBase, NotificationCreate, NotificationResponse
