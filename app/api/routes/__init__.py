# app/api/routes/__init__.py

from fastapi import APIRouter
from app.api.routes import studies

router = APIRouter()
router.include_router(studies.router, prefix="/studies", tags=["Studies"])
