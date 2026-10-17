from sqlalchemy.orm import Session

from app.models.user import User

from app.core.security import (
    hash_password,
    verify_password
)

ALLOWED_ROLES = {"recruiter", "candidate"}


def create_user(
    db: Session,
    username: str,
    email: str,
    password: str,
    role: str = "recruiter"
):

    if role not in ALLOWED_ROLES:
        raise ValueError("Invalid account role")

    existing_user = db.query(User).filter(
        (User.email == email) | (User.username == username)
    ).first()

    if existing_user:

        return None

    hashed_pw = hash_password(password)

    user = User(
        username=username,
        email=email,
        hashed_password=hashed_pw
        ,role=role
    )

    db.add(user)

    db.commit()

    db.refresh(user)

    return user


def authenticate_user(
    db: Session,
    email: str,
    password: str
):

    user = db.query(User).filter(
        User.email == email
    ).first()

    if not user:
        return None

    password_match = verify_password(
        password,
        user.hashed_password
    )

    if not password_match:
        return None

    return user
