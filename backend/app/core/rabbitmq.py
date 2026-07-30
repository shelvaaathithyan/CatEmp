import aio_pika
import json
import os
from typing import Any, Dict

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost/")
QUEUE_NAME = "notifications_queue"

class RabbitMQManager:
    def __init__(self):
        self.connection = None
        self.channel = None

    async def connect(self):
        try:
            self.connection = await aio_pika.connect_robust(RABBITMQ_URL)
            self.channel = await self.connection.channel()
            # Ensure the queue exists
            await self.channel.declare_queue(QUEUE_NAME, durable=True)
            print("Connected to RabbitMQ.")
        except Exception as e:
            print(f"Failed to connect to RabbitMQ: {e}")

    async def close(self):
        if self.connection:
            await self.connection.close()

    async def publish_message(self, message: Dict[str, Any]):
        if not self.channel:
            print("RabbitMQ channel not initialized.")
            return

        try:
            await self.channel.default_exchange.publish(
                aio_pika.Message(
                    body=json.dumps(message).encode(),
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT
                ),
                routing_key=QUEUE_NAME,
            )
        except Exception as e:
            print(f"Failed to publish message: {e}")

rabbitmq = RabbitMQManager()
