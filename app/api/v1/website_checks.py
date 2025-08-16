"""
Website checks API endpoints.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.website_check import WebsiteCheck
import structlog

logger = structlog.get_logger(__name__)

router = APIRouter()


@router.get("/", response_model=List[dict])
async def get_website_checks(
    skip: int = 0,
    limit: int = 100,
    business_id: int = None,
    check_type: str = None,
    db: Session = Depends(get_db)
):
    """Get list of website checks."""
    query = db.query(WebsiteCheck)
    
    if business_id:
        query = query.filter(WebsiteCheck.business_id == business_id)
    if check_type:
        query = query.filter(WebsiteCheck.check_type == check_type)
    
    checks = query.offset(skip).limit(limit).all()
    
    logger.info(f"Retrieved {len(checks)} website checks")
    return [check.to_dict() for check in checks]


@router.get("/{check_id}", response_model=dict)
async def get_website_check(check_id: int, db: Session = Depends(get_db)):
    """Get a specific website check by ID."""
    check = db.query(WebsiteCheck).filter(WebsiteCheck.id == check_id).first()
    if not check:
        raise HTTPException(status_code=404, detail="Website check not found")
    
    logger.info(f"Retrieved website check {check_id}")
    return check.to_dict()


@router.get("/business/{business_id}", response_model=List[dict])
async def get_business_website_checks(
    business_id: int,
    db: Session = Depends(get_db)
):
    """Get all website checks for a specific business."""
    checks = db.query(WebsiteCheck).filter(WebsiteCheck.business_id == business_id).all()
    
    logger.info(f"Retrieved {len(checks)} website checks for business {business_id}")
    return [check.to_dict() for check in checks] 