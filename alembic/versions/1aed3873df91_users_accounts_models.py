"""users, accounts models

Revision ID: 1aed3873df91
Revises: 5076d647819b
Create Date: 2015-05-06 21:51:50.168057

"""

# revision identifiers, used by Alembic.
revision = '1aed3873df91'
down_revision = '5076d647819b'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('login', sa.String(length=64), nullable=True),
    sa.Column('password', sa.String(length=128), nullable=True),
    sa.Column('email', sa.String(length=255), nullable=True),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.Column('cdate', sa.DateTime(), nullable=True),
    sa.Column('mdate', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('login')
    )
    op.create_table('account_type',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=False),
    sa.Column('group', sa.Integer(), nullable=False),
    sa.Column('order', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('account',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('account_type_id', sa.String(length=36), nullable=False),
    sa.Column('user_id', sa.String(length=36), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=False),
    sa.Column('initial_balance', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('debit_limit', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.Column('cdate', sa.DateTime(), nullable=False),
    sa.Column('mdate', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['account_type_id'], ['account_type.id'], ondelete='cascade'),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='cascade'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('account')
    op.drop_table('account_type')
    op.drop_table('user')
    ### end Alembic commands ###
