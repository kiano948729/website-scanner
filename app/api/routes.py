"""
Main API router with all route endpoints.
"""

from fastapi import APIRouter

from app.api.v1.businesses import router as businesses_router
from app.api.v1.jobs import router as jobs_router
from app.api.v1.website_checks import router as website_checks_router
from app.api.v1.exports import router as exports_router
from app.api.v1.dashboard import router as dashboard_router

# Create main API router
api_router = APIRouter()

# Include all route modules
api_router.include_router(businesses_router, prefix="/businesses", tags=["businesses"])
api_router.include_router(jobs_router, prefix="/jobs", tags=["jobs"])
api_router.include_router(website_checks_router, prefix="/website-checks", tags=["website-checks"])
api_router.include_router(exports_router, prefix="/exports", tags=["exports"])
api_router.include_router(dashboard_router, prefix="/dashboard", tags=["dashboard"]) 