from sqlalchemy import create_engine, Column, Integer, String, Enum
from magpie.settings import settings
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


_engine = None
def start_engine():
    global _engine
    if not _engine:
        _engine = create_engine('{}{}'.format(settings.DATABASE['ENGINE'],
                                              settings.DATABASE['NAME']),)
    return _engine
engine = start_engine()


def setup_db():
    Base.metadata.create_all(engine)


class Pet(Base):
    __tablename__ = "pet"

    id = Column(Integer, primary_key=True)
    type = Column(String(16))
    breed = Column(String(32))
    gender = Column(Enum('male', 'female'))
    name = Column(String(64))

    def __repr__(self):
        return "<Pet(id={}, name={}>".format(self.id, self.name)





