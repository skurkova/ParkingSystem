import datetime

from faker import Faker
from flask import Flask, jsonify, request
from module_30_ci_linters.homework.hw1.scr.models import (
    Client,
    ClientParking,
    Parking,
    db,
)
from module_30_ci_linters.homework.hw1.tests.factories import (
    ClientFactory,
    ParkingFactory,
)

fake = Faker("en_US")


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///parking.db"
    db.init_app(app)

    @app.before_request
    def before_request_func():
        db.create_all()

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db.session.remove()

    @app.route("/", methods=["GET"])
    def populating_db():
        """Заполнение БД"""
        clients = [ClientFactory() for _ in range(20)]
        parkings = [ParkingFactory() for _ in range(20)]

        db.session.bulk_save_objects(clients)
        db.session.bulk_save_objects(parkings)
        db.session.commit()
        return "Database populating"

    @app.route("/clients", methods=["GET"])
    def get_clients():
        """Получение списка всех клиентов"""
        clients = db.session.query(Client).all()

        clients_list = [client.to_json() for client in clients]
        return jsonify(clients_list), 200

    @app.route("/clients/<int:client_id>", methods=["GET"])
    def get_client_id(client_id: int):
        """Получение информации клиента по ID"""
        client = db.session.query(Client).get(client_id)
        if client is not None:
            return jsonify(client.to_json()), 200
        else:
            return "There is no client with this ID."

    @app.route("/clients", methods=["POST"])
    def creat_client():
        """Создание нового клиента"""
        new_client = Client(
            name=request.form.get("name", type=str),
            surname=request.form.get("surname", type=str),
            credit_card=request.form.get("credit_card", type=str),
            car_number=request.form.get("car_number", type=str),
        )

        db.session.add(new_client)
        db.session.commit()
        return jsonify(new_client.to_json()), 201

    @app.route("/parkings", methods=["POST"])
    def creat_parking():
        """Создание новой парковочной зоны"""
        new_parking = Parking(
            address=request.form.get("address", type=str),
            opened=request.form.get("opened", type=bool),
            count_places=request.form.get("count_places", type=int),
            count_available_places=request.form.get("count_available_places", type=int),
        )

        db.session.add(new_parking)
        db.session.commit()
        return jsonify(new_parking.to_json()), 201

    @app.route("/client_parkings", methods=["POST"])
    def parking_entrance():
        """Заезд клиента на парковку"""
        client_id = request.form.get("client_id")
        parking_id = request.form.get("parking_id")

        parking = db.session.query(Parking).get(parking_id)

        if parking.opened is True:
            client_parking = ClientParking(
                client_id=client_id,
                parking_id=parking_id,
                time_in=datetime.datetime.today(),
            )
            db.session.add(client_parking)
            parking.count_available_places -= 1
            db.session.flush()
            if parking.count_available_places == 0:
                parking.opened = False
            db.session.commit()
            return jsonify("Entry in parking: ", client_parking.to_json()), 201
        else:
            return "No available parking spaces", 201

    @app.route("/client_parkings", methods=["DELETE"])
    def exit_parking():
        """Выезд клиента с парковки"""
        client_id = request.form.get("client_id")
        parking_id = request.form.get("parking_id")

        parking = db.session.query(Parking).get(parking_id)
        client = db.session.query(Client).get(client_id)
        client_parking = (
            db.session.query(ClientParking)
            .filter(
                ClientParking.client_id == client_id,
                ClientParking.parking_id == parking_id,
            )
            .one_or_none()
        )

        if client.credit_card:
            client_parking.time_out = datetime.datetime.today()
            parking.count_available_places += 1
            db.session.flush()
            if parking.count_available_places != 0 and parking.opened is False:
                parking.opened = True
            db.session.commit()
            return jsonify("Exit from parking:", client_parking.to_json()), 201
        else:
            return "ERROR! Credit card is not linked!", 201

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(port=8080, debug=True)
