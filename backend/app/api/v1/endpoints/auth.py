from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest, Token
from app.schemas.user import UserRead
from app.services.auth_service import AuthService

router = APIRouter()


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED, summary="Register User")
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """Register a new Entrepreneur or Sponsor account."""
    return await AuthService.register(db, data)


@router.post("/login", response_model=Token, summary="Login User")
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Authenticate with email and password to receive JWT access token."""
    return await AuthService.login(db, data)


@router.get("/me", response_model=UserRead, summary="Get Current User Profile")
async def get_me(current_user: User = Depends(get_current_user)):
    """Retrieve the authenticated user's profile and active role details."""
    return current_user
