import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load env vars
load_dotenv()

# Database URL configuration (defaults to SQLite)
# Note: SQLite connection string on Windows uses 3 slashes for relative path, or 4 for absolute path.
# For SQLite, we must set connect_args={"check_same_thread": False}
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./sentivision.db")

# Create engine
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL, connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(DATABASE_URL)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for ORM models
Base = declarative_base()

def get_db():
    """
    FastAPI dependency to yield a database session.
    Closes the session after the request is completed.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
