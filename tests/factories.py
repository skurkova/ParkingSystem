import random

import factory
from scr.models import Client, Parking, db


class ClientFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Client
        sqlalchemy_session = db.session

    name = factory.Faker("first_name")
    surname = factory.Faker("last_name")
    credit_card = factory.Faker("credit_card_number")
    car_number = factory.Faker("license_plate")


class ParkingFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Parking
        sqlalchemy_session = db.session

    address = factory.Faker("address")
    count_places = factory.LazyAttribute(lambda x: random.randrange(10, 100))
    count_available_places = factory.LazyAttribute(
        lambda x: random.randrange(0, x.count_places)
    )
    opened = factory.LazyAttribute(lambda x: bool(x.count_available_places != 0))
