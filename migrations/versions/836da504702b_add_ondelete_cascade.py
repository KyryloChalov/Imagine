"""add ondelete cascade

Revision ID: 836da504702b
Revises: 76383aa9d6ba
Create Date: 2024-03-25 09:22:07.798387

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '836da504702b'
down_revision: Union[str, None] = '76383aa9d6ba'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('comments_photo_id_fkey', 'comments', type_='foreignkey')
    op.drop_constraint('comments_user_id_fkey', 'comments', type_='foreignkey')
    op.create_foreign_key(None, 'comments', 'photos', ['photo_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'comments', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    op.drop_constraint('photos_user_id_fkey', 'photos', type_='foreignkey')
    op.create_foreign_key(None, 'photos', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    op.drop_constraint('ratings_user_id_fkey', 'ratings', type_='foreignkey')
    op.drop_constraint('ratings_photo_id_fkey', 'ratings', type_='foreignkey')
    op.create_foreign_key(None, 'ratings', 'photos', ['photo_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'ratings', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'ratings', type_='foreignkey')
    op.drop_constraint(None, 'ratings', type_='foreignkey')
    op.create_foreign_key('ratings_photo_id_fkey', 'ratings', 'photos', ['photo_id'], ['id'])
    op.create_foreign_key('ratings_user_id_fkey', 'ratings', 'users', ['user_id'], ['id'])
    op.drop_constraint(None, 'photos', type_='foreignkey')
    op.create_foreign_key('photos_user_id_fkey', 'photos', 'users', ['user_id'], ['id'])
    op.drop_constraint(None, 'comments', type_='foreignkey')
    op.drop_constraint(None, 'comments', type_='foreignkey')
    op.create_foreign_key('comments_user_id_fkey', 'comments', 'users', ['user_id'], ['id'])
    op.create_foreign_key('comments_photo_id_fkey', 'comments', 'photos', ['photo_id'], ['id'])
    # ### end Alembic commands ###
