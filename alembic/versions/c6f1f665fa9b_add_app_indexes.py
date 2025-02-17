"""add app indexes

Revision ID: c6f1f665fa9b
Revises: 50fb707438ff
Create Date: 2025-02-14 15:57:20.398438

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'c6f1f665fa9b'
down_revision: Union[str, None] = '50fb707438ff'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_index('idx_apps_category_free', 'apps', ['category_id', 'is_free'], 
                    unique=False, 
                    postgresql_include=[
                    'id',
                    'name',
                    'app_id',
                    'rating',
                    'rating_count',
                    'installs',
                    'price',
                    'released_date',
                    'last_updated',
                    'content_rating',
                    'developer_id'])
    op.create_index('idx_apps_category_rating', 'apps', ['category_id', 'rating'], unique=False)
    op.create_index('idx_apps_yearly_stats', 'apps', ['category_id', 'released_date', 'last_updated'], unique=False)


def downgrade() -> None:
    op.drop_index('idx_apps_yearly_stats', table_name='apps')
    op.drop_index('idx_apps_category_free', table_name='apps', postgresql_include=[
                    'id',
                    'name',
                    'app_id',
                    'rating',
                    'rating_count',
                    'installs',
                    'price',
                    'released_date',
                    'last_updated',
                    'content_rating',
                    'developer_id'])
    op.drop_index('idx_apps_category_rating', table_name='apps')
    # op.drop_index('idx_apps_category_cover', table_name='apps', postgresql_include=['name', 'app_id', 'is_free', 'rating_count', 'has_ads', 'is_editors_choice', 'released_date'])
