from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.core.security import verify_password, get_password_hash
from app.repositories.user import user_repo
from app.schemas.user import UserCreate
from app.models.user import User

class AuthService:
    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> User:
        """Validates user credentials and returns the User object if successful."""
        user = user_repo.get_by_email(db, email)
        if not user or not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user

    @staticmethod
    def register_user(db: Session, user_in: UserCreate) -> User:
        """Registers a new user after checking if the email is already in use."""
        if user_repo.get_by_email(db, user_in.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
        # Hash the password before saving
        hashed_password = get_password_hash(user_in.password)
        db_user = User(
            email=user_in.email,
            password_hash=hashed_password,
            role=user_in.role,
            name=user_in.name,
            phone=user_in.phone
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

auth_service = AuthService()
