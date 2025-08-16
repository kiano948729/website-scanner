"""
Business API endpoints for CRUD operations.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.database.connection import get_db
from app.models.business import Business
from app.schemas.business import BusinessCreate, BusinessUpdate, BusinessResponse
import structlog

logger = structlog.get_logger(__name__)

router = APIRouter()


@router.get("/", response_model=List[BusinessResponse])
async def get_businesses(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    city: Optional[str] = Query(None, description="Filter by city"),
    country: Optional[str] = Query(None, description="Filter by country"),
    website_exists: Optional[bool] = Query(None, description="Filter by website existence"),
    is_zzp: Optional[bool] = Query(None, description="Filter by ZZP status"),
    source: Optional[str] = Query(None, description="Filter by data source"),
    db: Session = Depends(get_db)
):
    """Get list of businesses with optional filtering."""
    query = db.query(Business)
    
    # Apply filters
    if city:
        query = query.filter(Business.city.ilike(f"%{city}%"))
    if country:
        query = query.filter(Business.country.ilike(f"%{country}%"))
    if website_exists is not None:
        query = query.filter(Business.website_exists == website_exists)
    if is_zzp is not None:
        query = query.filter(Business.is_zzp == is_zzp)
    if source:
        query = query.filter(Business.source == source)
    
    # Apply pagination
    businesses = query.offset(skip).limit(limit).all()
    
    logger.info(f"Retrieved {len(businesses)} businesses", 
                skip=skip, limit=limit, filters={"city": city, "country": country, 
                                                "website_exists": website_exists, "is_zzp": is_zzp, "source": source})
    
    return [BusinessResponse.from_orm(business) for business in businesses]


@router.get("/{business_id}", response_model=BusinessResponse)
async def get_business(business_id: int, db: Session = Depends(get_db)):
    """Get a specific business by ID."""
    business = db.query(Business).filter(Business.id == business_id).first()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    logger.info(f"Retrieved business {business_id}")
    return BusinessResponse.from_orm(business)


@router.post("/", response_model=BusinessResponse)
async def create_business(business: BusinessCreate, db: Session = Depends(get_db)):
    """Create a new business."""
    db_business = Business(**business.dict())
    db.add(db_business)
    db.commit()
    db.refresh(db_business)
    
    logger.info(f"Created business {db_business.id}")
    return BusinessResponse.from_orm(db_business)


@router.put("/{business_id}", response_model=BusinessResponse)
async def update_business(
    business_id: int, 
    business_update: BusinessUpdate, 
    db: Session = Depends(get_db)
):
    """Update a business."""
    db_business = db.query(Business).filter(Business.id == business_id).first()
    if not db_business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    # Update only provided fields
    update_data = business_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_business, field, value)
    
    db.commit()
    db.refresh(db_business)
    
    logger.info(f"Updated business {business_id}")
    return BusinessResponse.from_orm(db_business)


@router.delete("/{business_id}")
async def delete_business(business_id: int, db: Session = Depends(get_db)):
    """Delete a business."""
    db_business = db.query(Business).filter(Business.id == business_id).first()
    if not db_business:
        raise HTTPException(status_code=404, detail="Business not found")
    
    db.delete(db_business)
    db.commit()
    
    logger.info(f"Deleted business {business_id}")
    return {"message": "Business deleted successfully"}


@router.get("/stats/summary")
async def get_business_stats(db: Session = Depends(get_db)):
    """Get business statistics summary."""
    total_businesses = db.query(Business).count()
    businesses_with_website = db.query(Business).filter(Business.website_exists == True).count()
    zzp_businesses = db.query(Business).filter(Business.is_zzp == True).count()
    zzp_without_website = db.query(Business).filter(
        and_(Business.is_zzp == True, Business.website_exists == False)
    ).count()
    
    # Count by country
    country_stats = db.query(Business.country, db.func.count(Business.id)).group_by(Business.country).all()
    
    # Count by source
    source_stats = db.query(Business.source, db.func.count(Business.id)).group_by(Business.source).all()
    
    stats = {
        "total_businesses": total_businesses,
        "businesses_with_website": businesses_with_website,
        "businesses_without_website": total_businesses - businesses_with_website,
        "zzp_businesses": zzp_businesses,
        "zzp_without_website": zzp_without_website,
        "by_country": dict(country_stats),
        "by_source": dict(source_stats),
    }
    
    logger.info("Retrieved business statistics", stats=stats)
    return stats


@router.get("/search/", response_model=List[BusinessResponse])
async def search_businesses(
    q: str = Query(..., description="Search query"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """Search businesses by name, city, or industry."""
    query = db.query(Business).filter(
        or_(
            Business.name.ilike(f"%{q}%"),
            Business.city.ilike(f"%{q}%"),
            Business.industry.ilike(f"%{q}%"),
            Business.business_type.ilike(f"%{q}%")
        )
    )
    
    businesses = query.offset(skip).limit(limit).all()
    
    logger.info(f"Search for '{q}' returned {len(businesses)} results")
    return [BusinessResponse.from_orm(business) for business in businesses] 