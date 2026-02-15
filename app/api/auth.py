from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select

from app.core.database import get_session
from app.core.security import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token,
    get_password_hash,
    verify_password,
    get_current_user
)
from app.models.user import User, UserCreate, UserRead, UserRole

router = APIRouter()


@router.post("/signup", response_model=UserRead)
def create_user(user: UserCreate, session: Session = Depends(get_session)):
    statement = select(User).where(User.username == user.username)
    existing_user = session.exec(statement).first()
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Username already registered"
        )
    
    # Simple role assignment logic: if email contains "hr", assign HR role.
    # IN A REAL APP, THIS WOULD BE ADMIN-CONTROLLED OR DIFFERENTLY MANAGED.
    role = UserRole.USER
    if user.email and "hr" in user.email.lower():
        role = UserRole.HR
        
    # Create User object directly to avoid validation errors with missing hashed_password
    hashed_password = get_password_hash(user.password)
    
    # Exclude password and role from user dict
    user_data = user.model_dump(exclude={"password", "role"})
    
    db_user = User(**user_data, hashed_password=hashed_password, role=role)
    
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Session = Depends(get_session)
):
    statement = select(User).where(User.username == form_data.username)
    user = session.exec(statement).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user": {
             "username": user.username,
             "role": user.role
        }
    }

@router.get("/users/me", response_model=UserRead)
async def read_users_me(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user
