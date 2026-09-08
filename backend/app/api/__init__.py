from fastapi import APIRouter
from backend.app.api.documents import router as documents_router
from backend.app.api.facts import router as facts_router
from backend.app.api.relationships import router as relationships_router
from backend.app.api.analysis import router as analysis_router

api_router = APIRouter()
api_router.include_router(documents_router)
api_router.include_router(facts_router)
api_router.include_router(relationships_router)
api_router.include_router(analysis_router)
