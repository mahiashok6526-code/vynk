from fastapi import APIRouter

from app.api.v1.endpoints import (
    health,
    auth,
    users,
    projects,
    commitments,
    trust,
    ai,
    admin,
)

api_router = APIRouter()

api_router.include_router(health.router, tags=["Health"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(projects.router, prefix="/projects", tags=["Projects"])
api_router.include_router(commitments.router, prefix="/commitments", tags=["Sponsorship Commitments"])
api_router.include_router(trust.router, prefix="/trust", tags=["Trust Scores"])
api_router.include_router(ai.router, prefix="/ai", tags=["AI Services"])
api_router.include_router(admin.router, prefix="/admin", tags=["Admin Moderation"])
