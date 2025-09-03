from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional

from ..core.deps import get_current_user, get_current_active_user, get_current_admin_user
from ..core.database import get_db
from ..models.user import User

security = HTTPBearer(auto_error=False)


class AuthMiddleware:
    """Authentication middleware for protecting routes."""
    
    def __init__(self, require_verification: bool = True, require_admin: bool = False):
        self.require_verification = require_verification
        self.require_admin = require_admin
    
    async def __call__(self, request: Request):
        """Middleware function."""
        # Get authorization header
        authorization: Optional[str] = request.headers.get("Authorization")
        
        if not authorization:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authorization header missing"
            )
        
        # Extract token
        try:
            scheme, token = authorization.split()
            if scheme.lower() != "bearer":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication scheme"
                )
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization header format"
            )
        
        # Get database session
        db = next(get_db())
        
        try:
            # Create credentials object
            credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
            
            # Get user based on requirements
            if self.require_admin:
                user = get_current_admin_user(get_current_active_user(get_current_user(credentials, db)))
            elif self.require_verification:
                user = get_current_active_user(get_current_user(credentials, db))
            else:
                user = get_current_user(credentials, db)
            
            # Add user to request state
            request.state.current_user = user
            
        finally:
            db.close()


def require_auth(require_verification: bool = True):
    """Decorator to require authentication."""
    return AuthMiddleware(require_verification=require_verification)


def require_admin():
    """Decorator to require admin authentication."""
    return AuthMiddleware(require_verification=True, require_admin=True)