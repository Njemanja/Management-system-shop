from flask_sqlalchemy import SQLAlchemy


database=SQLAlchemy()

class Product(database.Model):
    __tablename__="products"
    id=database.Column(database.Integer, primary_key=True)
    price=database.Column(database.Float, nullable=False)
    productName=database.Column(database.String(256), nullable=False)
    def __repr__(self):
        return str(self.id)+":"+self.productName

class Category(database.Model):
    __tablename__="categories"
    id=database.Column(database.Integer, primary_key=True)
    categoryName=database.Column(database.String(256), nullable=False)
    def __repr__(self):
        return str(self.id)+":"+self.categoryName

class ProductCategory(database.Model):
    __tablename__="productcategories"
    id=database.Column(database.Integer, primary_key=True)
    idCategory=database.Column(database.Integer, database.ForeignKey("categories.id"), nullable=False)
    idProduct=database.Column(database.Integer, database.ForeignKey("products.id"), nullable=False)
    def __repr__(self):
        return str(self.id)+":"+ "IDCategory-"+str(self.idCategory)+"   IDProduct-"+str(self.idProduct)

class ProductOrder(database.Model):
    __tablename__="productorders"
    id=database.Column(database.Integer, primary_key=True)
    quantity=database.Column(database.Integer, nullable=False)
    price = database.Column(database.Float, nullable=False)
    idOrder = database.Column(database.Integer, database.ForeignKey("orders.id"), nullable=False)
    idProduct = database.Column(database.Integer, database.ForeignKey("products.id"), nullable=False)
    def __repr__(self):
        return self.id


class Order(database.Model):
    __tablename__="orders"
    id=database.Column(database.Integer, primary_key=True)
    price=database.Column(database.Float, nullable=False)
    status=database.Column(database.String(256), nullable=False)
    timestamp=database.Column(database.DateTime, nullable=False)
    idCustomer=database.Column(database.Integer, nullable=False)
    email=database.Column(database.String(256), nullable=False)
    #idCourier=database.Column(database.Integer, nullable=False)
    def __repr__(self):
        return self.id

class User(database.Model):
    __tablename__="users"
    id=database.Column(database.Integer, primary_key=True)
    email=database.Column(database.String(256), nullable=False, unique=True)
    password=database.Column(database.String(256), nullable=False)
    forename=database.Column(database.String(256), nullable=False)
    surname=database.Column(database.String(256), nullable=False)
    role=database.Column(database.String(256), nullable=False)
    def __repr__(self):
        return self.forename + " "+ self.surname+" "+self.email+" "+self.role