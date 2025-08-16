"""
CrawlJob model for tracking crawling tasks.
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Enum, Index
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum

from app.database.connection import Base


class JobStatus(enum.Enum):
    """Job status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class JobType(enum.Enum):
    """Job type enumeration."""
    GOOGLE_MAPS = "google_maps"
    LINKEDIN = "linkedin"
    FACEBOOK = "facebook"
    CHAMBER_OF_COMMERCE = "chamber_of_commerce"
    WEBSITE_CHECK = "website_check"
    DATA_ENRICHMENT = "data_enrichment"


class CrawlJob(Base):
    """CrawlJob model for tracking crawling tasks."""
    
    __tablename__ = "crawl_jobs"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, index=True)
    
    # Job information
    name = Column(String(255), nullable=False)
    job_type = Column(Enum(JobType), nullable=False)
    status = Column(Enum(JobStatus), default=JobStatus.PENDING, index=True)
    
    # Job parameters
    parameters = Column(Text)  # JSON string of job parameters
    target_location = Column(String(255))  # e.g., "Amsterdam, Netherlands"
    target_industry = Column(String(100))
    
    # Progress tracking
    total_items = Column(Integer, default=0)
    processed_items = Column(Integer, default=0)
    successful_items = Column(Integer, default=0)
    failed_items = Column(Integer, default=0)
    
    # Error handling
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    
    # Celery task tracking
    celery_task_id = Column(String(255))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_crawl_jobs_status', 'status'),
        Index('idx_crawl_jobs_type', 'job_type'),
        Index('idx_crawl_jobs_created', 'created_at'),
        Index('idx_crawl_jobs_celery', 'celery_task_id'),
    )
    
    def __repr__(self):
        return f"<CrawlJob(id={self.id}, name='{self.name}', status='{self.status.value}')>"
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'uuid': str(self.uuid),
            'name': self.name,
            'job_type': self.job_type.value if self.job_type else None,
            'status': self.status.value if self.status else None,
            'parameters': self.parameters,
            'target_location': self.target_location,
            'target_industry': self.target_industry,
            'total_items': self.total_items,
            'processed_items': self.processed_items,
            'successful_items': self.successful_items,
            'failed_items': self.failed_items,
            'error_message': self.error_message,
            'retry_count': self.retry_count,
            'max_retries': self.max_retries,
            'celery_task_id': self.celery_task_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
        }
    
    @property
    def progress_percentage(self):
        """Calculate progress percentage."""
        if self.total_items == 0:
            return 0
        return (self.processed_items / self.total_items) * 100
    
    @property
    def is_completed(self):
        """Check if job is completed."""
        return self.status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]
    
    @property
    def can_retry(self):
        """Check if job can be retried."""
        return self.status == JobStatus.FAILED and self.retry_count < self.max_retries 