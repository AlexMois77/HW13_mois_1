from config.db import Base
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Role(Base):
    __tablename__ = "roles"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    name: Mapped[str] = mapped_column(String, unique=True)


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String, unique=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String)
    is_active: Mapped[bool] = mapped_column(default=True)
    contacts: Mapped[list["Contact"]] = relationship("Contact", back_populates="owner")
    role_id: Mapped[int] = mapped_column(Integer, ForeignKey("roles.id"), nullable=True)
    role: Mapped["Role"] = relationship("Role", lazy="selectin")
    avatar: Mapped[str] = mapped_column(String, nullable=True)
