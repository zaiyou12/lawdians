"""add hit, medal Column in Hospital

Revision ID: 053f1d45fbfe
Revises: 41ebf94a66a3
Create Date: 2017-07-20 23:28:03.089739

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '053f1d45fbfe'
down_revision = '41ebf94a66a3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('hospitals', sa.Column('has_medal_1', sa.Boolean(), nullable=True))
    op.add_column('hospitals', sa.Column('has_medal_2', sa.Boolean(), nullable=True))
    op.add_column('hospitals', sa.Column('hits', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('hospitals', 'hits')
    op.drop_column('hospitals', 'has_medal_2')
    op.drop_column('hospitals', 'has_medal_1')
    # ### end Alembic commands ###