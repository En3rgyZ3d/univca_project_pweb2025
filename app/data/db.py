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

            # We need the username (and the email, since it would be secondary key) to be unique,
            # so we track the ones that already come out; if we get a duplicate, we generate
            # a new value.

            fake_usernames = []
            fake_emails = []

            for i in range(10):
                generated_username = f.user_name()
                while generated_username in fake_usernames:
                    generated_username = f.user_name()

                generated_email = f.email()
                while generated_email in fake_emails:
                    generated_email = f.email()

                user = User(
                    username=generated_username,
                    email=generated_email,
                    name=f.name()
                )
                fake_user_list.append(user.username) # Adding the username to the list
                fake_usernames.append(generated_username)
                fake_emails.append(generated_email)
                session.add(user)

            session.commit() # Commits the changes to the db

            # -- Fake Event Data init


            # We check that no duplicate event is created (even though not required by the db structure)

            fake_titles = []
            fake_descriptions = []
            fake_locations = []
            fake_dates = []

            for i in range(10):

                generated_title = f.title(nb_words=5)
                generated_description = f.description(nb_words=20)
                generated_location = f.address()
                generated_date = f.date_time()

                # Checks if duplicates

                while generated_title in fake_titles:
                    generated_title = f.title(nb_words=5)

                while generated_description in fake_descriptions:
                    generated_description = f.description(nb_words=20)

                while generated_location in fake_locations:
                    generated_location = f.address()

                while generated_date in fake_dates:
                    generated_date = f.date_time()

                # Appends to the list

                fake_titles.append(generated_title)
                fake_descriptions.append(generated_description)
                fake_locations.append(generated_location)
                fake_dates.append(generated_date)

                event = Event(
                    title= generated_title,
                    description= generated_description,
                    location= generated_location,
                    date=generated_date
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
