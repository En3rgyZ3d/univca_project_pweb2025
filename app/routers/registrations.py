from fastapi import APIRouter, Query, Path, HTTPException
from sqlalchemy.orm import session

from sqlmodel import select,delete
from typing import Annotated

from app.data.db import SessionDep
from app.models.registration import Registration
from app.models.event import Event, EventPublic
from app.models.user import User, UserPublic

router= APIRouter(prefix="/registrations")


@router.get("/")
def get_all_registrations(session: SessionDep) -> list[Registration]:
    """Returns all registrations"""
    statement = select(Registration)
    registrations = session.exec(statement).all()
    return registrations


@router.get("/{username}")
def get_user_registrations(
    username: Annotated[str,
    Path(description="The Username of the User to check")],
    session: SessionDep
) -> list[EventPublic]:
    """Returns all registrations of a given user"""
    statement = select(Event).join(Registration).where(Registration.username == username)
    registrations = session.exec(statement).all()
    return registrations


@router.delete("/{username}/{event_id}")
def delete_registration(
    username: Annotated[str, Path(description="The Username of the User to check")],
    event_id: Annotated[int, Path(description="The ID of the Event to check")],
    session: SessionDep
) -> str:
    """Deletes a registration"""
    statement = delete(Registration).where(Registration.username == username, Registration.event_id == event_id)
    session.exec(statement)
    session.commit()
    return ("Registration deleted successfully!")


