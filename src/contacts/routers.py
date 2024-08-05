from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi_limiter.depends import RateLimiter

from src.auth.schemas import RoleEnum
from src.auth.models import User
from src.auth.utils import RoleChecker, get_current_user
from config.db import get_db
from src.contacts.repo import ContactsRepository
from src.contacts.schemas import ContactsCreate, ContactsResponse

router = APIRouter()


@router.get("/ping")
def hello():
    return {"message": "pong"}


@router.post(
    "/",
    response_model=ContactsResponse,
    dependencies=[
        Depends(RoleChecker([RoleEnum.USER, RoleEnum.ADMIN])),
        Depends(RateLimiter(times=10, seconds=60)),
    ],
    status_code=status.HTTP_201_CREATED,
)
def create_contacts(
    contact: ContactsCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repo = ContactsRepository(db)
    return repo.create_contacts(contact, current_user.id)


@router.get(
    "/",
    response_model=list[ContactsResponse],
    dependencies=[
        Depends(RoleChecker([RoleEnum.USER, RoleEnum.ADMIN])),
        Depends(RateLimiter(times=10, seconds=60)),
    ],
)
def get_contacts(
    limit: int = 10,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repo = ContactsRepository(db)
    return repo.get_contacts(current_user.id, limit, offset)


@router.get(
    "/all/",
    response_model=list[ContactsResponse],
    dependencies=[
        Depends(RoleChecker([RoleEnum.ADMIN])),
        Depends(RateLimiter(times=10, seconds=60)),
    ],
    tags=["admin"],
)
def get_contacts_all(
    limit: int = 10,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    repo = ContactsRepository(db)
    return repo.get_contacts_all(limit, offset)


@router.get(
    "/search/",
    response_model=list[ContactsResponse],
    dependencies=[
        Depends(RoleChecker([RoleEnum.USER, RoleEnum.ADMIN])),
        Depends(RateLimiter(times=10, seconds=60)),
    ],
)
def search_contacts(
    query: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repo = ContactsRepository(db)
    return repo.search_contacts(current_user.id, query)


@router.delete("/{contact_id}", dependencies=[Depends(RoleChecker([RoleEnum.ADMIN]))])
def delete_contact(
    contact_id: int,
    db: Session = Depends(get_db),
):
    repo = ContactsRepository(db)
    contact = repo.get_contact_by_id(contact_id)
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    repo.delete_contact(contact_id)
    return {"message": f"Contact {contact_id} deleted"}


@router.get("/upcoming_birthdays/")
def get_upcoming_birthdays(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    days: int = 7,
):
    repo = ContactsRepository(db)
    return repo.get_upcoming_birthdays(current_user.id, days)


@router.put("/{identifier}", response_model=ContactsResponse)
def update_contact(
    identifier: str,
    contact_update: ContactsCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    repo = ContactsRepository(db)
    updated_contact = repo.update_contact(identifier, current_user.id, contact_update)
    if updated_contact:
        return updated_contact
    else:
        raise HTTPException(status_code=404, detail="Contact not found")
