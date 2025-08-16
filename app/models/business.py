"""
Business model for storing business information.
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Numeric, Index
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.database.connection import Base


class Business(Base):
    """Business model for storing business information."""
    
    __tablename__ = "businesses"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, index=True)
    
    # Business information
    name = Column(String(255), nullable=False, index=True)
    address = Column(Text)
    city = Column(String(100), index=True)
    country = Column(String(50), index=True)
    postal_code = Column(String(20))
    phone = Column(String(50))
    email = Column(String(255))
    
    # Business classification
    business_type = Column(String(100))
    industry = Column(String(100))
    employee_count = Column(String(50))  # e.g., "1-10", "11-50", etc.
    is_zzp = Column(Boolean, default=True)
    
    # Website information
    website_exists = Column(Boolean, default=False, index=True)
    website_url = Column(String(500))
    website_confidence_score = Column(Numeric(3, 2))  # 0.00 to 1.00
    
    # Source and metadata
    source = Column(String(100))  # e.g., "google_maps", "linkedin", "facebook"
    source_id = Column(String(255))  # ID from the source
    raw_data = Column(Text)  # JSON string of raw data from source
    
    # Quality and processing
    confidence_score = Column(Numeric(3, 2), default=0.0)  # Overall confidence
    is_processed = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_checked = Column(DateTime(timezone=True))
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_businesses_location', 'city', 'country'),
        Index('idx_businesses_website', 'website_exists'),
        Index('idx_businesses_confidence', 'confidence_score'),
        Index('idx_businesses_source', 'source'),
        Index('idx_businesses_processed', 'is_processed'),
        Index('idx_businesses_zzp', 'is_zzp'),
    )
    
    def __repr__(self):
        return f"<Business(id={self.id}, name='{self.name}', city='{self.city}')>"
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'uuid': str(self.uuid),
            'name': self.name,
            'address': self.address,
            'city': self.city,
            'country': self.country,
            'postal_code': self.postal_code,
            'phone': self.phone,
            'email': self.email,
            'business_type': self.business_type,
            'industry': self.industry,
            'employee_count': self.employee_count,
            'is_zzp': self.is_zzp,
            'website_exists': self.website_exists,
            'website_url': self.website_url,
            'website_confidence_score': float(self.website_confidence_score) if self.website_confidence_score else None,
            'source': self.source,
            'source_id': self.source_id,
            'confidence_score': float(self.confidence_score) if self.confidence_score else None,
            'is_processed': self.is_processed,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_checked': self.last_checked.isoformat() if self.last_checked else None,
        } 