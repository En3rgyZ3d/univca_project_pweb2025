from fastapi import APIRouter, Path, HTTPException
from sqlalchemy.orm import session

from sqlmodel import select,delete
from typing import Annotated


from app.data.db import SessionDep
from app.models.event import EventPublic, Event, EventCreate

router = APIRouter(prefix="/events", tags=["events"])


@router.get("/")
def get_events(
        session: SessionDep
) -> list[EventPublic]:
    """Returns the events list."""
    events = session.exec(select(Event)).all() # Queries all the events in the Event table
    return events


@router.post("/")
def post_event(
        event: EventCreate,
        session: SessionDep
):
    """Adds a new event to the list."""
    session.add(Event.model_validate(event))
    # model_validate takes the data from the EventCreate instance and
    # creates an instance of Event, which can be added to the database.

    session.commit()
    return "Event successfully created."


@router.delete("/")
def delete_events(
        session: SessionDep
):
    """Deletes all events from the list."""
    session.exec(delete(Event))
    # Since we don't have a "WHERE" condition in the statement, the database
    # deletes all rows in the "event" table.
    session.commit()
    return "Events successfully deleted."


@router.get("/{id}")
def get_event_by_id(
        id: Annotated[int, Path(description="ID of the event to search")],
        session: SessionDep
) -> EventPublic:
    """Returns the event by id."""
    event = session.get(Event, id) # Event is the table, id is the PK.
    if event: # If the event is found, we return it; otherwise we return error code 404.
        return event
    else:
        raise HTTPException(status_code=404, detail="Event not found")

