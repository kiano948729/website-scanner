"""
WebsiteCheck model for tracking website verification results.
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Numeric, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.database.connection import Base


class WebsiteCheck(Base):
    """WebsiteCheck model for tracking website verification results."""
    
    __tablename__ = "website_checks"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, index=True)
    
    # Foreign key to business
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False, index=True)
    business = relationship("Business", backref="website_checks")
    
    # Check information
    check_type = Column(String(50))  # e.g., "dns", "google_search", "whois", "http"
    url_checked = Column(String(500))
    
    # Results
    website_exists = Column(Boolean, default=False)
    confidence_score = Column(Numeric(3, 2))  # 0.00 to 1.00
    status_code = Column(Integer)  # HTTP status code
    response_time = Column(Numeric(5, 3))  # Response time in seconds
    
    # Technical details
    dns_records = Column(Text)  # JSON string of DNS records
    whois_data = Column(Text)  # JSON string of WHOIS data
    ssl_info = Column(Text)  # JSON string of SSL certificate info
    headers = Column(Text)  # JSON string of HTTP headers
    
    # Error information
    error_message = Column(Text)
    is_error = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    checked_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_website_checks_business', 'business_id'),
        Index('idx_website_checks_type', 'check_type'),
        Index('idx_website_checks_exists', 'website_exists'),
        Index('idx_website_checks_confidence', 'confidence_score'),
        Index('idx_website_checks_created', 'created_at'),
    )
    
    def __repr__(self):
        return f"<WebsiteCheck(id={self.id}, business_id={self.business_id}, type='{self.check_type}')>"
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'uuid': str(self.uuid),
            'business_id': self.business_id,
            'check_type': self.check_type,
            'url_checked': self.url_checked,
            'website_exists': self.website_exists,
            'confidence_score': float(self.confidence_score) if self.confidence_score else None,
            'status_code': self.status_code,
            'response_time': float(self.response_time) if self.response_time else None,
            'dns_records': self.dns_records,
            'whois_data': self.whois_data,
            'ssl_info': self.ssl_info,
            'headers': self.headers,
            'error_message': self.error_message,
            'is_error': self.is_error,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'checked_at': self.checked_at.isoformat() if self.checked_at else None,
        } 