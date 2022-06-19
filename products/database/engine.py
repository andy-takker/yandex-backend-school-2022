from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import get_settings
from database.base import Base

settings = get_settings()
engine = create_engine(url=settings.SQLALCHEMY_DATABASE_URI)

Session = sessionmaker(autoflush=False, autocommit=False, bind=engine)


def get_session():
    """For Dependsy Injection"""
    session = None
    try:
        session = Session()
        yield session
    finally:
        if session is not None:
            if session is not None:
                session.close()


def create_db():
    Base.metadata.create_all(engine)
