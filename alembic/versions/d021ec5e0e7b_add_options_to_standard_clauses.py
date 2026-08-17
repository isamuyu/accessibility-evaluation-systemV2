"""add options to standard_clauses

Revision ID: d021ec5e0e7b
Revises: a21a66e08175
Create Date: 2026-08-10 15:46:49.623343

"""
from alembic import op
import sqlalchemy as sa


revision = 'd021ec5e0e7b'
down_revision = 'a21a66e08175'
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table('standard_clauses') as batch_op:
        batch_op.add_column(sa.Column('options', sa.JSON(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table('standard_clauses') as batch_op:
        batch_op.drop_column('options')
