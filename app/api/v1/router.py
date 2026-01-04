"""Main API v1 router."""

from fastapi import APIRouter

from app.api.v1 import datasets, domains, documents, export, health, models, review, segments, templates, training_jobs

api_router = APIRouter()

# API v1 routes (health is included directly in main.py at root level)
api_router.include_router(domains.router)
api_router.include_router(documents.router)
api_router.include_router(segments.router)
api_router.include_router(templates.router)
api_router.include_router(datasets.router)
api_router.include_router(review.router)
api_router.include_router(export.router)
api_router.include_router(models.router)
api_router.include_router(training_jobs.router)

