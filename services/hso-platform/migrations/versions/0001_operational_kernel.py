"""Initial HSO operational kernel schema.

Revision ID: 0001_operational_kernel
Revises:
"""
from alembic import op

from hso_platform.models import Base

revision = "0001_operational_kernel"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Bootstrap migration for the initial schema. Later model changes must use
    # explicit Alembic revisions and must not silently rely on create_all.
    Base.metadata.create_all(bind=op.get_bind())


def downgrade() -> None:
    Base.metadata.drop_all(bind=op.get_bind())
