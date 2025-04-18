"""Add fields for learning paths and insights

Revision ID: 7cf2d35add5
Revises: 
Create Date: 2025-04-18 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '7cf2d35add5'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add learning_goal to users table
    op.add_column('users', sa.Column('learning_goal', sa.String(), nullable=True))
    
    # Add topics and difficulty_score to legal_sections table
    op.add_column('legal_sections', sa.Column('topics', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('legal_sections', sa.Column('difficulty_score', sa.Float(), nullable=True))
    
    # Add topic_tags and difficulty_rating to mcq_questions table
    op.add_column('mcq_questions', sa.Column('topic_tags', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('mcq_questions', sa.Column('difficulty_rating', sa.Integer(), nullable=True))


def downgrade() -> None:
    # Remove columns from mcq_questions table
    op.drop_column('mcq_questions', 'difficulty_rating')
    op.drop_column('mcq_questions', 'topic_tags')
    
    # Remove columns from legal_sections table
    op.drop_column('legal_sections', 'difficulty_score')
    op.drop_column('legal_sections', 'topics')
    
    # Remove column from users table
    op.drop_column('users', 'learning_goal')