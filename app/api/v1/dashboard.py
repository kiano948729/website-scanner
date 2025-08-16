"""
Dashboard API endpoints for statistics and monitoring.
"""

from typing import Dict, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timedelta

from app.database.connection import get_db
from app.models.business import Business
from app.models.crawl_job import CrawlJob, JobStatus
from app.models.website_check import WebsiteCheck
import structlog

logger = structlog.get_logger(__name__)

router = APIRouter()


@router.get("/stats")
async def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get dashboard statistics."""
    # Basic counts
    total_businesses = db.query(Business).count()
    businesses_with_website = db.query(Business).filter(Business.website_exists == True).count()
    businesses_without_website = total_businesses - businesses_with_website
    zzp_businesses = db.query(Business).filter(Business.is_zzp == True).count()
    zzp_without_website = db.query(Business).filter(
        and_(Business.is_zzp == True, Business.website_exists == False)
    ).count()
    
    # Recent activity (last 7 days)
    week_ago = datetime.now() - timedelta(days=7)
    recent_businesses = db.query(Business).filter(Business.created_at >= week_ago).count()
    recent_checks = db.query(WebsiteCheck).filter(WebsiteCheck.created_at >= week_ago).count()
    
    # Job statistics
    active_jobs = db.query(CrawlJob).filter(CrawlJob.status == JobStatus.RUNNING).count()
    completed_jobs = db.query(CrawlJob).filter(CrawlJob.status == JobStatus.COMPLETED).count()
    failed_jobs = db.query(CrawlJob).filter(CrawlJob.status == JobStatus.FAILED).count()
    
    # Geographic distribution
    country_stats = db.query(
        Business.country, 
        func.count(Business.id)
    ).group_by(Business.country).all()
    
    # Source distribution
    source_stats = db.query(
        Business.source, 
        func.count(Business.id)
    ).group_by(Business.source).all()
    
    # Website check statistics
    total_checks = db.query(WebsiteCheck).count()
    successful_checks = db.query(WebsiteCheck).filter(WebsiteCheck.is_error == False).count()
    failed_checks = total_checks - successful_checks
    
    stats = {
        "businesses": {
            "total": total_businesses,
            "with_website": businesses_with_website,
            "without_website": businesses_without_website,
            "zzp": zzp_businesses,
            "zzp_without_website": zzp_without_website,
            "recent_additions": recent_businesses,
        },
        "jobs": {
            "active": active_jobs,
            "completed": completed_jobs,
            "failed": failed_jobs,
        },
        "website_checks": {
            "total": total_checks,
            "successful": successful_checks,
            "failed": failed_checks,
            "recent": recent_checks,
        },
        "geographic": dict(country_stats),
        "sources": dict(source_stats),
    }
    
    logger.info("Retrieved dashboard statistics")
    return stats


@router.get("/recent-activity")
async def get_recent_activity(
    days: int = 7,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get recent activity."""
    since = datetime.now() - timedelta(days=days)
    
    # Recent businesses
    recent_businesses = db.query(Business).filter(
        Business.created_at >= since
    ).order_by(Business.created_at.desc()).limit(limit).all()
    
    # Recent jobs
    recent_jobs = db.query(CrawlJob).filter(
        CrawlJob.created_at >= since
    ).order_by(CrawlJob.created_at.desc()).limit(limit).all()
    
    # Recent website checks
    recent_checks = db.query(WebsiteCheck).filter(
        WebsiteCheck.created_at >= since
    ).order_by(WebsiteCheck.created_at.desc()).limit(limit).all()
    
    activity = {
        "businesses": [business.to_dict() for business in recent_businesses],
        "jobs": [job.to_dict() for job in recent_jobs],
        "website_checks": [check.to_dict() for check in recent_checks],
    }
    
    logger.info(f"Retrieved recent activity for last {days} days")
    return activity


@router.get("/top-cities")
async def get_top_cities(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get top cities by business count."""
    cities = db.query(
        Business.city,
        func.count(Business.id).label('count')
    ).filter(
        Business.city.isnot(None)
    ).group_by(Business.city).order_by(
        func.count(Business.id).desc()
    ).limit(limit).all()
    
    result = [{"city": city, "count": count} for city, count in cities]
    
    logger.info(f"Retrieved top {limit} cities")
    return result


@router.get("/top-industries")
async def get_top_industries(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get top industries by business count."""
    industries = db.query(
        Business.industry,
        func.count(Business.id).label('count')
    ).filter(
        Business.industry.isnot(None)
    ).group_by(Business.industry).order_by(
        func.count(Business.id).desc()
    ).limit(limit).all()
    
    result = [{"industry": industry, "count": count} for industry, count in industries]
    
    logger.info(f"Retrieved top {limit} industries")
    return result


@router.get("/website-check-success-rate")
async def get_website_check_success_rate(db: Session = Depends(get_db)):
    """Get website check success rate by check type."""
    success_rates = db.query(
        WebsiteCheck.check_type,
        func.count(WebsiteCheck.id).label('total'),
        func.sum(func.case([(WebsiteCheck.is_error == False, 1)], else_=0)).label('successful')
    ).group_by(WebsiteCheck.check_type).all()
    
    result = []
    for check_type, total, successful in success_rates:
        success_rate = (successful / total * 100) if total > 0 else 0
        result.append({
            "check_type": check_type,
            "total": total,
            "successful": successful,
            "success_rate": round(success_rate, 2)
        })
    
    logger.info("Retrieved website check success rates")
    return result


@router.get("/job-performance")
async def get_job_performance(db: Session = Depends(get_db)):
    """Get job performance statistics."""
    # Job completion rates by type
    job_stats = db.query(
        CrawlJob.job_type,
        func.count(CrawlJob.id).label('total'),
        func.sum(func.case([(CrawlJob.status == JobStatus.COMPLETED, 1)], else_=0)).label('completed'),
        func.sum(func.case([(CrawlJob.status == JobStatus.FAILED, 1)], else_=0)).label('failed')
    ).group_by(CrawlJob.job_type).all()
    
    result = []
    for job_type, total, completed, failed in job_stats:
        completion_rate = (completed / total * 100) if total > 0 else 0
        failure_rate = (failed / total * 100) if total > 0 else 0
        
        result.append({
            "job_type": job_type.value if job_type else None,
            "total": total,
            "completed": completed,
            "failed": failed,
            "completion_rate": round(completion_rate, 2),
            "failure_rate": round(failure_rate, 2)
        })
    
    logger.info("Retrieved job performance statistics")
    return result 