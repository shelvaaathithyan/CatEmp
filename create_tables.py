import logging
from app.core.database import engine, Base
import app.models  # Ensures all models are loaded before creating tables

# Set up logging to show SQLAlchemy operations
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
# Enable SQLAlchemy query logging so we can see the tables being created
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

def init_db():
    logging.info("Starting database initialization...")
    try:
        # This will create all tables that don't exist yet
        Base.metadata.create_all(bind=engine)
        logging.info("Successfully created all tables!")
    except Exception as e:
        logging.error(f"Error creating tables: {e}")
        logging.error("Make sure your .env has the EXTERNAL Database URL and your IP is whitelisted on Render.")

if __name__ == "__main__":
    init_db()
