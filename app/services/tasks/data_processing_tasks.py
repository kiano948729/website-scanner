"""
Celery tasks for data processing functionality.
"""

from celery import current_task
import structlog
import time
from datetime import datetime, timedelta
from typing import List

from app.database.connection import get_db_session
from app.models.business import Business
from app.models.website_check import WebsiteCheck
from app.models.crawl_job import CrawlJob
from app.services.celery_app import celery_app

logger = structlog.get_logger(__name__)


@celery_app.task(bind=True)
def cleanup_old_data(self, days_to_keep: int = 90):
    """Clean up old data to maintain database performance."""
    logger.info(f"Starting data cleanup, keeping {days_to_keep} days of data")
    
    db = get_db_session()
    try:
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        # Clean up old website checks
        old_checks = db.query(WebsiteCheck).filter(
            WebsiteCheck.created_at < cutoff_date
        ).delete()
        
        # Clean up old crawl jobs (keep only completed/failed ones)
        old_jobs = db.query(CrawlJob).filter(
            CrawlJob.created_at < cutoff_date,
            CrawlJob.status.in_(['completed', 'failed', 'cancelled'])
        ).delete()
        
        # Clean up old businesses that are not ZZP and have no website
        old_businesses = db.query(Business).filter(
            Business.created_at < cutoff_date,
            Business.is_zzp == False,
            Business.website_exists == False
        ).delete()
        
        db.commit()
        
        logger.info(f"Data cleanup completed", 
                   old_checks=old_checks, old_jobs=old_jobs, old_businesses=old_businesses)
        
        return {
            "status": "completed",
            "old_website_checks_deleted": old_checks,
            "old_jobs_deleted": old_jobs,
            "old_businesses_deleted": old_businesses
        }
        
    except Exception as e:
        logger.error(f"Error in data cleanup: {e}")
        raise
    finally:
        db.close()


@celery_app.task(bind=True)
def recalculate_confidence_scores(self):
    """Recalculate confidence scores for all businesses."""
    logger.info("Starting confidence score recalculation")
    
    db = get_db_session()
    try:
        businesses = db.query(Business).all()
        updated_count = 0
        
        for business in businesses:
            try:
                # Calculate new confidence score based on available data
                score = calculate_business_confidence(business)
                
                if business.confidence_score != score:
                    business.confidence_score = score
                    updated_count += 1
                
            except Exception as e:
                logger.error(f"Error calculating confidence for business {business.id}: {e}")
                continue
        
        db.commit()
        
        logger.info(f"Confidence score recalculation completed", updated_count=updated_count)
        
        return {
            "status": "completed",
            "businesses_updated": updated_count,
            "total_businesses": len(businesses)
        }
        
    except Exception as e:
        logger.error(f"Error in confidence score recalculation: {e}")
        raise
    finally:
        db.close()


def calculate_business_confidence(business: Business) -> float:
    """Calculate confidence score for a business."""
    score = 0.0
    
    # Base score for having basic information
    if business.name:
        score += 0.3
    
    if business.city:
        score += 0.2
    
    if business.country:
        score += 0.1
    
    if business.phone:
        score += 0.15
    
    if business.email:
        score += 0.15
    
    if business.address:
        score += 0.1
    
    # Bonus for having website information
    if business.website_exists is not None:
        score += 0.1
    
    if business.website_url:
        score += 0.1
    
    # Bonus for having business classification
    if business.business_type:
        score += 0.05
    
    if business.industry:
        score += 0.05
    
    # Cap at 1.0
    return min(score, 1.0)


