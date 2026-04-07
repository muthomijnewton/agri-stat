from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.models import User
from app.schemas.schemas import LoginRequest, LoginResponse

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/login", response_model=LoginResponse, status_code=status.HTTP_200_OK)
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    """
    Login endpoint with simple username/password authentication
    For production, implement proper password hashing (bcrypt, argon2, etc.)
    """
    # Find user by username
    user = db.query(User).filter(User.username == credentials.username).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    # Check password (simple comparison for now - use hashing in production)
    if user.password != credentials.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Return user data on successful login
    return LoginResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        is_admin=user.is_admin,
        message="Login successful"
    )

@router.post("/verify", response_model=LoginResponse)
def verify_user(credentials: LoginRequest, db: Session = Depends(get_db)):
    """
    Verify user credentials (same as login, can be used for session validation)
    """
    return login(credentials, db)
