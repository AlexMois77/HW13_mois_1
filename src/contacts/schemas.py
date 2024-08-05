from datetime import date, datetime
from pydantic import BaseModel, EmailStr
from src.auth.schemas import UserBase


class ContactsBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str
    birthday: date
    additional_info: str | None = None


class ContactsResponse(ContactsBase):
    id: int
    owner: UserBase


class ContactsCreate(ContactsBase):
    pass


# class ContactsUpdate(ContactsBase):
#     done: bool

# class ContactsStatusUpdate(BaseModel):
#     done: bool
