"""
Exports API endpoints for data export functionality.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import and_
import pandas as pd
import os
from datetime import datetime

from app.database.connection import get_db
from app.models.business import Business
from app.config.settings import get_settings
import structlog

logger = structlog.get_logger(__name__)

router = APIRouter()


@router.post("/businesses/csv")
async def export_businesses_csv(
    city: Optional[str] = Query(None, description="Filter by city"),
    country: Optional[str] = Query(None, description="Filter by country"),
    website_exists: Optional[bool] = Query(None, description="Filter by website existence"),
    is_zzp: Optional[bool] = Query(None, description="Filter by ZZP status"),
    source: Optional[str] = Query(None, description="Filter by data source"),
    db: Session = Depends(get_db)
):
    """Export businesses to CSV file."""
    settings = get_settings()
    
    # Build query
    query = db.query(Business)
    
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
    
    # Get businesses
    businesses = query.all()
    
    if len(businesses) > settings.MAX_EXPORT_SIZE:
        raise HTTPException(
            status_code=400, 
            detail=f"Export too large. Maximum {settings.MAX_EXPORT_SIZE} records allowed."
        )
    
    # Convert to DataFrame
    data = []
    for business in businesses:
        data.append({
            'id': business.id,
            'name': business.name,
            'address': business.address,
            'city': business.city,
            'country': business.country,
            'postal_code': business.postal_code,
            'phone': business.phone,
            'email': business.email,
            'business_type': business.business_type,
            'industry': business.industry,
            'employee_count': business.employee_count,
            'is_zzp': business.is_zzp,
            'website_exists': business.website_exists,
            'website_url': business.website_url,
            'website_confidence_score': float(business.website_confidence_score) if business.website_confidence_score else None,
            'source': business.source,
            'confidence_score': float(business.confidence_score) if business.confidence_score else None,
            'created_at': business.created_at.isoformat() if business.created_at else None,
            'updated_at': business.updated_at.isoformat() if business.updated_at else None,
        })
    
    df = pd.DataFrame(data)
    
    # Create export directory if it doesn't exist
    os.makedirs(settings.EXPORT_DIR, exist_ok=True)
    
    # Generate filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"businesses_export_{timestamp}.csv"
    filepath = os.path.join(settings.EXPORT_DIR, filename)
    
    # Export to CSV
    df.to_csv(filepath, index=False, encoding='utf-8')
    
    logger.info(f"Exported {len(businesses)} businesses to {filename}")
    
    return FileResponse(
        path=filepath,
        filename=filename,
        media_type='text/csv'
    )


@router.post("/businesses/excel")
async def export_businesses_excel(
    city: Optional[str] = Query(None, description="Filter by city"),
    country: Optional[str] = Query(None, description="Filter by country"),
    website_exists: Optional[bool] = Query(None, description="Filter by website existence"),
    is_zzp: Optional[bool] = Query(None, description="Filter by ZZP status"),
    source: Optional[str] = Query(None, description="Filter by data source"),
    db: Session = Depends(get_db)
):
    """Export businesses to Excel file."""
    settings = get_settings()
    
    # Build query
    query = db.query(Business)
    
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
    
    # Get businesses
    businesses = query.all()
    
    if len(businesses) > settings.MAX_EXPORT_SIZE:
        raise HTTPException(
            status_code=400, 
            detail=f"Export too large. Maximum {settings.MAX_EXPORT_SIZE} records allowed."
        )
    
    # Convert to DataFrame
    data = []
    for business in businesses:
        data.append({
            'id': business.id,
            'name': business.name,
            'address': business.address,
            'city': business.city,
            'country': business.country,
            'postal_code': business.postal_code,
            'phone': business.phone,
            'email': business.email,
            'business_type': business.business_type,
            'industry': business.industry,
            'employee_count': business.employee_count,
            'is_zzp': business.is_zzp,
            'website_exists': business.website_exists,
            'website_url': business.website_url,
            'website_confidence_score': float(business.website_confidence_score) if business.website_confidence_score else None,
            'source': business.source,
            'confidence_score': float(business.confidence_score) if business.confidence_score else None,
            'created_at': business.created_at.isoformat() if business.created_at else None,
            'updated_at': business.updated_at.isoformat() if business.updated_at else None,
        })
    
    df = pd.DataFrame(data)
    
    # Create export directory if it doesn't exist
    os.makedirs(settings.EXPORT_DIR, exist_ok=True)
    
    # Generate filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"businesses_export_{timestamp}.xlsx"
    filepath = os.path.join(settings.EXPORT_DIR, filename)
    
    # Export to Excel
    with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Businesses', index=False)
        
        # Add summary sheet
        summary_data = {
            'Metric': [
                'Total Businesses',
                'Businesses with Website',
                'Businesses without Website',
                'ZZP Businesses',
                'ZZP without Website',
            ],
            'Count': [
                len(businesses),
                len([b for b in businesses if b.website_exists]),
                len([b for b in businesses if not b.website_exists]),
                len([b for b in businesses if b.is_zzp]),
                len([b for b in businesses if b.is_zzp and not b.website_exists]),
            ]
        }
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
    
    logger.info(f"Exported {len(businesses)} businesses to {filename}")
    
    return FileResponse(
        path=filepath,
        filename=filename,
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )


@router.get("/zzp-without-website")
async def export_zzp_without_website(
    city: Optional[str] = Query(None, description="Filter by city"),
    country: Optional[str] = Query(None, description="Filter by country"),
    db: Session = Depends(get_db)
):
    """Export ZZP businesses without websites."""
    settings = get_settings()
    
    # Build query for ZZP without website
    query = db.query(Business).filter(
        and_(Business.is_zzp == True, Business.website_exists == False)
    )
    
    if city:
        query = query.filter(Business.city.ilike(f"%{city}%"))
    if country:
        query = query.filter(Business.country.ilike(f"%{country}%"))
    
    # Get businesses
    businesses = query.all()
    
    if len(businesses) > settings.MAX_EXPORT_SIZE:
        raise HTTPException(
            status_code=400, 
            detail=f"Export too large. Maximum {settings.MAX_EXPORT_SIZE} records allowed."
        )
    
    # Convert to DataFrame
    data = []
    for business in businesses:
        data.append({
            'id': business.id,
            'name': business.name,
            'address': business.address,
            'city': business.city,
            'country': business.country,
            'postal_code': business.postal_code,
            'phone': business.phone,
            'email': business.email,
            'business_type': business.business_type,
            'industry': business.industry,
            'employee_count': business.employee_count,
            'source': business.source,
            'confidence_score': float(business.confidence_score) if business.confidence_score else None,
            'created_at': business.created_at.isoformat() if business.created_at else None,
        })
    
    df = pd.DataFrame(data)
    
    # Create export directory if it doesn't exist
    os.makedirs(settings.EXPORT_DIR, exist_ok=True)
    
    # Generate filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"zzp_without_website_{timestamp}.csv"
    filepath = os.path.join(settings.EXPORT_DIR, filename)
    
    # Export to CSV
    df.to_csv(filepath, index=False, encoding='utf-8')
    
    logger.info(f"Exported {len(businesses)} ZZP businesses without website to {filename}")
    
    return FileResponse(
        path=filepath,
        filename=filename,
        media_type='text/csv'
    ) 