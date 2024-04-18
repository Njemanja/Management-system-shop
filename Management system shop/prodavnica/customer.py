from builtins import Exception
from flask import Flask, request, Response, jsonify
from configuration import Configuration
from models import database, Order, Product, ProductOrder, Category, ProductCategory
from flask_jwt_extended import JWTManager, jwt_required, get_jwt
from datetime import datetime
from prodavnicaDecorator import roleCheck

application = Flask(__name__)
application.config.from_object(Configuration)
jwt = JWTManager(application)


@application.route("/delivered", methods=["POST"])
@jwt_required()
@roleCheck(role="customer")
def delivered():
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
    if order.status == "CREATED":
        return jsonify({"message": "Invalid order id."}), 400
    order.status = "COMPLETE"
    database.session.commit()
    return Response(status=200)


@application.route("/status", methods=["GET"])
@roleCheck(role="customer")
@jwt_required()
def status():
    orders = Order.query.filter().all()
    allOrders = []
    for order in orders:
        products = []
        productsOrder = ProductOrder.query.filter(ProductOrder.idOrder == order.id).all()
        for p in productsOrder:
            categories = []
            productCategories = ProductCategory.query.filter(ProductCategory.idProduct == p.idProduct).all()
            for c in productCategories:
                category = Category.query.filter(Category.id == c.idCategory).first()
                categories.append(category.categoryName)
            oneProduct = Product.query.filter(Product.id == p.idProduct).first()
            products.append({"categories": categories, "name": oneProduct.productName, "price": oneProduct.price,
                             "quantity": p.quantity})
        allOrders.append({"products": products, "price": order.price, "status": order.status,
                          "timestamp": (order.timestamp).isoformat()})

    return jsonify({"orders": allOrders})


@application.route("/order", methods=["POST"])
@roleCheck(role="customer")
@jwt_required()
def order():
    finalPrice = 0
    try:
        req = request.json.get("requests", "")
    except Exception:
        return jsonify({"message": "Field requests is missing."}), 400
    if not req:
        return jsonify({"message": "Field requests is missing."}), 400
    i = 1
    lista = []
    for r in req:
        try:
            id = r["id"]
        except Exception:
            return jsonify({"message": "Product id is missing for request number " + str(i-1) + "."}), 400
        try:
            q = r["quantity"]
        except Exception:
            return jsonify({"message": "Product quantity is missing for request number " + str(i-1) + "."}), 400
        if not isinstance(id, int):
            return jsonify({"message": "Invalid product id for request number " + str(i-1) + "."}), 400
        if id <= 0:
            return jsonify({"message": "Invalid product id for request number " + str(i-1) + "."}), 400

        if not isinstance(q, int):
            return jsonify({"message": "Invalid product quantity for request number " + str(i - 1) + "."}), 400
        if q <= 0:
            return jsonify({"message": "Invalid product quantity for request number " + str(i-1) + "."}), 400
        product = Product.query.filter(Product.id == id).first()
        if not product:
            return jsonify({"message": "Invalid product for request number " + str(i-1) + "."}), 400
        i += 1
        p = ProductOrder()
        p.idProduct = product.id
        p.quantity = q
        p.price = product.price
        finalPrice += q * product.price
        lista.append(p)
    claims = get_jwt()

    o = Order()
    o.price = finalPrice
    o.status = "CREATED"
    o.timestamp = datetime.now()
    o.email = claims["sub"]
    o.idCustomer = claims["id"]
    o.idCourier = 0
    database.session.add(o)
    database.session.commit()
    last = Order.query.order_by(Order.id.desc()).first()
    for l in lista:
        l.idOrder = last.id
        database.session.add(l)
        database.session.commit()
    return jsonify({"id": last.id}), 200


@application.route("/search", methods=["GET"])
@roleCheck(role="customer")
@jwt_required()
def search():
    ime = request.args.get("name")
    kategorija = request.args.get("category")
    if not ime:
        ime = ""
    else:
        ime = (ime.split("\n"))[0]
    if not kategorija:
        kategorija = ""
    kategorije = []
    a = kategorija.split('\n')
    a = a[0]
    category= Category.query.filter(Category.categoryName.like(f"%{a}%")).all()
    for k in category:
        kategorije.append(k.categoryName)
    proizvodi = []
    kategorijeKojePostoje = []
    product = Product.query.filter(Product.productName.like(f"%{ime}%")).all()

    for p in product:
        productCategory = ProductCategory.query.filter(ProductCategory.idProduct == p.id).all()
        if not productCategory:
            continue
        lista = []
        imaKategoriju = False
        for pc in productCategory:
            kat = Category.query.filter(Category.id == pc.idCategory).first()
            if kat.categoryName in kategorije:
                imaKategoriju = True
                lista.append(kat.categoryName)
                if not (kat.categoryName in kategorijeKojePostoje):
                    kategorijeKojePostoje.append(kat.categoryName)
        if imaKategoriju:
            proizvodi.append({"categories": lista, "id": p.id, "name": p.productName, "price": p.price})
    for k in kategorije:
        if not k in kategorijeKojePostoje:
            kategorije.remove(k)

    return jsonify({"categories": kategorijeKojePostoje, "products": proizvodi}), 200


if (__name__ == "__main__"):
    database.init_app(application)
    application.run(debug=True, host="0.0.0.0", port=5002)