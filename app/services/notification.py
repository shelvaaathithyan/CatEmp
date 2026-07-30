from sqlalchemy.orm import Session
from app.models.notification import Notification
from app.schemas.notification import NotificationCreate

class NotificationService:
    @staticmethod
    def create_notification(db: Session, notification_in: NotificationCreate) -> Notification:
        """Creates a new notification for a specific user."""
        db_obj = Notification(
            user_id=notification_in.user_id,
            equipment_id=notification_in.equipment_id,
            notification_type=notification_in.notification_type,
            title=notification_in.title,
            message=notification_in.message,
            priority=notification_in.priority
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    @staticmethod
    def mark_as_read(db: Session, notification_id: int) -> Notification:
        """Marks a specific notification as read."""
        notification = db.query(Notification).filter(Notification.id == notification_id).first()
        if notification:
            notification.is_read = True
            db.commit()
            db.refresh(notification)
        return notification

notification_service = NotificationService()
