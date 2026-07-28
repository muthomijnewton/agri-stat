from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.models import User
from app.schemas.schemas import LoginRequest, LoginResponse, UserProfileResponse, UserProfileUpdate
from app.core.security import (
    create_access_token,
    get_current_user,
    get_password_hash,
    password_is_hashed,
    verify_password,
)
from app.core.limiter import limiter

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse, status_code=status.HTTP_200_OK)
@limiter.limit("10/minute")
def login(request: Request, credentials: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == credentials.username).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    valid_password = (
        verify_password(credentials.password, user.password)
        if password_is_hashed(user.password)
        else user.password == credentials.password
    )

    if not valid_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    if not password_is_hashed(user.password):
        user.password = get_password_hash(credentials.password)
        db.commit()
        db.refresh(user)

    access_token = create_access_token(
        {
            "sub": user.username,
            "user_id": user.id,
            "is_admin": user.is_admin,
        }
    )

    return LoginResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        is_admin=user.is_admin,
        access_token=access_token,
        message="Login successful"
    )


@router.post("/verify", response_model=LoginResponse)
@limiter.limit("10/minute")
def verify_user(request: Request, credentials: LoginRequest, db: Session = Depends(get_db)):
    """
    Verify user credentials (same as login, can be used for session validation).
    """
    return login(request, credentials, db)


# ---------------------------------------------------------------------------
# Profile endpoints
# ---------------------------------------------------------------------------

@router.get("/me", response_model=UserProfileResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Return the authenticated user's full profile."""
    return current_user


@router.patch("/me", response_model=UserProfileResponse)
def update_me(
    updates: UserProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update the authenticated user's profile.

    - All fields are optional — only provided fields are changed.
    - To change the password supply current_password + new_password.
    - Username cannot be changed (used as the JWT subject).
    """
    data = updates.model_dump(exclude_unset=True)

    # ── Password change ──────────────────────────────────────────────────
    new_password   = data.pop("new_password",     None)
    curr_password  = data.pop("current_password", None)

    if new_password:
        if not curr_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="current_password is required to set a new password.",
            )
        if not verify_password(curr_password, current_user.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect.",
            )
        if len(new_password) < 6:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New password must be at least 6 characters.",
            )
        data["password"] = get_password_hash(new_password)

    # ── Apply remaining field updates ────────────────────────────────────
    for field, value in data.items():
        setattr(current_user, field, value)

    db.commit()
    db.refresh(current_user)
    return current_user
