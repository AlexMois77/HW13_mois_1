from datetime import datetime, timedelta
from sqlalchemy import extract, or_, select, update

from src.contacts.models import Contact
from src.contacts.schemas import ContactsCreate


class ContactsRepository:
    def __init__(self, session):
        self.session = session

    def get_contacts(self, owner_id, limit: int = 10, offset: int = 0):
        query = (
            select(Contact)
            .where(Contact.owner_id == owner_id)
            .limit(limit)
            .offset(offset)
        )
        results = self.session.execute(query)
        return results.scalars().all()

    def get_contacts_all(self, limit: int = 10, offset: int = 0):
        query = select(Contact).limit(limit).offset(offset)
        results = self.session.execute(query)
        return results.scalars().all()

    def create_contacts(self, contact: ContactsCreate, owner_id: int):
        new_contact = Contact(**contact.model_dump(), owner_id=owner_id)
        self.session.add(new_contact)
        self.session.commit()
        self.session.refresh(new_contact)  # To get the ID from the database
        return new_contact

    def search_contacts(self, owner_id, query):
        q = (
            select(Contact)
            .where(Contact.owner_id == owner_id)
            .filter(
                (Contact.first_name.ilike(f"%{query}%"))
                | (Contact.last_name.ilike(f"%{query}%"))
                | (Contact.email.ilike(f"%{query}%"))
            )
        )
        results = self.session.execute(q)
        return results.scalars().all()

    def get_contact_by_id_and_owner(self, owner_id: int, contact_id: int):
        q = select(Contact).where(
            Contact.owner_id == owner_id, Contact.id == contact_id
        )
        result = self.session.execute(q)
        return result.scalar_one_or_none()

    def get_contact_by_id(self, contact_id: int):
        query = select(Contact).where(Contact.id == contact_id)
        result = self.session.execute(query)
        return result.scalar_one_or_none()

    def delete_contact(self, contact_id: int):
        contact = self.session.get(Contact, contact_id)
        if contact:
            self.session.delete(contact)
            self.session.commit()

    def get_upcoming_birthdays(self, owner_id: int, days: int = 7):
        today = datetime.today()
        upcoming_date = today + timedelta(days=days)
        today_day_of_year = today.timetuple().tm_yday
        upcoming_day_of_year = upcoming_date.timetuple().tm_yday

        if today_day_of_year <= upcoming_day_of_year:
            query = select(Contact).filter(
                Contact.owner_id == owner_id,
                extract("doy", Contact.birthday).between(
                    today_day_of_year, upcoming_day_of_year
                ),
            )
        else:
            query = select(Contact).filter(
                Contact.owner_id == owner_id,
                or_(
                    extract("doy", Contact.birthday) >= today_day_of_year,
                    extract("doy", Contact.birthday) <= upcoming_day_of_year,
                ),
            )

        results = self.session.execute(query)
        return results.scalars().all()

    def find_contact(self, owner_id: int, identifier: str):
        try:
            contact_id = int(identifier)
        except ValueError:
            contact_id = None

        query = select(Contact).where(
            Contact.owner_id == owner_id,
            or_(
                Contact.id == contact_id,
                Contact.email == identifier,
                Contact.first_name == identifier,
                (Contact.first_name + " " + Contact.last_name) == identifier,
            ),
        )
        result = self.session.execute(query)
        return result.scalar_one_or_none()

    def update_contact(
        self, identifier: str, owner_id: int, contact_update: ContactsCreate
    ):
        contact = self.find_contact(owner_id, identifier)
        if not contact:
            return None

        if contact_update.email:
            existing_contact = self.session.execute(
                select(Contact).where(Contact.email == contact_update.email)
            ).scalar_one_or_none()
            if existing_contact and existing_contact.id != contact.id:
                raise ValueError("Email already in use")

        stmt = (
            update(Contact)
            .where(Contact.id == contact.id)
            .values(contact_update.model_dump(exclude_unset=True))
            .returning(Contact)
        )
        result = self.session.execute(stmt)
        self.session.commit()
        updated_contact = result.scalar()
        return updated_contact
