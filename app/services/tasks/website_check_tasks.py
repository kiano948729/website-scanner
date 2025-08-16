"""
Celery tasks for website checking functionality.
"""

from celery import current_task
import structlog
import time
import requests
import dns.resolver
from typing import List, Optional

from app.database.connection import get_db_session
from app.models.business import Business
from app.models.website_check import WebsiteCheck
from app.models.crawl_job import CrawlJob, JobStatus
from app.services.celery_app import celery_app

logger = structlog.get_logger(__name__)


@celery_app.task(bind=True)
def check_websites(self, job_id: int, business_ids: Optional[List[int]] = None):
    """Check websites for businesses."""
    logger.info(f"Starting website check job {job_id}", business_ids=business_ids)
    
    db = get_db_session()
    try:
        # Update job status
        job = db.query(CrawlJob).filter(CrawlJob.id == job_id).first()
        if job:
            job.status = JobStatus.RUNNING
            job.started_at = time.time()
            db.commit()
        
        # Get businesses to check
        if business_ids:
            businesses = db.query(Business).filter(Business.id.in_(business_ids)).all()
        else:
            # Check all businesses that haven't been checked recently
            businesses = db.query(Business).filter(
                Business.website_exists.is_(None)
            ).limit(100).all()  # Limit to prevent overwhelming
        
        total_businesses = len(businesses)
        successful_checks = 0
        failed_checks = 0
        
        logger.info(f"Checking websites for {total_businesses} businesses")
        
        for i, business in enumerate(businesses):
            try:
                # Check website existence
                website_exists, confidence_score, check_details = check_business_website(business)
                
                # Create website check record
                website_check = WebsiteCheck(
                    business_id=business.id,
                    check_type="combined",
                    url_checked=f"https://{business.name.lower().replace(' ', '')}.nl",
                    website_exists=website_exists,
                    confidence_score=confidence_score,
                    status_code=check_details.get("status_code"),
                    response_time=check_details.get("response_time"),
                    dns_records=str(check_details.get("dns_records", [])),
                    headers=str(check_details.get("headers", {})),
                    error_message=check_details.get("error_message"),
                    is_error=check_details.get("is_error", False)
                )
                db.add(website_check)
                
                # Update business record
                business.website_exists = website_exists
                business.website_confidence_score = confidence_score
                business.last_checked = time.time()
                
                if website_exists:
                    business.website_url = f"https://{business.name.lower().replace(' ', '')}.nl"
                
                successful_checks += 1
                logger.info(f"Checked website for {business.name}: {website_exists}")
                
            except Exception as e:
                failed_checks += 1
                logger.error(f"Error checking website for {business.name}: {e}")
                
                # Create error record
                website_check = WebsiteCheck(
                    business_id=business.id,
                    check_type="combined",
                    url_checked=f"https://{business.name.lower().replace(' ', '')}.nl",
                    website_exists=False,
                    confidence_score=0.0,
                    error_message=str(e),
                    is_error=True
                )
                db.add(website_check)
            
            # Update progress
            current_task.update_state(
                state='PROGRESS',
                meta={'current': i + 1, 'total': total_businesses}
            )
            
            time.sleep(0.5)  # Rate limiting
        
        # Update job status
        if job:
            job.status = JobStatus.COMPLETED
            job.completed_at = time.time()
            job.total_items = total_businesses
            job.processed_items = total_businesses
            job.successful_items = successful_checks
            job.failed_items = failed_checks
            db.commit()
        
        logger.info(f"Completed website check job {job_id}", 
                   successful=successful_checks, failed=failed_checks, total=total_businesses)
        
        return {
            "status": "completed",
            "successful_checks": successful_checks,
            "failed_checks": failed_checks,
            "total_processed": total_businesses
        }
        
    except Exception as e:
        logger.error(f"Error in website check job {job_id}: {e}")
        
        # Update job status to failed
        if job:
            job.status = JobStatus.FAILED
            job.error_message = str(e)
            db.commit()
        
        raise
    finally:
        db.close()


def check_business_website(business: Business) -> tuple[bool, float, dict]:
    """Check if a business has a website."""
    business_name = business.name.lower().replace(' ', '').replace('-', '')
    potential_domains = [
        f"{business_name}.nl",
        f"{business_name}.com",
        f"{business_name}.be",
        f"{business_name}.de",
        f"{business_name}.lu"
    ]
    
    check_details = {
        "dns_records": [],
        "headers": {},
        "status_code": None,
        "response_time": None,
        "error_message": None,
        "is_error": False
    }
    
    for domain in potential_domains:
        try:
            # DNS check
            try:
                dns_records = dns.resolver.resolve(domain, 'A')
                check_details["dns_records"] = [str(record) for record in dns_records]
                
                # HTTP check
                start_time = time.time()
                response = requests.get(
                    f"https://{domain}",
                    timeout=10,
                    headers={'User-Agent': 'Mozilla/5.0 (compatible; ZZP-Scanner/1.0)'}
                )
                response_time = time.time() - start_time
                
                check_details["status_code"] = response.status_code
                check_details["response_time"] = response_time
                check_details["headers"] = dict(response.headers)
                
                if response.status_code == 200:
                    return True, 0.9, check_details
                elif response.status_code < 400:
                    return True, 0.7, check_details
                    
            except dns.resolver.NXDOMAIN:
                continue
            except Exception as e:
                check_details["error_message"] = str(e)
                continue
                
        except Exception as e:
            check_details["error_message"] = str(e)
            continue
    
    # If no website found, return False
    return False, 0.0, check_details


@celery_app.task(bind=True)
def check_single_website(self, business_id: int):
    """Check website for a single business."""
    logger.info(f"Checking website for business {business_id}")
    
    db = get_db_session()
    try:
        business = db.query(Business).filter(Business.id == business_id).first()
        if not business:
            raise ValueError(f"Business {business_id} not found")
        
        website_exists, confidence_score, check_details = check_business_website(business)
        
        # Create website check record
        website_check = WebsiteCheck(
            business_id=business.id,
            check_type="single",
            url_checked=f"https://{business.name.lower().replace(' ', '')}.nl",
            website_exists=website_exists,
            confidence_score=confidence_score,
            status_code=check_details.get("status_code"),
            response_time=check_details.get("response_time"),
            dns_records=str(check_details.get("dns_records", [])),
            headers=str(check_details.get("headers", {})),
            error_message=check_details.get("error_message"),
            is_error=check_details.get("is_error", False)
        )
        db.add(website_check)
        
        # Update business record
        business.website_exists = website_exists
        business.website_confidence_score = confidence_score
        business.last_checked = time.time()
        
        if website_exists:
            business.website_url = f"https://{business.name.lower().replace(' ', '')}.nl"
        
        db.commit()
        
        logger.info(f"Completed website check for {business.name}: {website_exists}")
        
        return {
            "business_id": business_id,
            "website_exists": website_exists,
            "confidence_score": confidence_score
        }
        
    except Exception as e:
        logger.error(f"Error checking website for business {business_id}: {e}")
        raise
    finally:
        db.close() 