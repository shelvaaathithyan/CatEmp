from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.routers import api_router
from app.core.database import engine, Base
# Import all models so Base.metadata.create_all can see them
import asyncio
from contextlib import asynccontextmanager

from app.core.rabbitmq import rabbitmq
from app.workers.notification_worker import start_consumer
from app.core.scheduler import start_scheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Connect to RabbitMQ, start consumer, start scheduler
    await rabbitmq.connect()
    asyncio.create_task(start_consumer())
    start_scheduler()
    yield
    # Shutdown: Close connections
    await rabbitmq.close()

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    description="Backend for the Caterpillar Smart Rental Tracking System",
    lifespan=lifespan
)

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {"message": "Welcome to the Smart Rental Tracking System API. Visit /docs for Swagger UI."}
