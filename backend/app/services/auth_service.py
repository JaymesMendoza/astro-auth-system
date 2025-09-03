from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_
from fastapi import HTTPException, status
from typing import Optional

from ..models.user import User
from ..models.token import EmailVerificationToken, PasswordResetToken, TokenBlacklist
from ..core.security import (
    verify_password, 
    get_password_hash, 
    create_access_token, 
    create_refresh_token,
    generate_verification_token,
    generate_reset_token,
    verify_token
)
from ..schemas.auth import UserRegister, UserLogin
from .email_service import EmailService


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.email_service = EmailService()

    def register_user(self, user_data: UserRegister) -> User:
        """Register a new user."""
        # Check if user already exists
        existing_user = self.db.query(User).filter(
            (User.email == user_data.email) | (User.username == user_data.username)
        ).first()
        
        if existing_user:
            if existing_user.email == user_data.email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken"
                )

        # Create new user
        hashed_password = get_password_hash(user_data.password)
        user = User(
            email=user_data.email,
            username=user_data.username,
            password_hash=hashed_password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            is_verified=False
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        # Generate verification token
        verification_token = generate_verification_token()
        expires_at = datetime.utcnow() + timedelta(hours=24)
        
        token_record = EmailVerificationToken(
            user_id=user.id,
            token=verification_token,
            expires_at=expires_at
        )
        
        self.db.add(token_record)
        self.db.commit()

        # Send verification email
        self.email_service.send_verification_email(user.email, verification_token)

        return user

    def authenticate_user(self, login_data: UserLogin) -> Optional[User]:
        """Authenticate user with email and password."""
        user = self.db.query(User).filter(User.email == login_data.email).first()
        
        if not user or not verify_password(login_data.password, user.password_hash):
            return None
        
        return user

    def create_tokens(self, user: User) -> dict:
        """Create access and refresh tokens for user."""
        access_token = create_access_token(data={"sub": str(user.id)})
        refresh_token = create_refresh_token(data={"sub": str(user.id)})
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }

    def refresh_access_token(self, refresh_token: str) -> dict:
        """Create new access token from refresh token."""
        payload = verify_token(refresh_token, "refresh")
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        return self.create_tokens(user)

    def logout_user(self, token: str) -> None:
        """Blacklist access token."""
        try:
            payload = verify_token(token, "access")
            expires_at = datetime.fromtimestamp(payload.get("exp"))
            
            blacklisted_token = TokenBlacklist(
                token_jti=token,
                expires_at=expires_at
            )
            
            self.db.add(blacklisted_token)
            self.db.commit()
        except Exception:
            # Token might be invalid, but that's okay for logout
            pass

    def verify_email(self, token: str) -> User:
        """Verify user email with token."""
        token_record = self.db.query(EmailVerificationToken).filter(
            and_(
                EmailVerificationToken.token == token,
                EmailVerificationToken.used == False,
                EmailVerificationToken.expires_at > datetime.utcnow()
            )
        ).first()
        
        if not token_record:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired verification token"
            )
        
        user = self.db.query(User).filter(User.id == token_record.user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Mark user as verified and token as used
        user.is_verified = True
        token_record.used = True
        
        self.db.commit()
        self.db.refresh(user)
        
        return user

    def resend_verification(self, email: str) -> None:
        """Resend verification email."""
        user = self.db.query(User).filter(User.email == email).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already verified"
            )
        
        # Invalidate old tokens
        self.db.query(EmailVerificationToken).filter(
            and_(
                EmailVerificationToken.user_id == user.id,
                EmailVerificationToken.used == False
            )
        ).update({"used": True})
        
        # Generate new verification token
        verification_token = generate_verification_token()
        expires_at = datetime.utcnow() + timedelta(hours=24)
        
        token_record = EmailVerificationToken(
            user_id=user.id,
            token=verification_token,
            expires_at=expires_at
        )
        
        self.db.add(token_record)
        self.db.commit()

        # Send verification email
        self.email_service.send_verification_email(user.email, verification_token)

    def forgot_password(self, email: str) -> None:
        """Initiate password reset flow."""
        user = self.db.query(User).filter(User.email == email).first()
        
        if not user:
            # Don't reveal if email exists
            return
        
        # Invalidate old reset tokens
        self.db.query(PasswordResetToken).filter(
            and_(
                PasswordResetToken.user_id == user.id,
                PasswordResetToken.used == False
            )
        ).update({"used": True})
        
        # Generate new reset token
        reset_token = generate_reset_token()
        expires_at = datetime.utcnow() + timedelta(hours=1)
        
        token_record = PasswordResetToken(
            user_id=user.id,
            token=reset_token,
            expires_at=expires_at
        )
        
        self.db.add(token_record)
        self.db.commit()

        # Send reset email
        self.email_service.send_password_reset_email(user.email, reset_token)

    def reset_password(self, token: str, new_password: str) -> User:
        """Reset user password with token."""
        token_record = self.db.query(PasswordResetToken).filter(
            and_(
                PasswordResetToken.token == token,
                PasswordResetToken.used == False,
                PasswordResetToken.expires_at > datetime.utcnow()
            )
        ).first()
        
        if not token_record:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token"
            )
        
        user = self.db.query(User).filter(User.id == token_record.user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update password and mark token as used
        user.password_hash = get_password_hash(new_password)
        token_record.used = True
        
        self.db.commit()
        self.db.refresh(user)
        
        return user