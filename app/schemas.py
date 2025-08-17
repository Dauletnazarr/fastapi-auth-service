from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

class UserOut(BaseModel):
    id: int
    email: EmailStr
    is_active: bool
    is_email_verified: bool
    created_at: datetime

    model_config = {"from_attributes": True}

class RegisterIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshIn(BaseModel):
    refresh_token: str

class ChangePasswordIn(BaseModel):
    old_password: str
    new_password: str = Field(min_length=8)
