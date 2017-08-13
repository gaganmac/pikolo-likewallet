"""empty message

Revision ID: 7e3312fe1899
Revises: b6d7600235cc
Create Date: 2017-08-11 13:29:34.702595

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7e3312fe1899'
down_revision = 'b6d7600235cc'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('auth_influencer')

    


    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('auth_influencer',
    sa.Column('id', sa.VARCHAR(length=64), autoincrement=False, nullable=False),
    sa.Column('handle', sa.VARCHAR(length=128), autoincrement=False, nullable=True),
    sa.Column('token', sa.VARCHAR(length=128), autoincrement=False, nullable=True),
    sa.Column('user_id', sa.VARCHAR(length=64), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['auth_user.id'], name='auth_influencer_user_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='auth_influencer_pkey')
    )
    op.create_table('auth_user',
    sa.Column('id', sa.VARCHAR(length=64), autoincrement=False, nullable=False),
    sa.Column('first', sa.VARCHAR(length=128), autoincrement=False, nullable=True),
    sa.Column('last', sa.VARCHAR(length=128), autoincrement=False, nullable=True),
    sa.Column('company', sa.VARCHAR(length=128), autoincrement=False, nullable=True),
    sa.Column('website', sa.VARCHAR(length=128), autoincrement=False, nullable=True),
    sa.Column('email', sa.VARCHAR(length=128), autoincrement=False, nullable=True),
    sa.Column('phone', sa.VARCHAR(length=12), autoincrement=False, nullable=True),
    sa.Column('password', sa.VARCHAR(length=128), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='auth_user_pkey'),
    sa.UniqueConstraint('email', name='auth_user_email_key')
    )
    # ### end Alembic commands ###
