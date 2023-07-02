"""add user tokens

Revision ID: 1e8f932da163
Revises: cb1154cc05de
Create Date: 2023-07-02 12:20:36.557782

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1e8f932da163'
down_revision = 'cb1154cc05de'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    # with op.batch_alter_table('accounts_table', schema=None) as batch_op:
        # batch_op.drop_constraint(None, type_='foreignkey')
        # batch_op.drop_constraint(None, type_='foreignkey')

    with op.batch_alter_table('transactions_table', schema=None) as batch_op:
        batch_op.alter_column('receiver',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.alter_column('sender',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.create_foreign_key(batch_op.f('fk_transactions_table_receiver_accounts_table'), 'accounts_table', ['receiver'], ['account_num'])
        batch_op.create_foreign_key(batch_op.f('fk_transactions_table_sender_accounts_table'), 'accounts_table', ['sender'], ['account_num'])

    with op.batch_alter_table('users_table', schema=None) as batch_op:
        batch_op.add_column(sa.Column('token', sa.String(length=32), nullable=True))
        batch_op.add_column(sa.Column('token_expiration', sa.DateTime(), nullable=True))
        batch_op.create_index(batch_op.f('ix_users_table_token'), ['token'], unique=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users_table', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_users_table_token'))
        batch_op.drop_column('token_expiration')
        batch_op.drop_column('token')

    with op.batch_alter_table('transactions_table', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('fk_transactions_table_sender_accounts_table'), type_='foreignkey')
        batch_op.drop_constraint(batch_op.f('fk_transactions_table_receiver_accounts_table'), type_='foreignkey')
        batch_op.alter_column('sender',
               existing_type=sa.INTEGER(),
               nullable=True)
        batch_op.alter_column('receiver',
               existing_type=sa.INTEGER(),
               nullable=True)

    with op.batch_alter_table('accounts_table', schema=None) as batch_op:
        batch_op.create_foreign_key(None, 'transactions_table', ['account_num'], ['receiver'])
        batch_op.create_foreign_key(None, 'transactions_table', ['account_num'], ['sender'])

    # ### end Alembic commands ###
