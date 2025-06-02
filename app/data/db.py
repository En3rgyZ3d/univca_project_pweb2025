from sqlmodel import create_engine, SQLModel, Session, select
from typing import Annotated
from fastapi import Depends
import os
from faker import Faker

from app.config import config
from app.models.registration import Registration
from app.models.user import User
from app.models.event import Event

sqlite_file_name = config.root_dir / "data/database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args, echo=True)


def init_database() -> None:
    ds_exists = os.path.isfile(sqlite_file_name)
    SQLModel.metadata.create_all(engine)
    if not ds_exists:
        f = Faker("it_IT")
        with Session(engine) as session:

            # -- Fake User Data init

            fake_user_list = [] # We'll use this to create fake (but valid) registration data
            for i in range(10):
                user = User(
                    username=f.user_name(),
                    email=f.email(),
                    name=f.name()
                )
                fake_user_list.append(user.username) # Adding the username to the list
                session.add(user)
            session.commit() # Commits the changes to the db

            # -- Fake Event Data init

            for i in range(10):
                event = Event(
                    title= f.sentence(nb_words=5),
                    description= f.sentence(nb_words=20),
                    location= f.address(),
                    date=f.date_time()
                )
                session.add(event)
            session.commit()

            # -- Fake Registration Data init

            numbers_generated = [] # Empty list to check if a given combination already exists
            # Since the combination of username and event_id in Registration is primary key of the registration table,
            # the registrations must be unique; so, we need to check if a given combination already appeared
            # while initialising the database.

            for i in range(10):
                # If the combination already exists, then a new combination is generated
                random_numbers = (f.pyint(0, 9), f.pyint(0, 9))
                while random_numbers in numbers_generated:
                    random_numbers = (f.pyint(0, 9), f.pyint(0, 9))

                numbers_generated.append(random_numbers) # Once the combination is created, we add it to the list

                event_registration = Registration(
                    username=fake_user_list[random_numbers[0]], # Random user in the list
                    event_id = random_numbers[1] # Random event between the ones created
                )
                session.add(event_registration)
            session.commit()



def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
