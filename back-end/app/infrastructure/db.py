from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config.settings import settings


Base = declarative_base()

engine = create_engine(
    settings.db_url,
    echo=False,
    future=True,
    connect_args={"connect_timeout": 3},
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def init_db():
    try:
        import app.infrastructure.orm_models  # ensure models are imported
        Base.metadata.create_all(bind=engine)
    except Exception:
        # Allow app to start even if DB is down
        pass