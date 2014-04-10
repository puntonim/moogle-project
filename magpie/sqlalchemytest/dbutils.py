from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from magpie.settings import settings


Base = declarative_base()

def setup_db():
    print("*************************** Creating a new engine")
    Base.metadata.create_all(engine)


def _start_engine():
    # TODO: the only purpose of this function is to print this text
    # I'm printing this text cause I want to monitor how many times the engine is started
    # Later on I can remove this and set directly the module var, like:
    # engine = create_engine(...)
    print("*************************** Creating a new engine")
    return create_engine('sqlite:///test.db')
engine = _start_engine()


Session = sessionmaker(bind=engine)


@contextmanager
def session_autocommit():
    print("*************************** Creating a new session")
    sex = Session()
    try:
        yield sex
        sex.commit()
    except:
        sex.rollback()
        raise
    finally:
        sex.close()