@celery_app.task(bind=True)
def deduplicate_businesses(self):
    """Remove duplicate businesses based on name and location."""
    logger.info("Starting business deduplication")
    
    db = get_db_session()
    try:
        # Find potential duplicates
        duplicates = db.query(Business).filter(
            Business.name.isnot(None),
            Business.city.isnot(None)
        ).all()
        
        duplicate_groups = {}
        for business in duplicates:
            key = f"{business.name.lower()}_{business.city.lower()}"
            if key not in duplicate_groups:
                duplicate_groups[key] = []
            duplicate_groups[key].append(business)
        
        removed_count = 0
        for key, group in duplicate_groups.items():
            if len(group) > 1:
                # Keep the one with highest confidence score
                group.sort(key=lambda x: x.confidence_score or 0, reverse=True)
                
                # Remove duplicates, keeping the first one
                for duplicate in group[1:]:
                    db.delete(duplicate)
                    removed_count += 1
        
        db.commit()
        
        logger.info(f"Business deduplication completed", removed_count=removed_count)
        
        return {
            "status": "completed",
            "duplicates_removed": removed_count
        }
        
    except Exception as e:
        logger.error(f"Error in business deduplication: {e}")
        raise
    finally:
        db.close()


@celery_app.task(bind=True)
def enrich_business_data(self, business_ids: List[int] = None):
    """Enrich business data with additional information."""
    logger.info("Starting business data enrichment")
    
    db = get_db_session()
    try:
        if business_ids:
            businesses = db.query(Business).filter(Business.id.in_(business_ids)).all()
        else:
            # Enrich businesses that haven't been processed recently
            businesses = db.query(Business).filter(
                Business.is_processed == False
            ).limit(100).all()
        
        enriched_count = 0
        
        for business in businesses:
            try:
                # Enrich business data
                enriched = enrich_single_business(business)
                
                if enriched:
                    business.is_processed = True
                    enriched_count += 1
                
            except Exception as e:
                logger.error(f"Error enriching business {business.id}: {e}")
                continue
        
        db.commit()
        
        logger.info(f"Business data enrichment completed", enriched_count=enriched_count)
        
        return {
            "status": "completed",
            "businesses_enriched": enriched_count,
            "total_processed": len(businesses)
        }
        
    except Exception as e:
        logger.error(f"Error in business data enrichment: {e}")
        raise
    finally:
        db.close()


def enrich_single_business(business: Business) -> bool:
    """Enrich a single business with additional data."""
    # This is a placeholder for actual enrichment logic
    # In a real implementation, this would:
    # - Call external APIs for additional business information
    # - Analyze business name to determine industry
    # - Check social media presence
    # - Validate contact information
    # - etc.
    
    # For now, just mark as enriched if we have basic data
    if business.name and business.city:
        return True
    
    return False


@celery_app.task(bind=True)
def generate_daily_report(self):
    """Generate daily report of system activity."""
    logger.info("Generating daily report")
    
    db = get_db_session()
    try:
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        
        # Get statistics for yesterday
        new_businesses = db.query(Business).filter(
            Business.created_at >= yesterday,
            Business.created_at < today
        ).count()
        
        new_website_checks = db.query(WebsiteCheck).filter(
            WebsiteCheck.created_at >= yesterday,
            WebsiteCheck.created_at < today
        ).count()
        
        completed_jobs = db.query(CrawlJob).filter(
            CrawlJob.completed_at >= yesterday,
            CrawlJob.completed_at < today,
            CrawlJob.status == 'completed'
        ).count()
        
        failed_jobs = db.query(CrawlJob).filter(
            CrawlJob.completed_at >= yesterday,
            CrawlJob.completed_at < today,
            CrawlJob.status == 'failed'
        ).count()
        
        # Calculate totals
        total_businesses = db.query(Business).count()
        total_zzp_without_website = db.query(Business).filter(
            Business.is_zzp == True,
            Business.website_exists == False
        ).count()
        
        report = {
            "date": yesterday.isoformat(),
            "new_businesses": new_businesses,
            "new_website_checks": new_website_checks,
            "completed_jobs": completed_jobs,
            "failed_jobs": failed_jobs,
            "total_businesses": total_businesses,
            "total_zzp_without_website": total_zzp_without_website
        }
        
        logger.info("Daily report generated", report=report)
        
        return report
        
    except Exception as e:
        logger.error(f"Error generating daily report: {e}")
        raise
    finally:
        db.close() 