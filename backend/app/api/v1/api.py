from fastapi import APIRouter

from app.api.v1.endpoints import (
    health,
    auth,
    users,
    projects,
    commitments,
    sponsorship_requests,
    sponsorships_alias,
    trust,
    ai,
    admin,
    profiles,
    sponsors,
    messages,
    notifications,
    reports_disputes,
)

api_router = APIRouter()

api_router.include_router(health.router, tags=["Health"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(profiles.router, prefix="/profiles", tags=["Professional Profiles"])
api_router.include_router(projects.router, prefix="/projects", tags=["Projects"])
api_router.include_router(sponsors.router, prefix="/sponsors", tags=["Sponsor Discovery"])
api_router.include_router(sponsorship_requests.router, prefix="/sponsorship-requests", tags=["Sponsorship Requests"])
api_router.include_router(sponsorships_alias.router, prefix="/sponsorships", tags=["Sponsorship Requests"])
api_router.include_router(commitments.router, prefix="/commitments", tags=["Sponsorship Commitments"])
api_router.include_router(trust.router, prefix="/trust", tags=["Trust Scores"])
api_router.include_router(messages.router, prefix="/messages", tags=["Messaging"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])
api_router.include_router(reports_disputes.router, prefix="", tags=["Reports & Disputes"])
api_router.include_router(ai.router, prefix="/ai", tags=["AI Services"])
api_router.include_router(admin.router, prefix="/admin", tags=["Admin Moderation"])

