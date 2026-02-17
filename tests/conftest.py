import datetime

import pytest
from scr.app import create_app
from scr.models import (
  Client,
  ClientParking,
  Parking
)
from scr.models import db as _db


@pytest.fixture
def app():
    _app = create_app()
    _app.config["TESTING"] = True
    _app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"

    with _app.app_context():
        _db.create_all()
        clients = [
            Client(
                id=1,
                name="Name 1",
                surname="Surname 1",
                credit_card="credit_card",
                car_number="car_number 1",
            ),
            Client(
                id=2,
                name="Name 2",
                surname="Surname 2",
                credit_card=None,
                car_number="car_number 2",
            ),
        ]
        parkings = [
            Parking(
                id=1,
                address="address 1",
                opened=True,
                count_places=50,
                count_available_places=10,
            ),
            Parking(
                id=2,
                address="address 2",
                opened=False,
                count_places=20,
                count_available_places=0,
            ),
        ]
        client_parking = ClientParking(
            id=1,
            client_id=1,
            parking_id=1,
            time_in=datetime.datetime.today(),
            time_out=None,
        )
        _db.session.bulk_save_objects(clients)
        _db.session.bulk_save_objects(parkings)
        _db.session.add(client_parking)
        _db.session.commit()

        yield _app
        _db.session.close()
        _db.drop_all()


@pytest.fixture
def client(app):
    client = app.test_client()
    yield client


@pytest.fixture
def db(app):
    with app.app_context():
        yield _db
