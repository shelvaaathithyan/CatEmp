from app.repositories.base import BaseRepository
from app.models.site_transfer import SiteTransfer
from app.models.checkin_checkout import CheckinCheckout
from app.models.equipment_usage import EquipmentUsage
from app.schemas.site_transfer import SiteTransferCreate, SiteTransferBase
from app.schemas.checkin_checkout import CheckinCheckoutCreate, CheckinCheckoutBase
from app.schemas.equipment_usage import EquipmentUsageCreate, EquipmentUsageBase

site_transfer_repo = BaseRepository[SiteTransfer, SiteTransferCreate, SiteTransferBase](SiteTransfer)
checkin_checkout_repo = BaseRepository[CheckinCheckout, CheckinCheckoutCreate, CheckinCheckoutBase](CheckinCheckout)
equipment_usage_repo = BaseRepository[EquipmentUsage, EquipmentUsageCreate, EquipmentUsageBase](EquipmentUsage)
