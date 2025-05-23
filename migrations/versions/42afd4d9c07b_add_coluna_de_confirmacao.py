"""add coluna de confirmacao

Revision ID: 42afd4d9c07b
Revises: 
Create Date: 2025-04-21 09:06:36.540106

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '42afd4d9c07b'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('reserved_gifts', schema=None) as batch_op:
        batch_op.add_column(sa.Column('confirmed', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('confirmation_token', sa.String(length=100), nullable=True))
        batch_op.create_unique_constraint(None, ['confirmation_token'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('reserved_gifts', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='unique')
        batch_op.drop_column('confirmation_token')
        batch_op.drop_column('confirmed')

    # ### end Alembic commands ###
