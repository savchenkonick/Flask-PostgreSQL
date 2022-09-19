"""empty message

Revision ID: bb968238afbb
Revises: 
Create Date: 2022-09-18 17:39:04.360450

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bb968238afbb'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('courses',
    sa.Column('course_name', sa.String(length=40), nullable=False),
    sa.Column('description', sa.String(length=40), nullable=True),
    sa.PrimaryKeyConstraint('course_name')
    )
    op.create_table('groups',
    sa.Column('group_name', sa.String(length=40), nullable=False),
    sa.PrimaryKeyConstraint('group_name')
    )
    op.create_table('students',
    sa.Column('student_id', sa.Integer(), sa.Identity(always=False), nullable=False),
    sa.Column('group_id', sa.String(length=40), nullable=True),
    sa.Column('first_name', sa.String(length=40), nullable=False),
    sa.Column('last_name', sa.String(length=40), nullable=False),
    sa.PrimaryKeyConstraint('student_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('students')
    op.drop_table('groups')
    op.drop_table('courses')
    # ### end Alembic commands ###