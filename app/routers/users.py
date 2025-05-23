from fastapi import APIRouter, Path, HTTPException, status
from sqlmodel import select,delete
from typing import Annotated
from app.data.db import SessionDep
from app.models.user import UserPublic, User, UserCreate
from app.models.registration import Registration
from app.models.user import UserPublic, User
from datetime import datetime

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/")
def get_users(session: SessionDep) -> list[UserPublic]:
    """Returns the list of existing users"""
    users = session.exec(select(User)).all() # Queries all the users in the users table
    return users

@router.post("/")
def create_user(session: SessionDep, user: UserCreate):
    """Creates a new user"""
    session.add(User.model_validate(user))
    session.commit()
    return "User successfully created."

@router.delete("/")
def delete_users(session: SessionDep):
    """Deletes all users from the list."""
    session.exec(delete(User))
    session.commit()
    return "Users successfully deleted."

@router.get("/{username}", response_model=UserPublic)
def get_user_by_username(username: Annotated[str, Path(description="Username of the user to search")], session: SessionDep):
    # Retrieve a user by username from the database.
    user = session.exec(select(User).where(User.username == username)).first()
    if not user:
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.delete("/{username}")
def delete_a_user(username: Annotated[str, Path(description="Username of the user to delete")], session: SessionDep):
    """Delete a user from the list."""

    session.exec(delete(User).where(User.username == username))
    session.commit()

    return "User successfully deleted."











