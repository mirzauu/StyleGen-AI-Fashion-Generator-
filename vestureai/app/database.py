from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

# Create engine with connection pooling and best practices
engine = create_engine(
    os.getenv("DATABASE_URL"),
    pool_size=10,  # Initial number of connections in the pool
    max_overflow=10,  # Maximum number of connections beyond pool_size
    pool_timeout=30,  # Timeout in seconds for getting a connection from the pool
    pool_recycle=1800,  # Recycle connections every 30 minutes (to avoid stale connections)
    pool_pre_ping=True,  # Check the connection is alive before using it
    echo=False,  # Set to True for SQL query logging, False in production
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all ORM models
Base = declarative_base()
