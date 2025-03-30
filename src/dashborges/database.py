from sqlalchemy import create_engine, Column, Integer, String, Float, Date, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Create database directory if it doesn't exist
os.makedirs("/home/borges/development/dashborges/data", exist_ok=True)

# Create engine
DATABASE_URL = "sqlite:////home/borges/development/dashborges/data/finances.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

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
Base.metadata.create_all(bind=engine)


# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
