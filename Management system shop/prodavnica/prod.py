import json
from pyspark.sql import SparkSession
import os


PRODUCTION = True if ("PRODUCTION" in os.environ) else False
DATABASE_IP = "ShopDB"

builder = SparkSession.builder.appName("PySpark Database example")

if (not PRODUCTION):
    builder = builder.master("local[*]") \
        .config(
        "spark.driver.extraClassPath",
        "mysql-connector-j-8.0.33.jar"
    )

spark = builder.getOrCreate()

products = spark.read \
    .format ( "jdbc" ) \
    .option ( "driver","com.mysql.cj.jdbc.Driver" ) \
    .option ( "url", f"jdbc:mysql://{DATABASE_IP}:3306/prodavnicaDatabase" ) \
    .option ( "dbtable", "prodavnicaDatabase.products" ) \
    .option ( "user", "root" ) \
    .option ( "password", "root" ) \
    .load ( )

product_orders = spark.read \
    .format ( "jdbc" ) \
    .option ( "driver","com.mysql.cj.jdbc.Driver" ) \
    .option ( "url", f"jdbc:mysql://{DATABASE_IP}:3306/prodavnicaDatabase" ) \
    .option ( "dbtable", "prodavnicaDatabase.productorders" ) \
    .option ( "user", "root" ) \
    .option ( "password", "root" ) \
    .load ( )

orders = spark.read \
    .format ( "jdbc" ) \
    .option ( "driver","com.mysql.cj.jdbc.Driver" ) \
    .option ( "url", f"jdbc:mysql://{DATABASE_IP}:3306/prodavnicaDatabase" ) \
    .option ( "dbtable", "prodavnicaDatabase.orders" ) \
    .option ( "user", "root" ) \
    .option ( "password", "root" ) \
    .load ( )

products.createOrReplaceTempView("products")
product_orders.createOrReplaceTempView("product_orders")
orders.createOrReplaceTempView("orders")

statistics = spark.sql("""
    SELECT products.productName AS name,
        SUM(CASE WHEN orders.status = 'COMPLETE' THEN product_orders.quantity ELSE 0 END) AS sold,
        SUM(CASE WHEN orders.status != 'COMPLETE' THEN product_orders.quantity ELSE 0 END) AS waiting
    FROM products
    JOIN product_orders ON product_orders.idProduct = products.id
    JOIN orders ON orders.id = product_orders.idOrder
    GROUP BY products.productName
    HAVING sold > 0 OR waiting > 0
    ORDER BY name ASC
""")

statistics_json = statistics.toJSON().collect()

with open("prod.json", "w") as f:
    for l in statistics_json:
        f.write(json.dumps(l)+"\n")

