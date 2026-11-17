"""create user table

Revision ID: 5bdde01a24a7
Revises:
Create Date: 2026-10-26 17:39:43.169696

빈 DB에서 user 테이블 전체를 생성하는 최초 마이그레이션.
(기존에는 이미 존재하던 user 테이블에 컬럼만 추가하는 내용이었으나,
 빈 DB에서 `alembic upgrade head`가 동작하도록 테이블 생성으로 재작성.
 이 리비전이 이미 적용된 DB는 최종 스키마가 동일하므로 영향 없음.)
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5bdde01a24a7'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'user',
        sa.Column('id', sa.Integer(), sa.Identity(always=False), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('phone', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id', name='user_pkey'),
    )
    op.create_index('ix_user_email', 'user', ['email'], unique=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_user_email', table_name='user')
    op.drop_table('user')
