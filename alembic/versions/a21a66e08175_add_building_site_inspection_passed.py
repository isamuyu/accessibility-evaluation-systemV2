"""add building site_inspection_passed

Revision ID: a21a66e08175
Revises: d779360607f4
Create Date: 2026-07-28 16:48:20.005119

SQLite 不支持 ALTER 约束，使用 batch 模式（copy-and-move）重建相关表。
"""
from alembic import op
import sqlalchemy as sa


revision = 'a21a66e08175'
down_revision = 'd779360607f4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table('buildings') as batch_op:
        batch_op.add_column(sa.Column('site_inspection_passed', sa.Boolean(), nullable=True))

    with op.batch_alter_table('control_item_checks') as batch_op:
        batch_op.create_unique_constraint('uq_control_item_building_clause', ['building_id', 'clause_id'])

    with op.batch_alter_table('system_score_details') as batch_op:
        batch_op.create_unique_constraint('uq_system_score_building_clause', ['building_id', 'clause_id'])

    with op.batch_alter_table('facility_score_details') as batch_op:
        batch_op.create_unique_constraint('uq_facility_score_facility_clause', ['facility_id', 'clause_id'])

    with op.batch_alter_table('standard_clauses') as batch_op:
        batch_op.create_unique_constraint('uq_standard_clause_number', ['clause_number'])


def downgrade() -> None:
    with op.batch_alter_table('standard_clauses') as batch_op:
        batch_op.drop_constraint('uq_standard_clause_number', type_='unique')

    with op.batch_alter_table('facility_score_details') as batch_op:
        batch_op.drop_constraint('uq_facility_score_facility_clause', type_='unique')

    with op.batch_alter_table('system_score_details') as batch_op:
        batch_op.drop_constraint('uq_system_score_building_clause', type_='unique')

    with op.batch_alter_table('control_item_checks') as batch_op:
        batch_op.drop_constraint('uq_control_item_building_clause', type_='unique')

    with op.batch_alter_table('buildings') as batch_op:
        batch_op.drop_column('site_inspection_passed')
