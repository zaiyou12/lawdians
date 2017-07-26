"""add image table

Revision ID: 381876ac07d7
Revises: d18f4807469c
Create Date: 2017-07-26 15:11:34.027563

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '381876ac07d7'
down_revision = 'd18f4807469c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('uploaded_images',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('filename', sa.String(), nullable=True),
    sa.Column('service_id', sa.Integer(), nullable=True),
    sa.Column('event_id', sa.Integer(), nullable=True),
    sa.Column('ad_id', sa.Integer(), nullable=True),
    sa.Column('hospital_id', sa.Integer(), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['ad_id'], ['hospital_ads.id'], ),
    sa.ForeignKeyConstraint(['event_id'], ['events.id'], ),
    sa.ForeignKeyConstraint(['hospital_id'], ['hospitals.id'], ),
    sa.ForeignKeyConstraint(['service_id'], ['services.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_uploaded_images_timestamp'), 'uploaded_images', ['timestamp'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_uploaded_images_timestamp'), table_name='uploaded_images')
    op.drop_table('uploaded_images')
    # ### end Alembic commands ###
