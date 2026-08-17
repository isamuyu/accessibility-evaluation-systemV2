"""add is_scored to score details

Revision ID: a71630119f18
Revises: d021ec5e0e7b
Create Date: 2026-08-10 16:20:00.000000

已有数据迁移规则：actual_score > 0 的视为已评分，其余为未评分。
"""
from alembic import op
import sqlalchemy as sa


revision = 'a71630119f18'
down_revision = 'd021ec5e0e7b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table('system_score_details') as batch_op:
        batch_op.add_column(sa.Column('is_scored', sa.Boolean(), nullable=True))
    with op.batch_alter_table('facility_score_details') as batch_op:
        batch_op.add_column(sa.Column('is_scored', sa.Boolean(), nullable=True))

    # 已有数据：得过分的标记为已评分，0分的视为未评分
    op.execute("UPDATE system_score_details SET is_scored = 1 WHERE actual_score > 0")
    op.execute("UPDATE system_score_details SET is_scored = 0 WHERE is_scored IS NULL")
    op.execute("UPDATE facility_score_details SET is_scored = 1 WHERE actual_score > 0")
    op.execute("UPDATE facility_score_details SET is_scored = 0 WHERE is_scored IS NULL")


def downgrade() -> None:
    with op.batch_alter_table('system_score_details') as batch_op:
        batch_op.drop_column('is_scored')
    with op.batch_alter_table('facility_score_details') as batch_op:
        batch_op.drop_column('is_scored')
