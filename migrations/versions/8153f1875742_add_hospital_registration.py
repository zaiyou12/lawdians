"""add hospital registration

Revision ID: 8153f1875742
Revises: f970056fd50f
Create Date: 2017-06-15 12:43:37.375836

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8153f1875742'
down_revision = 'f970056fd50f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('hospital_registration',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=64), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('doctor', sa.String(length=8), nullable=True),
    sa.Column('address', sa.String(length=64), nullable=True),
    sa.Column('phone', sa.String(length=32), nullable=True),
    sa.Column('requests', sa.Text(), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_hospital_registration_email'), 'hospital_registration', ['email'], unique=True)
    op.create_index(op.f('ix_hospital_registration_timestamp'), 'hospital_registration', ['timestamp'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_hospital_registration_timestamp'), table_name='hospital_registration')
    op.drop_index(op.f('ix_hospital_registration_email'), table_name='hospital_registration')
    op.drop_table('hospital_registration')
    # ### end Alembic commands ###