import asyncio
from scheduler import TelemetryScheduler
from logger import logger

async def main():
    logger.info("Starting Telemetry Simulator Service...")
    
    scheduler = TelemetryScheduler()
    scheduler.start()
    
    try:
        # Keep the main thread alive to allow the scheduler to run in the background
        while True:
            await asyncio.sleep(3600)
    except (KeyboardInterrupt, SystemExit):
        logger.info("Shutting down Telemetry Simulator Service...")

if __name__ == "__main__":
    asyncio.run(main())
