"""Authentication routes for user registration and login"""

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse
from datetime import datetime
import uuid
import logging

from app.models import RegisterSchema, LoginSchema, TokenSchema, AdminSetupSchema
from app.database import get_db
from app.dependencies.auth import (
    create_access_token,
    get_password_hash,
    verify_password
)
from app.services.rate_limiting import limiter, AUTH_RATE_LIMIT

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/auth/register", response_model=TokenSchema)
@limiter.limit(AUTH_RATE_LIMIT)
async def register(request: RegisterSchema):
    """
    Register a new user with email and password.
    
    - **email**: User email address (must be unique)
    - **password**: Password (minimum 8 characters)
    
    Returns JWT token on successful registration.
    """
    db = get_db()
    
    # Validate email uniqueness
    existing_user = await db.users.find_one({"email": request.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password
    hashed_password = get_password_hash(request.password)
    
    # Create new user
    user_id = str(uuid.uuid4())
    user_doc = {
        "user_id": user_id,
        "email": request.email,
        "password": hashed_password,
        "role": "user",
        "provider": "email",
        "created_at": datetime.utcnow(),
        "preferences": {
            "favorite_ragas": [],
            "preferred_time_of_day": None,
            "listening_frequency": None
        },
        "total_sessions": 0
    }
    
    await db.users.insert_one(user_doc)
    logger.info(f"New user registered: {user_id}")
    
    # Create JWT token
    access_token = create_access_token(user_id, request.email, "user")
    
    return TokenSchema(
        access_token=access_token,
        token_type="bearer",
        user={
            "user_id": user_id,
            "email": request.email,
            "role": "user"
        }
    )


@router.post("/auth/login", response_model=TokenSchema)
async def login(request: LoginSchema):
    """
    Login with email and password.
    
    - **email**: User email address
    - **password**: User password
    
    Returns JWT token on successful login.
    """
    db = get_db()
    
    if db is None:
        logger.error("[Login] Database not initialized")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection failed"
        )
    
    # Find user by email
    user = await db.users.find_one({"email": request.email})
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Verify password
    if not verify_password(request.password, user.get("password", "")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    logger.info(f"User logged in: {user.get('user_id')}")
    
    # Create JWT token
    access_token = create_access_token(
        user["user_id"],
        user["email"],
        user.get("role", "user")
    )
    
    return TokenSchema(
        access_token=access_token,
        token_type="bearer",
        user={
            "user_id": user["user_id"],
            "email": user["email"],
            "role": user.get("role", "user")
        }
    )


@router.post("/setup-admin", response_model=TokenSchema)
async def setup_admin(request: AdminSetupSchema):
    """
    Create the first admin user. This endpoint is disabled after first admin is created.
    
    - **email**: Admin email address
    - **password**: Admin password (minimum 8 characters)
    
    Returns JWT token for the new admin.
    """
    db = get_db()
    
    # Check if any admin already exists
    admin_count = await db.users.count_documents({"role": "admin"})
    
    if admin_count > 0:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin already exists. This endpoint is disabled."
        )
    
    # Validate email uniqueness
    existing_user = await db.users.find_one({"email": request.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password
    hashed_password = get_password_hash(request.password)
    
    # Create admin user
    user_id = str(uuid.uuid4())
    admin_doc = {
        "user_id": user_id,
        "email": request.email,
        "password": hashed_password,
        "role": "admin",
        "provider": "email",
        "created_at": datetime.utcnow(),
        "preferences": {
            "favorite_ragas": [],
            "preferred_time_of_day": None,
            "listening_frequency": None
        },
        "total_sessions": 0
    }
    
    await db.users.insert_one(admin_doc)
    logger.info(f"Admin user created: {user_id}")
    
    # Create JWT token
    access_token = create_access_token(user_id, request.email, "admin")
    
    return TokenSchema(
        access_token=access_token,
        token_type="bearer",
        user={
            "user_id": user_id,
            "email": request.email,
            "role": "admin"
        }
    )
