from functools import lru_cache
from fastapi import HTTPException, status
from sqlalchemy import select

from src.auth.models import Role, User
from src.auth.schemas import RoleEnum, UserCreate
from src.auth.pass_utils import get_password_hash


class UserRepository:
    def __init__(self, session):
        self.session = session

    def create_user(self, user_create: UserCreate):
        hashed_password = get_password_hash(user_create.password)
        user_role = RoleRepository(self.session).get_role_by_name(RoleEnum.USER)
        new_user = User(
            username=user_create.username,
            hashed_password=hashed_password,
            email=user_create.email,
            role_id=user_role.id,
            is_active=False,
        )
        self.session.add(new_user)
        self.session.commit()
        self.session.refresh(new_user)  # To get the ID from the database
        return new_user

    def get_user(self, username: str) -> User:
        query = select(User).where(User.username == username)
        result = self.session.execute(query)
        return result.scalar_one_or_none()

    def get_user_by_email(self, email: str) -> User:
        query = select(User).where(User.email == email)
        result = self.session.execute(query)
        return result.scalar_one_or_none()

    def activate_user(self, user: User):
        user.is_active = True
        self.session.add(user)
        self.session.commit()
        self.session.refresh(
            user
        )  # To get the updated is_active value from the database

    def update_avatar(self, email: str, url: str) -> User:
        query = select(User).where(User.email == email)
        result = self.session.execute(query)
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        user.avatar = url
        self.session.commit()
        self.session.refresh(user)
        return user


class RoleRepository:
    def __init__(self, session):
        self.session = session

    @lru_cache
    def get_role_by_name(self, name: RoleEnum):
        query = select(Role).where(Role.name == name.value)
        result = self.session.execute(query)
        return result.scalar_one_or_none()
