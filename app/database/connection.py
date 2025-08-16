"""
Database connection and session management.
"""

from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import structlog

from app.config.settings import get_database_url

logger = structlog.get_logger(__name__)

# Create SQLAlchemy engine
engine = create_engine(
    get_database_url(),
    poolclass=StaticPool,
    pool_pre_ping=True,
    echo=False,  # Set to True for SQL query logging
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

# Metadata for migrations
metadata = MetaData()


def get_db() -> Session:
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def init_db():
    """Initialize database tables."""
    try:
        # Import all models to ensure they are registered
        from app.models.business import Business
        from app.models.crawl_job import CrawlJob
        from app.models.website_check import WebsiteCheck
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


def get_db_session() -> Session:
    """Get a database session for use outside of FastAPI dependency injection."""
    return SessionLocal() 