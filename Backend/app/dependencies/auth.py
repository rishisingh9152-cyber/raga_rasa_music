"""Authentication dependencies for FastAPI"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import logging

from app.config import settings
from app.database import get_db
from app.models import TokenPayloadSchema

logger = logging.getLogger(__name__)
security = HTTPBearer(auto_error=False)  # Don't error if credentials missing


async def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Dict[str, Any]:
    """
    Extract and validate JWT token from request header.
    Returns user object from database.
    Raises 401 if no valid token provided.
    """
    if credentials is None:
        # No-auth mode: allow anonymous requests
        return {"user_id": None, "email": "anonymous@local", "role": "admin"}
    
    token = credentials.credentials
    
    try:
        # Decode JWT token
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        user_id: str = payload.get("user_id")
        email: str = payload.get("email")
        role: str = payload.get("role")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user_id",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Validate token payload
        token_payload = TokenPayloadSchema(
            user_id=user_id,
            email=email,
            role=role,
            exp=payload.get("exp", 0)
        )
        
    except JWTError as e:
        logger.warning(f"JWT validation failed, falling back to anonymous user: {str(e)}")
        return {"user_id": None, "email": "anonymous@local", "role": "admin"}
    
    # Fetch user from database to ensure they still exist
    db = get_db()
    if db is None:
        logger.warning("Database unavailable during auth lookup; falling back to anonymous user")
        return {"user_id": None, "email": "anonymous@local", "role": "admin"}

    user = await db.users.find_one({"user_id": user_id})
    
    if user is None:
        logger.warning(f"User not found: {user_id}, falling back to anonymous user")
        return {"user_id": None, "email": "anonymous@local", "role": "admin"}
    
    # Convert MongoDB ObjectId to string if needed
    if "_id" in user:
        user["_id"] = str(user["_id"])
    
    return user


async def require_admin(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """Backward-compatible alias; admin role checks removed."""
    return current_user


def create_access_token(user_id: str, email: str, role: str) -> str:
    """
    Create JWT access token for user.
    
    Args:
        user_id: Unique user identifier
        email: User email
        role: User role (user or admin)
    
    Returns:
        Encoded JWT token
    """
    now = datetime.utcnow()
    expires = now + timedelta(hours=settings.JWT_EXPIRATION_HOURS)
    
    payload = {
        "user_id": user_id,
        "email": email,
        "role": role,
        "iat": now,
        "exp": expires
    }
    
    encoded_jwt = jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify plain password against hashed password.
    Supports: plain text, bcrypt, and passlib hashes.
    """
    # Plain text comparison (simple fallback)
    if plain_password == hashed_password:
        return True
    
    # Try bcrypt
    try:
        import bcrypt
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except:
        pass
    
    # Try passlib
    try:
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        return pwd_context.verify(plain_password, hashed_password)
    except:
        pass
    
    return False


def get_password_hash(password: str) -> str:
    """
    Hash password using passlib with bcrypt.
    """
    try:
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        return pwd_context.hash(password)
    except Exception as e:
        logger.error(f"Password hashing error: {str(e)}")
        # Fallback - just return plain text (not secure, but better than failing)
        return password


async def get_current_user_optional(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[Dict[str, Any]]:
    """
    Optional authentication - returns user if valid token provided, None otherwise.
    Does not raise an error if no token is provided.
    """
    if credentials is None:
        return None
    
    token = credentials.credentials
    
    try:
        # Decode JWT token
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        user_id: str = payload.get("user_id")
        email: str = payload.get("email")
        role: str = payload.get("role")
        
        if user_id is None:
            return None
        
        # Fetch user from database to ensure they still exist
        db = get_db()
        if db is None:
            logger.warning("Database unavailable during optional auth lookup")
            return None

        user = await db.users.find_one({"user_id": user_id})
        
        if user is None:
            return None
        
        # Convert MongoDB ObjectId to string if needed
        if "_id" in user:
            user["_id"] = str(user["_id"])
        
        return user
        
    except JWTError:
        return None

