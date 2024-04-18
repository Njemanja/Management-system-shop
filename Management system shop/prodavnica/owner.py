import csv
import io
import json

import requests
from flask import Flask, request, jsonify


from configuration import Configuration
from models import database, Product, Order, ProductOrder, ProductCategory, Category
import os
import subprocess
from flask_jwt_extended import JWTManager, jwt_required
from prodavnicaDecorator import roleCheck




application = Flask(__name__)
application.config.from_object(Configuration)
jwt = JWTManager(application)


@application.route("/update", methods=["POST"])
@jwt_required()
@roleCheck(role="owner")
def update():
    file = request.files.get("file")
    if not file:
        return jsonify(message="Field file is missing."), 400

    datas = file.stream.read().decode("utf-8")
    con = io.StringIO(datas)
    read = csv.reader(con)
    proizvodi = []
    i = -1
    lista = []
    for proizvod in read:
        i+=1
        lista.append(proizvod)
        print(proizvod)
        kategorije = proizvod[0].split("|")
        if len(proizvod) != 3 or proizvod[0]=="" or proizvod[1]=="" or proizvod[2]=="":
            return jsonify({"message": "Incorrect number of values on line " + str(i) + "."}), 400
        try:
            if float(proizvod[2]) <= 0:
                return jsonify({"message": "Incorrect price on line " + str(i) + "."}), 400
        except Exception:
            return jsonify({"message": "Incorrect price on line " + str(i) + "."}), 400

        product = Product.query.filter(Product.productName == proizvod[1]).first()

        if not product:
            jedanProizvod = Product(
                price=float(proizvod[2]),
                productName=proizvod[1]
            )
            proizvodi.append(jedanProizvod)

        else:
            return jsonify({"message":   "Product " + proizvod[1] + " already exists." }), 400

    product = Product.query.filter().all()
    id = len(product) + 1
    lista1=[]
    for p in proizvodi:
        database.session.add(p)
        database.session.commit()
        a=1
    for proizvod in lista:
        kategorije = proizvod[0].split("|")
        for k in kategorije:
            idKategorije = Category.query.filter(Category.categoryName == k).first()
            if not idKategorije:
                c = Category(
                    categoryName=k
                )
                database.session.add(c)
                database.session.commit()
            idKategorije = Category.query.filter(Category.categoryName == k).first()
            idKategorije = idKategorije.id
            id = Product.query.filter(Product.productName == proizvod[1]).first()
            c = ProductCategory(
                idProduct=id.id,
                idCategory=idKategorije
            )
            database.session.add(c)
            database.session.commit()
    l=ProductCategory.query.filter().all()
    return jsonify(""),200





#SPARK-----------------------------------------------------------------------------------------------------------------------------

@application.route("/product_statistics", methods=["GET"])
@jwt_required()
@roleCheck(role="owner")
def product_statisticsSpark():
    response= requests.get("http://sparkapp:5000/product_statisticsSpark").content
    return response, 200



@application.route("/category_statistics", methods=["GET"])
@jwt_required()
@roleCheck(role="owner")
def categoryStatisticsSpark():
    response = requests.get("http://sparkapp:5000/category_statisticsSpark").content
    response=response.decode("utf-8")[1:-1]
    response=response.split(",")
    lista=[]
    for r in response:
        lista.append(r)
    limited_response = [item.strip('"/') for item in lista]
    limited_response.pop()
    return jsonify({"statistics": limited_response}), 200



@application.route("/", methods=["POST"])
def index():
    return "Index page of owner.\nHello World"



#--------------------------------------------------------------------------------------------------------------------
@application.route("/category_statistics1", methods=["GET"])
@jwt_required()
@roleCheck(role="owner")
def categoryStatistics():
    #categoryStat()
    s=0
    imenaKategorija = []
    lista = Category.query.filter().all()
    for l in lista:
        broj=0
        ime = l.categoryName
        orders=Order.query.filter().all()
        for order in orders:
            if order.status=="COMPLETE":
                productOrders=ProductOrder.query.filter(order.id==ProductOrder.idOrder).all()
                for productOrder in productOrders:
                    productCategory = ProductCategory.query.filter(productOrder.idProduct == ProductCategory.idProduct).all()
                    for p in productCategory:
                        if(p.idCategory==l.id):
                            broj+=productOrder.quantity
        imenaKategorija.append({
            "ime": ime,
            "broj": broj,
            "idKategorije": l.id})
        s+=1
    sorted_data = sorted(imenaKategorija, key=lambda x: (-x['broj'], x['ime']))
    lista = []
    for s in sorted_data:
        lista.append(s["ime"])
    return jsonify({"statistics": lista}), 200


@application.route("/product_statistics1", methods=["GET"])
@jwt_required()
@roleCheck(role="owner")
def product_statistics():
    #productStat()
    products = Product.query.filter().all()
    productOrder = ProductOrder.query.filter().all()
    statistics = []
    for product in products:
        sold = 0
        waiting = 0
        for p in productOrder:
            if (p.idProduct == product.id):
                order = Order.query.filter(Order.id == p.idOrder).first()
                if (order.status == "COMPLETE"):
                    sold += p.quantity
                else:
                    waiting += p.quantity
        if sold>0 or waiting>0:
            statistics.append({
                "name": product.productName,
                "sold": sold,
                "waiting": waiting
            })
    return jsonify({"statistics": statistics}), 200


if (__name__ == "__main__"):
    database.init_app(application)
    application.run(debug=True, host="0.0.0.0", port=5001)