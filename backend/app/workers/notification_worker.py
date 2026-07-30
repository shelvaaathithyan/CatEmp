import json
import asyncio
from app.core.rabbitmq import rabbitmq, QUEUE_NAME
from app.core.websocket_manager import ws_manager
from app.core.database import SessionLocal
from app.models.notification import Notification

async def process_notification(message: dict):
    """Saves to DB and broadcasts via WebSockets."""
    db = SessionLocal()
    try:
        user_id = message.get("user_id")
        title = message.get("title")
        body = message.get("message")
        equipment_id = message.get("equipment_id")
        priority = message.get("priority", "INFO")
        notification_type = message.get("notification_type", "SYSTEM")

        if not user_id or not title:
            return

        # 1. Save to DB
        new_notif = Notification(
            user_id=user_id,
            title=title,
            message=body,
            equipment_id=equipment_id,
            priority=priority,
            notification_type=notification_type
        )
        db.add(new_notif)
        db.commit()
        db.refresh(new_notif)

        # 2. Push to WebSocket
        payload = {
            "id": new_notif.id,
            "title": new_notif.title,
            "message": new_notif.message,
            "priority": new_notif.priority,
            "type": new_notif.notification_type,
            "equipment_id": new_notif.equipment_id,
            "created_at": new_notif.created_at.isoformat() if new_notif.created_at else None
        }
        await ws_manager.send_personal_message(payload, user_id)
    except Exception as e:
        print(f"Error processing notification: {e}")
        db.rollback()
    finally:
        db.close()

async def start_consumer():
    """Background task that consumes messages from RabbitMQ."""
    if not rabbitmq.connection:
        await rabbitmq.connect()
        
    if not rabbitmq.channel:
        return
        
    queue = await rabbitmq.channel.declare_queue(QUEUE_NAME, durable=True)
    print("Started RabbitMQ consumer worker...")

    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process():
                try:
                    payload = json.loads(message.body.decode())
                    await process_notification(payload)
                except Exception as e:
                    print(f"Consumer error: {e}")
