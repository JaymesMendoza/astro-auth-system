from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from fastapi import HTTPException, status, UploadFile
from typing import Optional, List

from ..models.user import User
from ..core.security import verify_password, get_password_hash
from ..schemas.user import UserUpdate, ChangePassword
from .upload_service import UploadService


class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.upload_service = UploadService()

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return self.db.query(User).filter(User.id == user_id).first()

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        return self.db.query(User).filter(User.email == email).first()

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        return self.db.query(User).filter(User.username == username).first()

    def update_user_profile(self, user: User, update_data: UserUpdate) -> User:
        """Update user profile."""
        for field, value in update_data.dict(exclude_unset=True).items():
            setattr(user, field, value)
        
        self.db.commit()
        self.db.refresh(user)
        return user

    def change_user_password(self, user: User, password_data: ChangePassword) -> User:
        """Change user password."""
        # Verify current password
        if not verify_password(password_data.current_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Update password
        user.password_hash = get_password_hash(password_data.new_password)
        self.db.commit()
        self.db.refresh(user)
        
        return user

    def upload_user_avatar(self, user: User, file: UploadFile) -> User:
        """Upload user avatar."""
        # Validate file
        if not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be an image"
            )
        
        # Upload to Cloudinary
        avatar_url = self.upload_service.upload_image(file, f"avatars/user_{user.id}")
        
        # Update user avatar
        user.avatar_url = avatar_url
        self.db.commit()
        self.db.refresh(user)
        
        return user

    def delete_user_account(self, user: User) -> None:
        """Delete user account."""
        self.db.delete(user)
        self.db.commit()

    def get_users_list(
        self, 
        page: int = 1, 
        per_page: int = 20, 
        search: Optional[str] = None,
        role: Optional[str] = None,
        is_verified: Optional[bool] = None
    ) -> dict:
        """Get paginated list of users with filters."""
        query = self.db.query(User)
        
        # Apply filters
        if search:
            search_filter = or_(
                User.email.ilike(f"%{search}%"),
                User.username.ilike(f"%{search}%"),
                User.first_name.ilike(f"%{search}%"),
                User.last_name.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
        
        if role:
            query = query.filter(User.role == role)
        
        if is_verified is not None:
            query = query.filter(User.is_verified == is_verified)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * per_page
        users = query.offset(offset).limit(per_page).all()
        
        # Calculate pagination info
        pages = (total + per_page - 1) // per_page
        
        return {
            "users": users,
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": pages
        }

    def update_user_admin(self, user: User, update_data: dict) -> User:
        """Update user (admin only)."""
        # Check if email or username already exists (if being changed)
        if "email" in update_data and update_data["email"] != user.email:
            existing_email = self.db.query(User).filter(
                and_(User.email == update_data["email"], User.id != user.id)
            ).first()
            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already exists"
                )
        
        if "username" in update_data and update_data["username"] != user.username:
            existing_username = self.db.query(User).filter(
                and_(User.username == update_data["username"], User.id != user.id)
            ).first()
            if existing_username:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already exists"
                )
        
        # Update fields
        for field, value in update_data.items():
            if hasattr(user, field):
                setattr(user, field, value)
        
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_user_stats(self) -> dict:
        """Get user statistics."""
        total_users = self.db.query(User).count()
        verified_users = self.db.query(User).filter(User.is_verified == True).count()
        unverified_users = total_users - verified_users
        admin_users = self.db.query(User).filter(User.role == "admin").count()
        
        # Recent registrations (last 7 days)
        from datetime import datetime, timedelta
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_registrations = self.db.query(User).filter(
            User.created_at >= week_ago
        ).count()
        
        return {
            "total_users": total_users,
            "verified_users": verified_users,
            "unverified_users": unverified_users,
            "admin_users": admin_users,
            "recent_registrations": recent_registrations
        }