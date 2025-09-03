from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..schemas.auth import (
    UserRegister, UserLogin, TokenResponse, RefreshTokenRequest,
    ForgotPasswordRequest, ResetPasswordRequest, VerifyEmailRequest,
    ResendVerificationRequest, MessageResponse
)
from ..services.auth_service import AuthService
from ..middleware.rate_limit import auth_rate_limit, password_reset_rate_limit

router = APIRouter()


@router.post("/register", response_model=MessageResponse)
@auth_rate_limit()
async def register(
    request: Request,
    user_data: UserRegister,
    db: Session = Depends(get_db)
):
    """Register a new user."""
    auth_service = AuthService(db)
    
    try:
        user = auth_service.register_user(user_data)
        return MessageResponse(
            message="User registered successfully. Please check your email for verification."
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/login", response_model=TokenResponse)
@auth_rate_limit()
async def login(
    request: Request,
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    """Authenticate user and return JWT tokens."""
    auth_service = AuthService(db)
    
    # Authenticate user
    user = auth_service.authenticate_user(login_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Create tokens
    tokens = auth_service.create_tokens(user)
    return TokenResponse(**tokens)


@router.post("/logout", response_model=MessageResponse)
async def logout(
    request: Request,
    db: Session = Depends(get_db)
):
    """Logout user and blacklist token."""
    authorization = request.headers.get("Authorization", "")
    
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header"
        )
    
    token = authorization.split(" ")[1]
    auth_service = AuthService(db)
    auth_service.logout_user(token)
    
    return MessageResponse(message="Successfully logged out")


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    token_data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """Refresh access token using refresh token."""
    auth_service = AuthService(db)
    
    try:
        tokens = auth_service.refresh_access_token(token_data.refresh_token)
        return TokenResponse(**tokens)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )


@router.post("/forgot-password", response_model=MessageResponse)
@password_reset_rate_limit()
async def forgot_password(
    request: Request,
    forgot_data: ForgotPasswordRequest,
    db: Session = Depends(get_db)
):
    """Initiate password reset flow."""
    auth_service = AuthService(db)
    auth_service.forgot_password(forgot_data.email)
    
    return MessageResponse(
        message="If an account with that email exists, you will receive password reset instructions."
    )


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(
    reset_data: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    """Reset password using reset token."""
    auth_service = AuthService(db)
    
    try:
        auth_service.reset_password(reset_data.token, reset_data.new_password)
        return MessageResponse(message="Password reset successfully")
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset failed"
        )


@router.post("/verify-email", response_model=MessageResponse)
async def verify_email(
    verify_data: VerifyEmailRequest,
    db: Session = Depends(get_db)
):
    """Verify user email with verification token."""
    auth_service = AuthService(db)
    
    try:
        auth_service.verify_email(verify_data.token)
        return MessageResponse(message="Email verified successfully")
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Email verification failed"
        )


@router.post("/resend-verification", response_model=MessageResponse)
@auth_rate_limit()
async def resend_verification(
    request: Request,
    resend_data: ResendVerificationRequest,
    db: Session = Depends(get_db)
):
    """Resend email verification."""
    auth_service = AuthService(db)
    
    try:
        auth_service.resend_verification(resend_data.email)
        return MessageResponse(
            message="If an unverified account with that email exists, verification email has been sent."
        )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to resend verification email"
        )