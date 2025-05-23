from sqlmodel import SQLModel, Field

class UserBase(SQLModel): # Common attributes
    name: str
    email: str

class User(UserBase,table = True): # Class used for ORM
    username: str = Field(primary_key=True)

class UserPublic(UserBase): # Class used to show User data
    username: str

class UserCreate(User): # Class used to create a user, imports everything from class User
    pass