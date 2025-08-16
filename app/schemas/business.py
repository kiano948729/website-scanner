"""
Pydantic schemas for business data validation and serialization.
"""

from typing import Optional
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field


class BusinessBase(BaseModel):
    """Base business schema."""
    name: str = Field(..., min_length=1, max_length=255, description="Business name")
    address: Optional[str] = Field(None, description="Business address")
    city: Optional[str] = Field(None, max_length=100, description="City")
    country: Optional[str] = Field(None, max_length=50, description="Country")
    postal_code: Optional[str] = Field(None, max_length=20, description="Postal code")
    phone: Optional[str] = Field(None, max_length=50, description="Phone number")
    email: Optional[str] = Field(None, max_length=255, description="Email address")
    business_type: Optional[str] = Field(None, max_length=100, description="Type of business")
    industry: Optional[str] = Field(None, max_length=100, description="Industry")
    employee_count: Optional[str] = Field(None, max_length=50, description="Number of employees")
    is_zzp: bool = Field(True, description="Is this a self-employed business")
    website_exists: bool = Field(False, description="Does the business have a website")
    website_url: Optional[str] = Field(None, max_length=500, description="Website URL")
    website_confidence_score: Optional[Decimal] = Field(None, ge=0, le=1, description="Website confidence score")
    source: Optional[str] = Field(None, max_length=100, description="Data source")
    source_id: Optional[str] = Field(None, max_length=255, description="Source ID")
    confidence_score: Optional[Decimal] = Field(None, ge=0, le=1, description="Overall confidence score")
    is_processed: bool = Field(False, description="Has the data been processed")
    is_verified: bool = Field(False, description="Has the data been verified")


class BusinessCreate(BusinessBase):
    """Schema for creating a new business."""
    pass


class BusinessUpdate(BaseModel):
    """Schema for updating a business."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    address: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=50)
    postal_code: Optional[str] = Field(None, max_length=20)
    phone: Optional[str] = Field(None, max_length=50)
    email: Optional[str] = Field(None, max_length=255)
    business_type: Optional[str] = Field(None, max_length=100)
    industry: Optional[str] = Field(None, max_length=100)
    employee_count: Optional[str] = Field(None, max_length=50)
    is_zzp: Optional[bool] = None
    website_exists: Optional[bool] = None
    website_url: Optional[str] = Field(None, max_length=500)
    website_confidence_score: Optional[Decimal] = Field(None, ge=0, le=1)
    source: Optional[str] = Field(None, max_length=100)
    source_id: Optional[str] = Field(None, max_length=255)
    confidence_score: Optional[Decimal] = Field(None, ge=0, le=1)
    is_processed: Optional[bool] = None
    is_verified: Optional[bool] = None


class BusinessResponse(BusinessBase):
    """Schema for business response."""
    id: int
    uuid: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_checked: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(v) if v is not None else None,
            datetime: lambda v: v.isoformat() if v else None,
        }


class BusinessStats(BaseModel):
    """Schema for business statistics."""
    total_businesses: int
    businesses_with_website: int
    businesses_without_website: int
    zzp_businesses: int
    zzp_without_website: int
    by_country: dict[str, int]
    by_source: dict[str, int]


class BusinessSearch(BaseModel):
    """Schema for business search parameters."""
    query: str = Field(..., min_length=1, description="Search query")
    skip: int = Field(0, ge=0, description="Number of records to skip")
    limit: int = Field(100, ge=1, le=1000, description="Number of records to return") 