from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..core.deps import get_current_active_user
from ..models.user import User
from ..schemas.user import UserProfile, UserUpdate, ChangePassword
from ..schemas.auth import MessageResponse
from ..services.user_service import UserService

router = APIRouter()


@router.get("/profile", response_model=UserProfile)
async def get_profile(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current user profile."""
    return current_user


@router.put("/profile", response_model=UserProfile)
async def update_profile(
    profile_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update current user profile."""
    user_service = UserService(db)
    
    try:
        updated_user = user_service.update_user_profile(current_user, profile_data)
        return updated_user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile"
        )


@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    password_data: ChangePassword,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Change user password."""
    user_service = UserService(db)
    
    try:
        user_service.change_user_password(current_user, password_data)
        return MessageResponse(message="Password changed successfully")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to change password"
        )


@router.post("/upload-avatar", response_model=UserProfile)
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Upload user avatar."""
    user_service = UserService(db)
    
    try:
        updated_user = user_service.upload_user_avatar(current_user, file)
        return updated_user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload avatar"
        )


@router.delete("/account", response_model=MessageResponse)
async def delete_account(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete user account."""
    user_service = UserService(db)
    
    try:
        user_service.delete_user_account(current_user)
        return MessageResponse(message="Account deleted successfully")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete account"
        )