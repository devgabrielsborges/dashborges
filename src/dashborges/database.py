from sqlalchemy import create_engine, Column, Integer, String, Float, Date, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get database directory from environment variable or use default
DATA_DIR = os.environ.get("DASHBORGES_DATA_DIR", "/app/data")
CONFIG_DIR = os.environ.get("DASHBORGES_CONFIG_DIR", "/app/config")
LOGS_DIR = os.environ.get("DASHBORGES_LOGS_DIR", "/app/logs")

# Create directories if they don't exist
for directory in [DATA_DIR, CONFIG_DIR, LOGS_DIR]:
    os.makedirs(directory, exist_ok=True)
    logger.info(f"Ensured directory exists: {directory}")

# Create engine with better configuration for container environments
DATABASE_URL = f"sqlite:///{os.path.join(DATA_DIR, 'finances.db')}"
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False, "timeout": 20},
    pool_pre_ping=True,
    echo=False,
)

# Log the database location
logger.info(f"Using database at: {os.path.join(DATA_DIR, 'finances.db')}")

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()


# Define the Transaction model
class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, index=True)
    category = Column(String, nullable=False)
    description = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    type = Column(String, nullable=False)  # 'income' or 'expense'

    def to_dict(self):
        return {
            "id": self.id,
            "date": str(self.date),
            "category": self.category,
            "description": self.description,
            "amount": self.amount,
            "type": self.type,
        }


# Create all tables
try:
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")
except Exception as e:
    logger.error(f"Error creating database tables: {e}")


# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Function to backup database
def backup_database():
    """Create a backup of the database file."""
    import shutil
    from datetime import datetime

    try:
        backup_filename = (
            f"finances_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        )
        backup_path = os.path.join(DATA_DIR, backup_filename)
        shutil.copy2(os.path.join(DATA_DIR, "finances.db"), backup_path)
        logger.info(f"Database backup created: {backup_path}")
        return backup_path
    except Exception as e:
        logger.error(f"Error creating database backup: {e}")
        return None
