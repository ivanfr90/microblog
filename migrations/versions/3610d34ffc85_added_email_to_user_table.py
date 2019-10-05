"""added email to user table

Revision ID: 3610d34ffc85
Revises: 775285fe6c46
Create Date: 2019-10-02 23:48:09.593544

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3610d34ffc85'
down_revision = '775285fe6c46'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('email', sa.String(length=120), nullable=True))
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_column('user', 'email')
    # ### end Alembic commands ###
