import pytest
from faker import Faker
from scr.models import Client, Parking
from tests.factories import (
  ClientFactory,
  ParkingFactory
)

fake = Faker("en_US")


@pytest.mark.parametrize("route", ["/clients", "/clients/1"])
def test_route_status(client, route):
    rv = client.get(route)
    assert rv.status_code == 200


def test_creat_client(client) -> None:
    client_data = {
        "name": fake.last_name(),
        "surname": fake.first_name(),
        "credit_card": fake.credit_card_number(),
        "car_number": fake.license_plate(),
    }
    resp = client.post("/clients", data=client_data)
    assert resp.status_code == 201


def test_creat_parking(client) -> None:
    parking_data = {
        "address": fake.address(),
        "opened": True,
        "count_places": 50,
        "count_available_places": 10,
    }
    resp = client.post("/parkings", data=parking_data)
    assert resp.status_code == 201


def test_parking_entrance(client) -> None:
    client_parking_data = {"client_id": 3, "parking_id": 1}
    resp = client.post("/client_parkings", data=client_parking_data)
    assert resp.status_code == 201


def test_parking_no_entrance(client) -> None:
    client_parking_data = {"client_id": 1, "parking_id": 2}
    resp = client.post("/client_parkings", data=client_parking_data)
    assert resp.status_code == 200
    assert resp.data.decode() == "No available parking spaces"


def test_exit_parking(client) -> None:
    client_parking_data = {"client_id": 1, "parking_id": 1}
    resp = client.delete("/client_parkings", data=client_parking_data)
    assert resp.status_code == 201


def test_no_exit_parking(client) -> None:
    client_parking_data = {"client_id": 2, "parking_id": 1}
    resp = client.delete("/client_parkings", data=client_parking_data)
    assert resp.status_code == 200
    assert resp.data.decode() == "ERROR! Credit card is not linked!"


def test_creat_client_factory(db):
    client = ClientFactory()
    db.session.commit()
    assert client.id is not None
    assert len(db.session.query(Client).all()) == 3


def test_creat_parking_factory(db):
    parking = ParkingFactory()
    db.session.commit()
    assert parking.id is not None
    assert len(db.session.query(Parking).all()) == 3
