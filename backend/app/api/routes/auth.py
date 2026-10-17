from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.schemas.auth_schema import ProfileUpdate, UserCreate, UserResponse
from app.core.dependencies import get_current_user

from app.services.auth_service import (
    create_user,
    authenticate_user
)

from app.core.database import get_db
from app.core.security import create_access_token

router = APIRouter()


@router.post("/signup")
def signup(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    try:
        created_user = create_user(db, user.username, user.email, user.password, user.role)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    if not created_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    return {
        "message": "User created successfully",
        "user_id": created_user.id,
        "role": created_user.role
    }


@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    authenticated_user = authenticate_user(
        db,
        form_data.username,
        form_data.password
    )

    if not authenticated_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    access_token = create_access_token(
        data={
            "sub": authenticated_user.email,
            "user_id": authenticated_user.id,
            "role": authenticated_user.role
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse.model_validate(authenticated_user).model_dump()
    }


@router.get("/me", response_model=UserResponse)
def me(user=Depends(get_current_user)):
    return user


@router.patch("/me", response_model=UserResponse)
def update_me(profile: ProfileUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    user.username = profile.username
    db.commit()
    db.refresh(user)
    return user
