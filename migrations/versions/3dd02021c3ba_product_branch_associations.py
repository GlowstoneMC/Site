"""Product-branch associations (Part 1)

Revision ID: 3dd02021c3ba
Revises: 95c3b9f7ca89
Create Date: 2017-06-25 17:08:44.945195

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '3dd02021c3ba'
down_revision = '95c3b9f7ca89'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column('product', 'branches')
    op.drop_table('product_branch')


def downgrade():
    print("This downgrade misses a table creation - please run the migration before it.")
    op.add_column('product', sa.Column('branches', postgresql.ARRAY(sa.INTEGER()), autoincrement=False, nullable=True))
