from fastapi import APIRouter, Path, HTTPException

from sqlmodel import select,delete
from typing import Annotated

from app.data.db import SessionDep
from app.models.event import EventPublic, Event, EventCreate
from app.models.registration import Registration
from app.models.user import UserPublic, User

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
    return "Event successfully created"


@router.post("/{id}/register")
def register_user_to_event(
        user_to_register: UserPublic,
        id: Annotated[int, Path(description="ID of the event to register")],
        session: SessionDep
):
    """Registers a user to the event with the specified ID."""

    # First, we check if the parameters (user_to_register, event_to_register_id) are valid
    user = session.get(User, user_to_register.username)
    if not user:
        # If the user doesn't exist, we report an error.
        raise HTTPException(status_code=404, detail="User not found")

    # We need to check if the data matches to the corresponding user.
    if (user_to_register.name != user.name) or (user_to_register.email != user.email):
        raise HTTPException(
            status_code=409,
            detail="Provided user information does not match the registered user data."
        )

    # Now we can check if the event is valid.
    event = session.get(Event, id)
    if not event:
        # If the event doesn't exist, we report an error.
        raise HTTPException(status_code=404, detail="Event not found")

    #Then, we check if the registration already exists
    registration = session.get(Registration, (user_to_register.username, id))
    if registration:
        # If the registration already exists, we report an error.
        raise HTTPException(status_code=403, detail="This user is already registered for the event.")

    # Now we can add the registration

    new_registration = Registration(username=user_to_register.username, event_id=id)
    session.add(new_registration)
    session.commit()
    return "User successfully registered for this event."





@router.delete("/")
def delete_events(
        session: SessionDep
):
    """Deletes all events from the list."""
    session.exec(delete(Event))
    # Since we don't have a "WHERE" condition in the statement, the database
    # deletes all rows in the "event" table.
    session.commit()

    # Since we deleted all the events,
    # We need to cancel all the registrations too.

    session.exec(delete(Registration))
    session.commit()
    # We chose to cancel and confirm the table even if it's empty, in order to avoid
    # a misunderstanding by the user that might think that an error prevented them
    # to cancel the events.

    return "Events successfully deleted"


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


@router.put("/{id}")
def update_event(
        id: Annotated[int, Path(description="ID of the event to update")],
        new_event: EventCreate,
        session: SessionDep
):
    """Updates the event with the specified ID."""
    # -- Notes:
    # In this function, we chose to keep the registrations even
    # after the event is updated (instead of canceling them),
    # leaving the web app with the opportunity to add a new feature
    # to send an e-mail to users, notifying them about the update.

    event_to_update = session.get(Event, id) # Queries for the corresponding event
    if event_to_update: # If it's found, then the event is updated with the new_event info and then added to db
        event_to_update.title = new_event.title
        event_to_update.description = new_event.description
        event_to_update.date = new_event.date
        event_to_update.location = new_event.location

        # Note: the use of model_validate is not necessary, since we are adding a valid "Event" instance to the DB
        # (it already has an ID).

        session.add(event_to_update) # Adds the updated event to the db (with the corresponding ID)
        session.commit() # Confirms the changes
        return "Event successfully updated"

    else: # Else, a 404 is returned.
        raise HTTPException(status_code=404, detail="Event not found")


@router.delete("/{id}")
def delete_event(
        id: Annotated[int, Path(description="ID of the event to delete")],
        session: SessionDep
):
    """Deletes the event with the specified ID."""
    # Here, we chose to check if an event with the specified ID exists, since when we delete
    # the whole table, we usually do not need to know the previous state of the table (we need
    # to erase it); on the other hand, we would like to know if we are deleting an event that
    # existed previously or not, thus requiring a check.

    event_to_delete = session.get(Event, id)
    if event_to_delete: # If an event is found, then we delete it
        session.delete(event_to_delete)
        session.commit()

        # Now, we need to cancel every registration for the given event.
        statement = delete(Registration).where(Registration.event_id == id) # NOQA
        # With NOQA, we are disabling warnings that are known bugs in type checks with SQLAlchemy (safe to ignore)
        session.exec(statement)
        session.commit()


        return "Event successfully deleted"
    else: # Else return a 404.
        raise HTTPException(status_code=404, detail="Event not found")

