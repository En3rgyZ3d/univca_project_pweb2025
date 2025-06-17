from sqlmodel import SQLModel, Field

class UserBase(SQLModel): # Common attributes
    name: str
    email: str
    username: str


class User(UserBase,table = True): # Class used for ORM
    username: str = Field(primary_key=True) # Overwrites the username field in UserBase

class UserPublic(UserBase): # Class used to show User data
    pass
class UserCreate(UserBase): # Class used to create a user, imports everything from class UserBase
    pass