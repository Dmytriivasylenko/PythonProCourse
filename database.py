import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker


engine = create_engine("sqlite:///db.db")
#engine = f'postgresql+psycopg2://postgres:example@{os.environ.get("DB_HOST", "localhost")}:5432'

db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


def init_db():
    import models
    Base.metadata.create_all(bind=engine)

# import all modules here that might define models so that
# they will be registered properly on the metadata.  Otherwise
# you will have to import them first before calling init_db()
