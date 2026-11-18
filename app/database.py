import os

from dotenv import load_dotenv
from sqlalchemy import URL, create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# Load environment variables
load_dotenv()

# Read database credentials
DATABASE_URL = URL.create(
    drivername="postgresql+psycopg",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST", "localhost"),
    port=int(os.getenv("DB_PORT", "5432")),
    database=os.getenv("DB_NAME", "digital_banking"),
)

# Create database engine
engine = create_engine(DATABASE_URL, echo=False)

# Create database session factory
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


# Base class for database models
class Base(DeclarativeBase):
    pass
