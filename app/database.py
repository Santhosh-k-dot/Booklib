from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Database URL from .env file
DATABASE_URL = "postgresql://postgres:root@localhost/library_db"

# Create engine
engine = create_engine(
    DATABASE_URL,
    pool_size=20,        # increase base pool
    max_overflow=30,     # extra temporary connections
    pool_timeout=30,     # wait time
)

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()