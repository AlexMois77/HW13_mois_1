"""add Roles

Revision ID: 3c5052c02346
Revises: 0e489a840c93
Create Date: 2024-07-28 10:39:46.082993

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import MetaData, Table

from src.auth.models import Role
from src.auth.schemas import RoleEnum


# revision identifiers, used by Alembic.
revision: str = "3c5052c02346"
down_revision: Union[str, None] = "0e489a840c93"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "roles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index(op.f("ix_roles_id"), "roles", ["id"], unique=False)
    op.add_column("users", sa.Column("role_id", sa.Integer(), nullable=True))
    op.create_foreign_key(None, "users", "roles", ["role_id"], ["id"])
    # ### end Alembic commands ###

    op.bulk_insert(
        Role.__table__,
        [
            {
                "name": RoleEnum.USER.value,
            },
            {"name": RoleEnum.ADMIN.value},
        ],
    )


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "users", type_="foreignkey")
    op.drop_column("users", "role_id")
    op.drop_index(op.f("ix_roles_id"), table_name="roles")
    op.drop_table("roles")
    # ### end Alembic commands ###
