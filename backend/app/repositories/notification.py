from typing import List, Optional
from sqlalchemy.orm import Session
from app.repositories.base import BaseRepository
from app.models.notification import Notification
from app.schemas.notification import NotificationCreate, NotificationBase

class NotificationRepository(BaseRepository[Notification, NotificationCreate, NotificationBase]):
    def get_user_notifications(self, db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Notification]:
        """Fetch historical notifications for a specific user."""
        return db.query(self.model)\
                 .filter(self.model.user_id == user_id)\
                 .order_by(self.model.created_at.desc())\
                 .offset(skip).limit(limit).all()
                 
    def mark_as_read(self, db: Session, notification_id: int, user_id: int) -> Optional[Notification]:
        """Marks a specific notification as read."""
        notif = db.query(self.model).filter(self.model.id == notification_id, self.model.user_id == user_id).first()
        if notif:
            notif.is_read = True
            db.commit()
            db.refresh(notif)
        return notif

notification_repo = NotificationRepository(Notification)
