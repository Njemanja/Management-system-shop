from pyspark.sql import SparkSession
from pyspark.sql.functions import col
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

categories = spark.read \
    .format ( "jdbc" ) \
    .option ( "driver","com.mysql.cj.jdbc.Driver" ) \
    .option ( "url", f"jdbc:mysql://{DATABASE_IP}:3306/prodavnicaDatabase" ) \
    .option ( "dbtable", "prodavnicaDatabase.categories" ) \
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

product_orders= spark.read \
    .format ( "jdbc" ) \
    .option ( "driver","com.mysql.cj.jdbc.Driver" ) \
    .option ( "url", f"jdbc:mysql://{DATABASE_IP}:3306/prodavnicaDatabase" ) \
    .option ( "dbtable", "prodavnicaDatabase.productorders" ) \
    .option ( "user", "root" ) \
    .option ( "password", "root" ) \
    .load ( )

product_category = spark.read \
    .format ( "jdbc" ) \
    .option ( "driver","com.mysql.cj.jdbc.Driver" ) \
    .option ( "url", f"jdbc:mysql://{DATABASE_IP}:3306/prodavnicaDatabase" ) \
    .option ( "dbtable", "prodavnicaDatabase.productcategories" ) \
    .option ( "user", "root" ) \
    .option ( "password", "root" ) \
    .load ( )

categories.createOrReplaceTempView("categories")
orders.createOrReplaceTempView("orders")
product_orders.createOrReplaceTempView("product_orders")
product_category.createOrReplaceTempView("product_category")

statistics= spark.sql("""
    SELECT c.categoryName AS ime, COALESCE(SUM(po.quantity), 0) AS broj
    FROM categories c
    LEFT JOIN product_category pc ON pc.idCategory = c.id
    LEFT JOIN product_orders po ON po.idProduct = pc.idProduct
    LEFT JOIN orders o ON o.id = po.idOrder 
    WHERE o.status = 'COMPLETE'
    GROUP BY c.categoryName, c.id
    ORDER BY broj DESC, ime ASC
""")

statistics2= spark.sql("""
    SELECT c.categoryName AS ime
    FROM categories c
    LEFT JOIN product_category pc ON pc.idCategory = c.id
    LEFT JOIN product_orders po ON po.idProduct = pc.idProduct
    LEFT JOIN orders o ON o.id = po.idOrder 
    ORDER BY ime ASC
""")


statistics_list = statistics.select(col("ime")).rdd.flatMap(lambda x: x).collect()
statistics_list2 = statistics2.select(col("ime")).rdd.flatMap(lambda x: x).collect()
for s in statistics_list2:
    if s not in statistics_list:
        statistics_list.append(s)




with open("cat.json", "w") as f:
    for line in statistics_list:
        f.write(line + "\n")

spark.stop()