from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import json

from magpie.settings import settings


def setup_db():
    # TODO printing this in order to monitor how many times this happens
    print("*************************** Setup the db")
    from .models import Base
    Base.metadata.create_all(engine)


def _start_engine():
    # TODO the only purpose of this function is to print this text
    # I'm printing this text cause I want to monitor how many times the engine is started
    # Later on I can remove this and set directly the module var, like:
    # engine = create_engine(...)
    print("*************************** Creating a new engine")
    return create_engine('{}{}'.format(settings.DATABASE['ENGINE'],
                                              settings.DATABASE['NAME']),)
engine = _start_engine()


Session = sessionmaker(bind=engine)


@contextmanager
def session_autocommit():
    # TODO printing this in order to monitor how many times this happens
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


def get_all_models_classes():
    """
    Return a list of all models classes in `crawler.models`
    """

    # TODO should be improved in order to search all models, not only `crawler.models`

    from inspect import getmembers
    import crawlers.models as models

    def is_Base_subclass(cls):
        """
        Check whether a class is subclass of `Base`.
        Where `Base` is the declarative base from SQLAlchemy, like:
        $ from sqlalchemy.ext.declarative import declarative_base
        $ Base = declarative_base()
        """
        try:
            if issubclass(cls, models.Base):
                return cls != models.Base  # we skip Base itself
        except Exception:
            return False

    # Inspect `crawler.models` and get all classes that are subclass of `Base`.
    # Returns a sequence of tuple, where each tuple is like: ('name of class', <actual class obj>)
    classes = getmembers(models, is_Base_subclass)

    # Return a list of class
    return [x[1] for x in classes]


def loaddata(path):
    """
    Read a json file containing objects which map to the models defined in `crawler.models`.
    Add those objects to the database.
    """

    def get_model_class_from_tablename(tablename):
        """
        Given a tablename, return an actual class in `crawler.models` with attribute:
        __tablename__ = `tablename`
        """
        for Cls in get_all_models_classes():
            if tablename == Cls.__tablename__:
                return Cls

    # Read the entire file and load it as json
    with open(path, 'r', encoding='utf-8') as fin:
        content = json.loads(fin.read())

    with session_autocommit() as sex:
        i = 0
        # For each item in the json file, create an actual object in the db
        for item in content:
            Cls = get_model_class_from_tablename(item['tablename'])
            obj = Cls(**item['fields'])
            obj.id = item['id']
            sex.add(obj)
            i += 1

    print("{} objects successfully added to the database.".format(i))