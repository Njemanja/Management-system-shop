from flask import Flask, request, Response, jsonify
from configuration import Configuration
from models import  database, User
from email.utils import  parseaddr
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, create_refresh_token, get_jwt, get_jwt_identity
from sqlalchemy import and_
import re


application = Flask(__name__)
application.config.from_object(Configuration)
jwt= JWTManager(application)

@application.route("/", methods=["GET"])
def index( ):
    return "Index page Auth.\nHello World."



@application.route("/register_customer", methods=["POST"])
def registerCustomer():
    print("Register customer")
    poruka=""
    email = request.json.get("email","")
    password = request.json.get("password", "")
    forename = request.json.get("forename", "")
    surname = request.json.get("surname", "")
    emailE= len(email)==0
    passwordE= len(password)==0
    forenameE= len(forename)==0
    surnameE = len(surname) == 0
    if (forenameE):
        return jsonify({'message': 'Field forename is missing.'}), 400
    if (surnameE):
        return jsonify({'message': 'Field surname is missing.'}), 400
    if(emailE):
        return jsonify({'message': 'Field email is missing.'}), 400
    if (passwordE):
        return jsonify({'message': 'Field password is missing.'}), 400

    if(poruka!=""):
       return jsonify(message=poruka), 400

    pattern = r'^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,4}$'

    if not re.match(pattern, email):
        return jsonify({'message':'Invalid email.'}), 400
    if (len(password) < 8):
        return jsonify({'message':'Invalid password.'}), 400
    user=User.query.filter(User.email==email).first()
    if user:
        return jsonify({'message':'Email already exists.'}), 400

    user= User(email=email, password=password, forename=forename, surname=surname, role="customer")
    database.session.add(user)
    database.session.commit()

    return Response(status=200)

@application.route("/register_courier", methods=["POST"])
def registerCourier():
    poruka=""
    email = request.json.get("email","")
    password = request.json.get("password", "")
    forename = request.json.get("forename", "")
    surname = request.json.get("surname", "")
    emailE= len(email)==0
    passwordE= len(password)==0
    forenameE= len(forename)==0
    surnameE = len(surname) == 0
    if (forenameE):
        return jsonify({'message': 'Field forename is missing.'}), 400
    if (surnameE):
        return jsonify({'message': 'Field surname is missing.'}), 400
    if (emailE):
        return jsonify({'message': 'Field email is missing.'}), 400
    if (passwordE):
        return jsonify({'message': 'Field password is missing.'}), 400
    if(poruka!=""):
       return jsonify(message=poruka), 400
    pattern = r'^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,4}$'
    if not re.match(pattern, email):
        return jsonify({'message':'Invalid email.'}), 400

    if (len(password) < 8):
        return jsonify({'message':'Invalid password.'}), 400
    user=User.query.filter(User.email==email).first()
    if user:
        return jsonify({'message':'Email already exists.'}), 400

    user= User(email=email, password=password, forename=forename, surname=surname, role="courier")
    database.session.add(user)
    database.session.commit()


    return Response(status=200)

@application.route("/login", methods=["POST"])
def login():
    email = request.json.get("email", "")
    password = request.json.get("password", "")
    emailE = len(email) == 0
    passwordE = len(password) == 0
    if (emailE ):
       return jsonify({'message': 'Field email is missing.'}), 400
    if(passwordE):
        return jsonify({'message': 'Field password is missing.'}), 400
    pattern = r'^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,4}$'

    if not re.match(pattern, email):
        return jsonify({'message':'Invalid email.'}), 400
    user= User.query.filter(and_ (User.email==email, User.password==password)).first()
    if(not user):
        return jsonify({'message':'Invalid credentials.'}), 400
    additionalClaims={
        "forename": user.forename,
        "surname": user.surname,
        "role": user.role,
        "roles": user.role,
        "id": user.id
    }
    accessToken= create_access_token(identity=user.email, additional_claims=additionalClaims)
    return jsonify({"accessToken" : accessToken})

@application.route("/delete", methods=["POST"])
@jwt_required()
def delete():
    token = get_jwt()
    if not (token):
        return jsonify({'message':"Missing Authorization Header"}), 400
    user= User.query.filter(User.email==token["sub"]).first()
    if not user:
        return jsonify({'message':'Unknown user.'}), 400
    database.session.delete(user)
    database.session.commit()
    return Response(status=200)






if(__name__=="__main__"):
    database.init_app(application)
    application.run(debug=True, host="0.0.0.0", port=5000) #5001