from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    user_id: int
    email: str
    full_name: str


class TokenPayload(BaseModel):
    sub: Optional[str] = None
    role: Optional[str] = None
    exp: Optional[int] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: str = Field(..., min_length=2, max_length=100)
    role: str = Field(..., pattern="^(entrepreneur|sponsor)$")

    # Optional initial role details
    headline: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None

    # Entrepreneur initial fields
    stage: Optional[str] = "idea"
    industry: Optional[str] = None

    # Sponsor initial fields
    organization_name: Optional[str] = None
    sponsor_type: Optional[str] = "individual_angel"
    min_budget: Optional[int] = 1000
    max_budget: Optional[int] = 50000
