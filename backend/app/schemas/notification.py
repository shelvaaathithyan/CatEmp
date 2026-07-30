from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class NotificationBase(BaseModel):
    user_id: int
    equipment_id: Optional[str] = None
    notification_type: Optional[str] = None
    title: str
    message: Optional[str] = None
    priority: Optional[str] = None

class NotificationCreate(NotificationBase):
    pass

class NotificationResponse(NotificationBase):
    id: int
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True

class NotificationSendRequest(BaseModel):
    recipient_id: int
    title: str
    message: str
    priority: Optional[str] = "INFO"
    notification_type: Optional[str] = "MANUAL"
