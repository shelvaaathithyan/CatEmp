from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import asyncio
from datetime import datetime
import json
from logger import logger
from telemetry_generator import TelemetryGenerator
from api_client import PredictionAPIClient
import config

class TelemetryScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.generator = TelemetryGenerator()
        self.api_client = PredictionAPIClient()

    async def execute_cycle(self):
        logger.info("=" * 48)
        logger.info("Scheduler Started")
        logger.info(f"Timestamp: {datetime.now().isoformat()}")
        logger.info("=" * 48)

        # 1. Generate synthetic telemetry
        records = self.generator.generate_telemetry()
        
        for record in records:
            logger.info("Telemetry Generated")
            logger.info(json.dumps(record, indent=2))
            
            # 2. Create payloads for each ML model
            demand_payload = self.generator.build_demand_payload(record)
            maintenance_payload = self.generator.build_maintenance_payload(record)
            utilization_payload = self.generator.build_utilization_payload(record)
            
            # 3. Call the FastAPI APIs and 4. Log responses
            await self.api_client.send_telemetry(
                demand_payload, 
                maintenance_payload, 
                utilization_payload
            )
            
        logger.info("=" * 48)
        logger.info("Cycle Completed Successfully")
        logger.info("=" * 48)

    def start(self):
        # Run automatically every 5 minutes using cron expression '*/5 * * * *'
        self.scheduler.add_job(
            self.execute_cycle, 
            CronTrigger.from_crontab('*/5 * * * *')
        )
        self.scheduler.start()
        
        logger.info(f"Telemetry Scheduler initialized. Running every 5 minutes.")
        
        # Optionally, run a cycle immediately
        asyncio.create_task(self.execute_cycle())
