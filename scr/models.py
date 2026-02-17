from typing import Any, Dict

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Client(db.Model):  # type: ignore[name-defined]
    __tablename__ = "clients"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    surname = db.Column(db.String(50), nullable=False)
    credit_card = db.Column(db.String(50), nullable=True)
    car_number = db.Column(db.String(10))

    def __repr__(self):
        return f"Клиент {self.name} {self.surname}"

    def to_json(self) -> Dict[str, Any]:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Parking(db.Model):  # type: ignore[name-defined]
    __tablename__ = "parkings"

    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(100), nullable=False)
    opened = db.Column(db.Boolean)
    count_places = db.Column(db.Integer, nullable=False)
    count_available_places = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"Парковка {self.id}"

    def to_json(self) -> Dict[str, Any]:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class ClientParking(db.Model):  # type: ignore[name-defined]
    __tablename__ = "clients_parkings"

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"), unique=True)
    parking_id = db.Column(db.Integer, db.ForeignKey("parkings.id"), unique=True)
    time_in = db.Column(db.DateTime)
    time_out = db.Column(db.DateTime)
    client = db.relationship("Client", backref="clients_parkings", lazy="joined")
    parking = db.relationship("Parking", backref="clients_parkings", lazy="joined")

    def __repr__(self):
        return (
            f"Клиентская парковка {self.id}: клиент {self.client} "
            f"на парковке {self.parking}"
        )

    def to_json(self) -> Dict[str, Any]:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
