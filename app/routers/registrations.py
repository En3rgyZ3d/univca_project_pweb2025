from fastapi import APIRouter, Query, Path, HTTPException
from sqlalchemy.orm import session

from sqlmodel import select, delete
from typing import Annotated

from app.data.db import SessionDep
from app.models.registration import Registration
from app.models.event import Event, EventPublic
from app.models.user import User, UserPublic

router= APIRouter(prefix="/registrations", tags=["/registrations"])


@router.get("/")
def get_all_registrations(session: SessionDep) -> list[Registration]:
    """Returns all registrations."""
    # Does a query to get all the registrations
    registrations = session.exec(select(Registration)).all()
    return registrations




@router.delete("/")
def delete_registration(
        username: Annotated[str, Query(description="The Username of the User to check")],
        event_id: Annotated[int, Query(description="The ID of the Event to check")],
        session: SessionDep
) -> str:
    """Deletes a registration."""
    user_registered = session.get(User, username)
    event_to_cancel = session.get(Event, event_id)

    # check if the user and event exist if not raise an exception
    if not user_registered:
        raise HTTPException(status_code=404, detail="User not found")
    if not event_to_cancel:
        raise HTTPException(status_code=404, detail="Event not found")

    # check if the registration exists if not raise an exception
    registration_to_cancel = session.get(Registration, (username, event_id))

    if not registration_to_cancel:
        raise HTTPException(status_code=404, detail="Registration not found")

    statement = delete(Registration).where((Registration.username == username), (Registration.event_id == event_id))  # NOQA
    # No Quality Assurance tag that disables warnings in the line, because of a bug in type checks in SQLAlchemy
    session.exec(statement)
    session.commit()

    return "Registration deleted successfully"

