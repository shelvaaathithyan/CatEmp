from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.notification import NotificationResponse, NotificationSendRequest
from app.repositories.notification import notification_repo
from app.core.rabbitmq import rabbitmq

router = APIRouter()

@router.get("/", response_model=List[NotificationResponse])
def get_notifications(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve historical notifications for the logged-in user."""
    return notification_repo.get_user_notifications(db, current_user.id, skip=skip, limit=limit)

@router.put("/{notification_id}/read", response_model=NotificationResponse)
def mark_notification_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark a specific notification as read."""
    notif = notification_repo.mark_as_read(db, notification_id, current_user.id)
    if not notif:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    return notif

@router.post("/send")
async def send_manual_notification(
    request: NotificationSendRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Sends a manual notification to another user."""
    payload = {
        "user_id": request.recipient_id,
        "title": f"From {current_user.name}: {request.title}",
        "message": request.message,
        "priority": request.priority,
        "notification_type": request.notification_type
    }
    await rabbitmq.publish_message(payload)
    return {"status": "success", "message": "Notification sent to queue"}
