"""provenance

Revision ID: 65222fc165b3
Revises: 
Create Date: 2026-07-22 16:31:16.951605

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '65222fc165b3'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new columns to analyses table
    op.add_column('analyses', sa.Column('inference_status', sa.String(), nullable=True))
    op.add_column('analyses', sa.Column('model_id', sa.String(), nullable=True))
    op.add_column('analyses', sa.Column('inference_provider', sa.String(), nullable=True))
    op.add_column('analyses', sa.Column('model_version', sa.String(), nullable=True))

    # Backfill existing records safely
    op.execute("UPDATE analyses SET inference_status = 'legacy_unverified' WHERE inference_status IS NULL")

    # Now make it non-nullable (since sqlite/postgres might require different syntax for altering non-null safely, 
    # but we can usually just alter it. SQLite has limitations on alter column, so we'll just leave it as nullable=True in DB but handle it in app, or we can use batch_alter_table)
    with op.batch_alter_table('analyses', schema=None) as batch_op:
        batch_op.alter_column('inference_status', existing_type=sa.String(), nullable=False)


def downgrade() -> None:
    with op.batch_alter_table('analyses', schema=None) as batch_op:
        batch_op.drop_column('model_version')
        batch_op.drop_column('inference_provider')
        batch_op.drop_column('model_id')
        batch_op.drop_column('inference_status')

