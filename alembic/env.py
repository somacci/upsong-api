import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config, pool

# src/를 path에 추가하여 프로젝트 모듈 임포트 보장
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from core.config import settings
from models.base import Base
import models.user  # noqa: F401 — autogenerate 테이블 탐지용

config = context.config
# 대상 DB: 코드에서 호출할 때 config.attributes["database_url"]로 지정 가능 (테스트 등),
# 없으면 앱 설정(.env.local)의 DATABASE_URL 사용
database_url = config.attributes.get("database_url") or settings.database_url
# Alembic은 동기 드라이버 사용 (asyncpg → psycopg2로 치환)
sync_url = database_url.replace("postgresql+asyncpg", "postgresql+psycopg2")
# ini 보간(%) 충돌 방지를 위해 %는 %%로 이스케이프
config.set_main_option("sqlalchemy.url", sync_url.replace("%", "%%"))

# 코드에서 호출할 때는 호출 측 로깅 설정을 덮어쓰지 않도록 configure_logger=False 지원
if config.config_file_name is not None and config.attributes.get("configure_logger", True):
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
