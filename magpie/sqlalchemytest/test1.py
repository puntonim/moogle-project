from contextlib import contextmanager

from sqlalchemy.orm import sessionmaker

from .models import Pet, engine


@contextmanager
def begin_session():
    Session = sessionmaker(bind=engine)
    sex = Session()
    try:
        yield sex
    except:
        sex.rollback()
        raise
    finally:
        sex.close()

if __name__ == "__main__":
    # Setup (run only the first time)
    #setup_db()

    pet = Pet()
    pet.id = 2
    pet.type = "dog"
    pet.breed = "spaniel"
    pet.gender = "female"
    pet.name = "cuca"

    with begin_session() as session:
        cuca = session.query(Pet).filter_by(name='cuca').one()
        print(cuca.id, cuca.name, cuca.breed)

        #dogs = session.query(Pet).filter_by(type='dog')
        dogs = session.query(Pet).filter_by(Pet.type=='dog')
        for dog in dogs:
            print(dog.id, dog.name, dog.breed)
