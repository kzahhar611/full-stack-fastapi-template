"""Add RFP Analysis tables for Module 1

Revision ID: 001_add_rfp_analysis_tables
Revises: 
Create Date: 2025-01-03 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_add_rfp_analysis_tables'
down_revision = None
head = None
branch_labels = None
depends_on = None


def upgrade():
    # Create enum types
    analysis_status_enum = postgresql.ENUM(
        'PENDING', 'IN_PROGRESS', 'COMPLETED', 'FAILED',
        name='analysisstatus'
    )
    analysis_status_enum.create(op.get_bind())
    
    decision_type_enum = postgresql.ENUM(
        'GO', 'NO_GO', 'CONDITIONAL', 'NEEDS_REVIEW',
        name='decisiontype'
    )
    decision_type_enum.create(op.get_bind())
    
    risk_level_enum = postgresql.ENUM(
        'LOW', 'MEDIUM', 'HIGH', 'CRITICAL',
        name='risklevel'
    )
    risk_level_enum.create(op.get_bind())

    # Create rfp_analyses table
    op.create_table(
        'rfp_analyses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('uuid', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('analysis_id', sa.String(length=100), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('status', analysis_status_enum, nullable=False),
        sa.Column('company_context', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('analysis_parameters', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('decision', decision_type_enum, nullable=True),
        sa.Column('confidence_score', sa.Numeric(precision=5, scale=4), nullable=True),
        sa.Column('primary_justification', sa.Text(), nullable=True),
        sa.Column('detailed_reasoning', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('risk_factors', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('success_factors', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('conditions', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('estimated_win_probability', sa.Numeric(precision=5, scale=4), nullable=True),
        sa.Column('overall_risk_level', risk_level_enum, nullable=True),
        sa.Column('risk_score', sa.Numeric(precision=4, scale=2), nullable=True),
        sa.Column('technical_risks', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('commercial_risks', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('operational_risks', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('legal_risks', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('mitigation_strategies', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('project_complexity', sa.String(length=20), nullable=True),
        sa.Column('estimated_duration_months', sa.Integer(), nullable=True),
        sa.Column('estimated_cost_range', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('technology_stack', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('required_team_size', sa.Integer(), nullable=True),
        sa.Column('key_success_factors', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('competitive_advantages', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('potential_challenges', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('kpi_dashboard', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('strategic_score', sa.Numeric(precision=5, scale=4), nullable=True),
        sa.Column('complexity_score', sa.Numeric(precision=5, scale=4), nullable=True),
        sa.Column('raw_analysis', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('strategic_analysis', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('retry_count', sa.Integer(), nullable=False),
        sa.Column('analysis_duration_seconds', sa.Integer(), nullable=True),
        sa.Column('rfp_id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('created_by_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.ForeignKeyConstraint(['rfp_id'], ['rfps.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_rfp_analyses_analysis_id'), 'rfp_analyses', ['analysis_id'], unique=True)
    op.create_index(op.f('ix_rfp_analyses_uuid'), 'rfp_analyses', ['uuid'], unique=True)

    # Create decision_history table
    op.create_table(
        'decision_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('uuid', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('previous_decision', decision_type_enum, nullable=True),
        sa.Column('new_decision', decision_type_enum, nullable=False),
        sa.Column('reason_for_change', sa.Text(), nullable=False),
        sa.Column('reviewer_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('analysis_id', sa.Integer(), nullable=False),
        sa.Column('reviewer_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['analysis_id'], ['rfp_analyses.id'], ),
        sa.ForeignKeyConstraint(['reviewer_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_decision_history_uuid'), 'decision_history', ['uuid'], unique=True)

    # Create analysis_templates table
    op.create_table(
        'analysis_templates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('uuid', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('industry', sa.String(length=100), nullable=True),
        sa.Column('company_size', sa.String(length=50), nullable=True),
        sa.Column('analysis_criteria', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('risk_weights', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('decision_thresholds', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('is_default', sa.Boolean(), nullable=False),
        sa.Column('usage_count', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('created_by_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_analysis_templates_uuid'), 'analysis_templates', ['uuid'], unique=True)


def downgrade():
    # Drop tables
    op.drop_table('analysis_templates')
    op.drop_table('decision_history')
    op.drop_table('rfp_analyses')
    
    # Drop enum types
    op.execute('DROP TYPE IF EXISTS analysisstatus')
    op.execute('DROP TYPE IF EXISTS decisiontype')
    op.execute('DROP TYPE IF EXISTS risklevel')