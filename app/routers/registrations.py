from fastapi import APIRouter, Query, HTTPException

from sqlmodel import select, delete
from typing import Annotated

from app.data.db import SessionDep
from app.models.registration import Registration
from app.models.event import Event
from app.models.user import User


router= APIRouter(prefix="/registrations", tags=["/registrations"])



@router.get("/")
def get_all_registrations(session: SessionDep) -> list[Registration]:
    """Returns all registrations."""
    # Queries the database to get all the registrations
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

    # Checks if the user and event exist; if not, raise an exception

    if not user_registered:
        raise HTTPException(status_code=404, detail="User not found")
    if not event_to_cancel:
        raise HTTPException(status_code=404, detail="Event not found")

    # Checks if the registration exists; if not, raise an exception
    registration_to_cancel = session.get(Registration, (username, event_id))

    if not registration_to_cancel:
        raise HTTPException(status_code=404, detail="Registration not found")

    statement = delete(Registration).where(Registration.username == username, # NOQA
                                           Registration.event_id == event_id)  # NOQA
    # NOQA disables a warning caused by a known type check bug in SQLAlchemy

    session.exec(statement)
    session.commit()
    return "Registration deleted successfully"

