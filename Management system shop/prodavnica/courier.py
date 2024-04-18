import csv
import io

from flask import Flask, request, Response, jsonify
from configuration import Configuration
from models import database, Order, User
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, create_refresh_token, get_jwt, get_jwt_identity
from prodavnicaDecorator import roleCheck

application = Flask(__name__)
application.config.from_object(Configuration)
jwt = JWTManager(application)


@application.route("/pick_up_order", methods=["POST"])
@jwt_required()
@roleCheck(role="courier")
def pick_up_order():
    try:
        id = request.json.get("id", "")
    except Exception:
        return jsonify({"message": "Missing order id."}), 400
    if not id:
        return jsonify({"message": "Missing order id."}), 400
    if not isinstance(id, int):
        return jsonify({"message": "Invalid order id."}), 400
    if id <= 0:
        return jsonify({"message": "Invalid order id."}), 400
    order = Order.query.filter(Order.id == id).first()
    if not order:
        return jsonify({"message": "Invalid order id."}), 400
    if order.status != "CREATED":
        return jsonify({"message": "Invalid order id."}), 400
    order.status = "PENDING"
    database.session.commit()
    return Response(status=200)


@application.route("/orders_to_deliver", methods=["GET"])
@jwt_required()
@roleCheck(role="courier")
def orders_to_deliver():
    lista = []
    orders = Order.query.filter(Order.status == "CREATED").all()
    for order in orders:
        lista.append({"id": order.id, "email": order.email})
    return jsonify({"orders": lista}), 200


if (__name__ == "__main__"):
    database.init_app(application)
    application.run(debug=True, host="0.0.0.0", port=5003)