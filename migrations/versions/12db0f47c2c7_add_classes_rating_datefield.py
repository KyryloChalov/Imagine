"""add Classes Rating Datefield

Revision ID: 12db0f47c2c7
Revises: 6b9e733b374b
Create Date: 2024-03-23 09:42:20.624487

"""
from typing import Sequence, Union

from alembic import op
import fastapi_users_db_sqlalchemy
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '12db0f47c2c7'
down_revision: Union[str, None] = '6b9e733b374b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('ratings',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('rating', sa.Integer(), nullable=False),
    sa.Column('photo_id', sa.Integer(), nullable=False),
    sa.Column('user_id', fastapi_users_db_sqlalchemy.generics.GUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['photo_id'], ['photos.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.alter_column('comments', 'user_id',
               existing_type=sa.UUID(),
               nullable=False)
    op.alter_column('comments', 'photo_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.drop_column('comments', 'rating')
    op.add_column('photos', sa.Column('updated_at', sa.DateTime(), nullable=False))
    op.alter_column('photos', 'user_id',
               existing_type=sa.UUID(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('photos', 'user_id',
               existing_type=sa.UUID(),
               nullable=True)
    op.drop_column('photos', 'updated_at')
    op.add_column('comments', sa.Column('rating', sa.INTEGER(), autoincrement=False, nullable=False))
    op.alter_column('comments', 'photo_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column('comments', 'user_id',
               existing_type=sa.UUID(),
               nullable=True)
    op.drop_table('ratings')
    # ### end Alembic commands ###
