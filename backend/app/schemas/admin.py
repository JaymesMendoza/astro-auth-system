from pydantic import BaseModel, Field
from typing import List, Optional
from .user import UserResponse


class UserListResponse(BaseModel):
    users: List[UserResponse]
    total: int
    page: int
    per_page: int
    pages: int


class UserStatsResponse(BaseModel):
    total_users: int
    verified_users: int
    unverified_users: int
    admin_users: int
    recent_registrations: int


class AdminUserFilter(BaseModel):
    role: Optional[str] = Field(None, pattern="^(user|admin)$")
    is_verified: Optional[bool] = None
    search: Optional[str] = Field(None, max_length=255)


class PaginationParams(BaseModel):
    page: int = Field(1, ge=1)
    per_page: int = Field(20, ge=1, le=100)