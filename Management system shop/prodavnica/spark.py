import json
import os
import subprocess
from flask import Flask, request, jsonify




application = Flask(__name__)



@application.route("/product_statisticsSpark", methods=["GET"])
def product_statisticsSpark():
    os.environ["SPARK_APPLICATION_PYTHON_LOCATION"] = "/app/prodavnica/prod.py"
    os.environ["SPARK_SUBMIT_ARGS"] = "--driver-class-path /app/mysql-connector-j-8.0.33.jar --jars /app/mysql-connector-j-8.0.33.jar"
    result = subprocess.check_output(["/template.sh"]).decode()
    lista=[]
    with open("prod.json", "r") as f:
         for l in f:
             lista.append(json.loads((json.loads(l))))
    return jsonify({"statistics": lista})


@application.route("/category_statisticsSpark", methods=["GET"])
def category_statisticsSpark():
    os.environ["SPARK_APPLICATION_PYTHON_LOCATION"] = "/app/prodavnica/cat.py"
    os.environ["SPARK_SUBMIT_ARGS"] = "--driver-class-path /app/mysql-connector-j-8.0.33.jar --jars /app/mysql-connector-j-8.0.33.jar"
    result = subprocess.check_output(["/template.sh"]).decode()
    with open("cat.json", "r") as f:
         result=f.read()
    return result.split("\n")

if (__name__ == "__main__"):
    HOST="0.0.0.0" if ("PRODUCTION" in os.environ) else "127.0.0.1"
    application.run(host=HOST)