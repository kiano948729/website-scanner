"""
Jobs API endpoints for managing crawling tasks.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.crawl_job import CrawlJob, JobStatus, JobType
from app.services.celery_app import celery_app
import structlog

logger = structlog.get_logger(__name__)

router = APIRouter()


@router.get("/", response_model=List[dict])
async def get_jobs(
    skip: int = 0,
    limit: int = 100,
    status: JobStatus = None,
    job_type: JobType = None,
    db: Session = Depends(get_db)
):
    """Get list of crawl jobs."""
    query = db.query(CrawlJob)
    
    if status:
        query = query.filter(CrawlJob.status == status)
    if job_type:
        query = query.filter(CrawlJob.job_type == job_type)
    
    jobs = query.offset(skip).limit(limit).all()
    
    logger.info(f"Retrieved {len(jobs)} jobs")
    return [job.to_dict() for job in jobs]


@router.get("/{job_id}", response_model=dict)
async def get_job(job_id: int, db: Session = Depends(get_db)):
    """Get a specific job by ID."""
    job = db.query(CrawlJob).filter(CrawlJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    logger.info(f"Retrieved job {job_id}")
    return job.to_dict()


@router.post("/start-google-maps-crawl")
async def start_google_maps_crawl(
    location: str,
    industry: str = None,
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    """Start a Google Maps crawling job."""
    # Create job record
    job = CrawlJob(
        name=f"Google Maps crawl - {location}",
        job_type=JobType.GOOGLE_MAPS,
        status=JobStatus.PENDING,
        target_location=location,
        target_industry=industry,
        parameters=f'{{"location": "{location}", "industry": "{industry}"}}'
    )
    
    db.add(job)
    db.commit()
    db.refresh(job)
    
    # Start Celery task
    task = celery_app.send_task(
        'app.services.tasks.crawl_tasks.crawl_google_maps',
        args=[job.id, location, industry]
    )
    
    # Update job with task ID
    job.celery_task_id = task.id
    db.commit()
    
    logger.info(f"Started Google Maps crawl job {job.id} for {location}")
    return {"job_id": job.id, "task_id": task.id, "status": "started"}


@router.post("/start-website-check")
async def start_website_check(
    business_ids: List[int] = None,
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    """Start a website checking job."""
    # Create job record
    job = CrawlJob(
        name="Website check job",
        job_type=JobType.WEBSITE_CHECK,
        status=JobStatus.PENDING,
        parameters=f'{{"business_ids": {business_ids}}}'
    )
    
    db.add(job)
    db.commit()
    db.refresh(job)
    
    # Start Celery task
    task = celery_app.send_task(
        'app.services.tasks.website_check_tasks.check_websites',
        args=[job.id, business_ids]
    )
    
    # Update job with task ID
    job.celery_task_id = task.id
    db.commit()
    
    logger.info(f"Started website check job {job.id}")
    return {"job_id": job.id, "task_id": task.id, "status": "started"}


@router.post("/{job_id}/cancel")
async def cancel_job(job_id: int, db: Session = Depends(get_db)):
    """Cancel a running job."""
    job = db.query(CrawlJob).filter(CrawlJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.status not in [JobStatus.PENDING, JobStatus.RUNNING]:
        raise HTTPException(status_code=400, detail="Job cannot be cancelled")
    
    # Cancel Celery task if it exists
    if job.celery_task_id:
        celery_app.control.revoke(job.celery_task_id, terminate=True)
    
    job.status = JobStatus.CANCELLED
    db.commit()
    
    logger.info(f"Cancelled job {job_id}")
    return {"message": "Job cancelled successfully"}


@router.post("/{job_id}/retry")
async def retry_job(job_id: int, db: Session = Depends(get_db)):
    """Retry a failed job."""
    job = db.query(CrawlJob).filter(CrawlJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if not job.can_retry:
        raise HTTPException(status_code=400, detail="Job cannot be retried")
    
    # Reset job status
    job.status = JobStatus.PENDING
    job.retry_count += 1
    job.error_message = None
    
    # Start new Celery task based on job type
    if job.job_type == JobType.GOOGLE_MAPS:
        task = celery_app.send_task(
            'app.services.tasks.crawl_tasks.crawl_google_maps',
            args=[job.id, job.target_location, job.target_industry]
        )
    elif job.job_type == JobType.WEBSITE_CHECK:
        task = celery_app.send_task(
            'app.services.tasks.website_check_tasks.check_websites',
            args=[job.id, None]  # Will use all businesses
        )
    else:
        raise HTTPException(status_code=400, detail="Unsupported job type for retry")
    
    job.celery_task_id = task.id
    db.commit()
    
    logger.info(f"Retried job {job_id}")
    return {"job_id": job.id, "task_id": task.id, "status": "retried"} 