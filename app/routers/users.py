from fastapi import APIRouter, Path, HTTPException

from sqlmodel import select,delete
from typing import Annotated

from app.data.db import SessionDep
from app.models.user import UserPublic, User, UserCreate
from app.models.registration import Registration


router = APIRouter(prefix="/users", tags=["users"])



@router.get("/")
def get_users(session: SessionDep) -> list[UserPublic]:
    """Returns the list of existing users"""
    users = session.exec(select(User)).all() # Queries all the users in the users table
    return users


@router.post("/")
def create_user(session: SessionDep, new_user: UserCreate):
    """Creates a new user"""

    # Before adding a user, we check if an email is already registered
    statement = select(User).where(User.email == new_user.email)

    duplicated_user_email = session.exec(statement).first()
    # .first() returns the first value of the query or None if no match is found

    if duplicated_user_email:
        raise HTTPException(status_code=409, detail="Email already registered") # 409 Conflict

    # Now we check if the username is already taken
    duplicated_user_username = session.get(User, new_user.username)

    if duplicated_user_username:
        raise HTTPException(status_code=409, detail="Username is already taken") # 409 Conflict
    else:
        session.add(User.model_validate(new_user))
        session.commit()

    return "User successfully created"


@router.delete("/")
def delete_users(session: SessionDep):
    """Deletes all users from the list."""
    session.exec(delete(User))
    session.commit()

    # Deletes all registrations from the list (same reason as in events endpoint).
    session.exec(delete(Registration))
    session.commit()

    # We don't check if users table is empty (same reason as in events endpoint).
    return "Users successfully deleted"


@router.get("/{username}", response_model=UserPublic)
def get_user_by_username(
        username: Annotated[str, Path(description="Username of the user to search")],
        session: SessionDep
):
    """Retrieves a user by username from the database."""
    user = session.get(User, username) # User is the table, username is the PK.
    if user: # If the user is found, we return it; otherwise we return error code 404.
        return user
    else:
        raise HTTPException(status_code=404, detail="User not found")


@router.delete("/{username}")
def delete_a_user(
        username: Annotated[str, Path(description="Username of the user to delete")],
        session: SessionDep
):
    """Deletes a user from the list."""

    # We check if the user exists
    valid_user = session.get(User, username)

    if not valid_user:
        raise HTTPException(status_code=404, detail="User not found")
    else:
        user_to_delete = session.get(User, username)
        session.delete(user_to_delete)
        session.commit()



    statement = delete(Registration).where(Registration.username == username)  # NOQA
    # With NOQA, we are disabling warnings that are known bugs in type checks with SQLAlchemy (safe to ignore)
    session.exec(statement)
    session.commit()

    return "User successfully deleted."

