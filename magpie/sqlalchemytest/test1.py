from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from .models import Pet, PetHouse
from .dbutils import session_autocommit


if __name__ == "__main__":
    ## SCHEMA CREATION
    #from .models import setup_db
    #setup_db()
    #exit(0)

    with session_autocommit() as sex:
        ## INSERT
        ## Create the Python object
        #pet1 = Pet()
        #pet1.id = 3  # No need to specify it, it will be chosen automatically
        #pet1.type = "dog"
        #pet1.breed = "spaniel"
        #pet1.gender = "female"
        #pet1.name = "cuca"
        #
        ## Insert 1 object
        #sex.add(pet1)
        #
        ## Add more objects
        #import copy
        #pet2 = copy.deepcopy(pet1)
        #pet2.name = "cuca maria"
        #sex.add_all([pet1, pet2])


        ## SELECT
        ## SELECT 1 OBJECT
        #cuca = sex.query(Pet).filter_by(name='cuca', type='dog').one()  # Joined by AND
        #
        ## This object is the same as the one we have just created
        #assert cuca is pet1  # where `pet1` is the Python object instantiated in 4. INSERT
        #print(cuca.id, cuca.name, cuca.breed)
        #
        ## SELECT ALL OBJECTS
        #for pet in sex.query(Pet).all():  # all() is optional
        #    print(pet)
        #
        ## SELECT MORE OBJECTS
        #dogs = sex.query(Pet).filter_by(type='dog')
        ## Using SQL Expression Language by SQLAlchemy
        ##dogs = session.query(Pet).filter(Pet.type=='dog')
        #for dog in dogs:
        #    print(dog.id, dog.name, dog.breed)
        #
        ## SELECT ONLY SOME FIELDS
        #for type, name in sex.query(Pet.type, Pet.name).all():
        #    print(type, name)

        # SELECT WITH LIMIT, OFFSET, ORDER BY
        #for pet in sex.query(Pet).order_by(-Pet.id)[1:2]:
        #    print(pet)

        # SELECT USING filter() (more powerful than filter_by)
        # http://docs.sqlalchemy.org/en/rel_0_9/orm/tutorial.html#common-filter-operators
        #cuca = sex.query(Pet).filter(Pet.name=='cuca', Pet.type=='dog').one()  # Joined by AND
        #
        #from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
        #try:
        #    cuca = sex.query(Pet).filter(Pet.name.like('%cuca%')).one()
        #except MultipleResultsFound as e:
        #    print(e)
        #except NoResultFound as e:
        #    print(e)

        #n = sex.query(Pet).count()
        #print(n)
        #
        #n = sex.query(Pet).group_by(Pet.type)
        #for m in n:
        #    print(m)

        # UPDATE
        #cuca = sex.query(Pet).filter_by(name='cuca').one()
        #
        #cuca.type = 'dog'

        #house = PetHouse()
        #house.name = "Casa rosso"
        #house.address = "Via le mani dal naso"
        #sex.add(house)

        house = sex.query(PetHouse).filter_by(name='Casa rosso').one()

        #pet1 = Pet()
        #pet1.type = "dog"
        #pet1.breed = "spaniel"
        #pet1.gender = "female"
        #pet1.name = "cuca2"
        #pet1.pethouse = house
        #sex.add(pet1)

        #print(dir(house))
        #print(house.pets)

        cuca2 = sex.query(Pet).filter_by(name='cuca2').one()
        print(dir(cuca2))
        print(cuca2.pethouse)


    with session_autocommit() as sex:
        n = sex.query(Pet).count()
        print(n)