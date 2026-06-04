from pydantic import BaseModel, EmailStr
from typing import Optional
import uuid
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserUpdate(UserBase):
    password: Optional[str] = None


class UserResponse(UserBase):
    id: uuid.UUID
    role: str
    subscription_tier: str
    created_at: datetime

    class Config:
        from_attributes = True
