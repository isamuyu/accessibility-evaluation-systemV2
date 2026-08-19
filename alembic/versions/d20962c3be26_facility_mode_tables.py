"""facility mode tables

Revision ID: d20962c3be26
Revises: 8310bfe77804
Create Date: 2026-08-17 18:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'd20962c3be26'
down_revision = '8310bfe77804'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'facility_mode_categories',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('category_code', sa.String(30), unique=True, nullable=False),
        sa.Column('category_name', sa.String(100), nullable=False),
        sa.Column('facility_category_code', sa.String(20)),
        sa.Column('sort_order', sa.Integer(), default=0),
        sa.Column('is_active', sa.Boolean(), default=True),
    )
    op.create_table(
        'facility_mode_clauses',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('clause_number', sa.String(80), unique=True, nullable=False),
        sa.Column('standard_clause_number', sa.String(50)),
        sa.Column('category_code', sa.String(30), sa.ForeignKey('facility_mode_categories.category_code'), nullable=False),
        sa.Column('chapter', sa.Enum('Q1', 'Q2', 'Q3', 'Q4', 'Q5', 'CONSTRUCTION', 'MAINTENANCE', 'CONTROL', name='chapter'), nullable=False),
        sa.Column('clause_type', sa.String(20), nullable=False),
        sa.Column('title', sa.String(200)),
        sa.Column('content', sa.Text()),
        sa.Column('max_score', sa.DECIMAL(5, 2), default=0),
        sa.Column('score_type', sa.String(20), nullable=False),
        sa.Column('score_options', sa.JSON()),
        sa.Column('sort_order', sa.Integer(), default=0),
        sa.Column('is_active', sa.Boolean(), default=True),
    )
    op.create_table(
        'facility_mode_instances',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('building_id', sa.String(36), sa.ForeignKey('buildings.id'), nullable=False),
        sa.Column('category_code', sa.String(30), sa.ForeignKey('facility_mode_categories.category_code'), nullable=False),
        sa.Column('instance_name', sa.String(200), nullable=False),
        sa.Column('location', sa.Text()),
        sa.Column('sort_order', sa.Integer(), default=0),
        sa.Column('mapped_facility_id', sa.String(36), sa.ForeignKey('facility_entities.id')),
        sa.Column('created_at', sa.DateTime()),
    )
    op.create_table(
        'facility_mode_checks',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('instance_id', sa.String(36), sa.ForeignKey('facility_mode_instances.id'), nullable=False),
        sa.Column('clause_id', sa.String(36), sa.ForeignKey('facility_mode_clauses.id'), nullable=False),
        sa.Column('status', sa.String(10), default='pending'),
        sa.Column('selected_option', sa.JSON()),
        sa.Column('auto_score', sa.DECIMAL(5, 2), default=0),
        sa.Column('notes', sa.Text()),
        sa.Column('checked_at', sa.DateTime()),
        sa.UniqueConstraint('instance_id', 'clause_id', name='uq_fm_check_instance_clause'),
    )


def downgrade() -> None:
    op.drop_table('facility_mode_checks')
    op.drop_table('facility_mode_instances')
    op.drop_table('facility_mode_clauses')
    op.drop_table('facility_mode_categories')
