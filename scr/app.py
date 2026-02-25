import datetime

from faker import Faker
from flask import Flask, jsonify, request
from scr.models import (
    Client,
    ClientParking,
    Parking,
    db,
)
from tests.factories import (
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
        # Очищаем существующие данные
        db.session.query(ClientParking).delete()
        db.session.query(Client).delete()
        db.session.query(Parking).delete()
        db.session.commit()

        # Создаём новые
        clients = [ClientFactory() for _ in range(20)]
        parkings = [ParkingFactory() for _ in range(20)]

        db.session.commit()
        return f"Database populating: {len(clients)} clients, {len(parkings)} parkings"

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
            return "There is no client with this ID.", 404

    @app.route("/clients", methods=["POST"])
    def creat_client():
        """Создание нового клиента"""
        name = request.form.get("name", type=str)
        surname = request.form.get("surname", type=str)
        credit_card = request.form.get("credit_card", type=str)
        car_number = request.form.get("car_number", type=str)

        # Проверяем существование клиента
        existing_client = db.session.query(Client).filter(
            Client.name == name,
            Client.surname == surname
        ).first()

        if existing_client:
            return "Client with this name and surname already exists", 409

        new_client = Client(
            name=name,
            surname=surname,
            credit_card=credit_card,
            car_number=car_number
        )

        db.session.add(new_client)
        db.session.commit()
        return jsonify(new_client.to_json()), 201

    @app.route("/parkings", methods=["POST"])
    def creat_parking():
        """Создание новой парковочной зоны"""
        address = request.form.get("address", type=str)
        opened = request.form.get("opened", type=bool)
        count_places = request.form.get("count_places", type=int)
        count_available_places = request.form.get("count_available_places", type=int)

        # Проверяем существование парковочной зоны
        existing_client = db.session.query(Parking).filter(
            Parking.address == address
        ).first()

        if existing_client:
            return "Parking with this address already exists", 409

        new_parking = Parking(
            address=address,
            opened=opened,
            count_places=count_places,
            count_available_places=count_available_places
        )

        db.session.add(new_parking)
        db.session.commit()
        return jsonify(new_parking.to_json()), 201

    @app.route("/client_parkings", methods=["POST"])
    def parking_entrance():
        """Заезд клиента на парковку"""
        client_id = request.form.get("client_id")
        parking_id = request.form.get("parking_id")

        client_parking = db.session.query(ClientParking).filter(
            ClientParking.client_id == client_id,
            ClientParking.parking_id == parking_id
        ).first()

        if not client_parking or client_parking.time_out:
            parking = db.session.query(Parking).get(parking_id)

            if parking.opened is True:
                if not client_parking:
                    client_parking = ClientParking(
                        client_id=client_id,
                        parking_id=parking_id,
                        time_in=datetime.datetime.today(),
                    )
                    db.session.add(client_parking)
                if client_parking.time_out:
                    client_parking.time_in = datetime.datetime.today()
                    client_parking.time_out = None
                parking.count_available_places -= 1
                db.session.flush()
                if parking.count_available_places == 0:
                    parking.opened = False
                db.session.commit()
                return jsonify("Entry in parking: ", client_parking.to_json()), 201
            else:
                return "No available parking spaces", 200
        else:
            return "Client with this car number is already in parking", 409

    @app.route("/client_parkings", methods=["DELETE"])
    def exit_parking():
        """Выезд клиента с парковки"""
        client_id = request.form.get("client_id")
        parking_id = request.form.get("parking_id")

        client_parking = db.session.query(ClientParking).filter(
            ClientParking.client_id == client_id,
            ClientParking.parking_id == parking_id,
        ).first()

        if not client_parking or client_parking.time_out:
            return "Client with this car number is not in parking", 200

        parking = db.session.query(Parking).get(parking_id)
        client = db.session.query(Client).get(client_id)

        if client.credit_card:
            client_parking.time_out = datetime.datetime.today()
            parking.count_available_places += 1
            db.session.flush()
            if parking.count_available_places > 0 and parking.opened is False:
                parking.opened = True
            db.session.commit()
            return jsonify("Exit from parking:", client_parking.to_json()), 201
        else:
            return "ERROR! Credit card is not linked!", 200

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(port=8080, debug=True)
