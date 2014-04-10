from sqlalchemy import Column, Integer, String, Enum, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref


Base = declarative_base()


class Pet(Base):
    __tablename__ = "pet"

    id = Column(Integer, primary_key=True)  # Automatically generated if not provided
    type = Column(String(16))
    breed = Column(String(32))  # default: nullable=True
    gender = Column(Enum('male', 'female'))  # Accepts only 'male' or 'female' (not nullable)
    name = Column(String(64), nullable=False)  # This is not nullable

    # Set the related field on the other table (pethouse.id)
    pethouse_id = Column(Integer, ForeignKey('pethouse.id'))
    # Set the other table (PetHouse) and the name of the reverse relationship (pets)
    pethouse = relationship("PetHouse", backref=backref('pets', order_by=id))

    def __repr__(self):
        return "<Pet(id={}, name={}>".format(self.id, self.name)


class PetHouse(Base):
    __tablename__ = "pethouse"

    id = Column(Integer, primary_key=True)
    name = Column(String(16))
    address = Column(String(16))



