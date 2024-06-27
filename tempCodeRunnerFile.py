from flask import Flask, jsonify, request 
from flask_cors import CORS 
from flask_sqlalchemy import SQLAlchemy 
from sqlalchemy.orm import Mapped, mapped_column, relationship, Session, registry
from sqlalchemy import select, ForeignKey, Column, String, Integer, Table, Float, Date, MetaData
from sqlalchemy.ext.declarative import declarative_base
from flask_marshmallow import Marshmallow 
from marshmallow import fields, ValidationError
from typing import List
from datetime import datetime, timedelta


app = Flask(__name__)
cors = CORS(app)
# CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+mysqlconnector://root:Hammond45!@localhost/Online_Shopping_project"
app.json.sort_keys = False
db = SQLAlchemy(app)
ma = Marshmallow(app)
Base = declarative_base(cls = db.Model)
metadata = MetaData() 
registry = registry()
app.app_context().push()


# Order Product 
class OrderProduct(Base): 
    __tablename__ = "Order_Product"
    order_id = Column(Integer, ForeignKey('Orders.order_id'), primary_key=True)
    product_id = Column(Integer, ForeignKey('Products.product_id'), primary_key=True)

class OrderProductSchema(ma.Schema):
    order_id = fields.Integer(required=True)
    product_id = fields.Integer(required=False)
    
    class Meta:
        fields = ("order_id", "product_id")

order_product_schema = OrderProductSchema()
order_products_schema = OrderProductSchema(many=True) 


# Product 
class Product(Base):
    __tablename__ = "Products"
    product_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    price = Column(Float, nullable=False)
    orders = relationship("OrderProduct")

class ProductSchema(ma.Schema):
    product_id = fields.Integer(required=False)
    name = fields.String(required=True)
    price = fields.Float(required=True)

    class Meta:
        fields = ("product_id", "name", "price")

product_schema = ProductSchema()
products_schema = ProductSchema(many=True) 

@app.route("/products", methods = ["GET"])
def get_products():
    query = select(Product) 
    result = db.session.execute(query).scalars() 
    print(result)
    products = result.all() 
    return products_schema.jsonify(products)

@app.route("/products/name_of_product/<string:name>", methods=["GET"])
def get_product_per_name(name):
    product = Product.query.filter(Product.name == name).first()
    if product:
        return product_schema.jsonify(product)
    else:
        return jsonify({"message": "Product could not be found by that name"}), 404

    
@app.route("/products", methods = ["POST"])
def add_product():
    try:
        product_data = product_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    with Session(db.engine) as session: 
        with session.begin():
            name = product_data['name']
            price = product_data['price']
            new_product = Product(name = name, price = price)
            session.add(new_product)
            session.commit()
    return jsonify({"message": "New product added successfully"}), 201 

@app.route("/products/<int:product_id>", methods=["PUT"])
def update_product(product_id):
    try:
        query = select(Product).filter(Product.product_id == product_id)
        product = db.session.execute(query).scalars().first()
        if not product: 
            return jsonify({"message": "Product could not be found with that product ID"}), 404
        product_data = product_schema.load(request.json, partial = True)
        for field, value in product_data.items():
            setattr(product, field, value)
        db.session.commit()
        return jsonify({"message": "Product updated successfully"}), 200
    except ValidationError as err:
        return jsonify(err.messages), 400

@app.route("/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    product = Product.query.filter(product_id==product_id).first()
    if not product: 
        return jsonify({"message": "Product could not be found with that product ID"}), 404
    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": "Product deleted successfully."}), 200

@app.route("/products/restock_products", methods=["POST"]) # This is a bonus option 
def restock_products():
    threshold = request.json.get("threshold", 10) 
    products_to_restock = []
    low_stock_products = Product.query.filter(Product.stock < threshold).all()
    for product in low_stock_products:
        product.stock += 20 
        products_to_restock.append(product)
    db.session.commit()
    return products_schema.jsonify(products_to_restock)


# Orders

order_table = Table(
    "Orders",
    metadata,
    Column("order_id", Integer, primary_key = True, autoincrement = True),
    Column("date", Date, nullable = False),
    Column("customer_id", Integer, ForeignKey('Customers.customer_id'))
)
class Order(Base):
    __tablename__ = "Orders"
    order_id: Mapped[int] = mapped_column(autoincrement = True, primary_key = True)
    date: Mapped[datetime.date] = mapped_column(Date, nullable = False)
    customer_id: Mapped[int] = mapped_column(Integer, ForeignKey('Customers.customer_id'))
    customer: Mapped['Customer'] = relationship("Customer", back_populates = "orders")
    products: Mapped[List["Product"]] = relationship("Product", secondary = "Order_Product")

class OrderSchema(ma.Schema):
    order_id = fields.Integer(required = False)
    date = fields.Date(required = True)
    customer_id = fields.Integer(required = True)

    class Meta:
        fields = ("order_id", "date", "customer_id")

order_schema = OrderSchema()
orders_schema = OrderSchema(many = True) 

@app.route("/orders", methods = ["GET"])
def get_orders():
    query = select(Order) 
    result = db.session.execute(query).scalars() 
    print(result)
    orders = result.all() 
    return orders_schema.jsonify(orders)

@app.route("/orders/<int:customer_id>", methods=["GET"])
def get_order_per_customer_id(customer_id):
    orders = Order.query.filter(Order.customer_id == customer_id).all()
    if orders:
        return orders_schema.jsonify(orders)
    else:
        return jsonify({"message": "No orders found for this customer"}), 404


@app.route("/orders", methods = ["POST"])
def add_order():
    try:
        order_data = order_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    with Session(db.engine) as session: 
        with session.begin():
            date = order_data['date']
            customer_id = order_data['customer_id']
            new_order = Order(date = date, customer_id = customer_id)
            session.add(new_order)
            session.commit()
    return jsonify({"message": "New order added successfully"}), 201 

@app.route("/orders/<int:order_id>", methods=["PUT"]) 
def update_order(order_id):
    try:
        order = Order.query.filter(Order.order_id ==order_id).first()
        if not order: 
            return jsonify({"message": "Order could not be found with that order ID"}), 404
        order_data = order_schema.load(request.json, partial = True)
        for field, value in order_data.items():
            setattr(order, field, value)
        db.session.commit()
        return jsonify({"message": "Order updated successfully"}), 200
    except ValidationError as err:
        return jsonify(err.messages), 400

@app.route("/orders/<int:order_id>", methods=["DELETE"])
def delete_order(order_id):
    order = Order.query.filter(Order.order_id == order_id).first()
    if not order: 
        return jsonify({"message": "Order could not be found with that order ID"}), 404
    db.session.delete(order)
    db.session.commit()
    return jsonify({"message": "Order deleted successfully."}), 200

@app.route("/track_order/<int:order_id>", methods=["GET"]) # This was listed on the initial project assignment then removed (Track Order)
def track_order(order_id):
    order = Order.query.filter(Order.order_id == order_id).first()
    if not order:
        return jsonify({"message": "Order not found"}), 404
    expected_delivery_date = order.date + timedelta(days=7)
    order_data = {
        "order_id": order.order_id,
        "date": order.date,
        "expected_delivery_date": expected_delivery_date,
        "customer_id": order.customer_id,
        "status": "In progress"  
    }
    return jsonify(order_data)

@app.route("/cancel_order/<int:order_id>", methods=["DELETE"]) # This is a bonus option (Cancel Order)
def cancel_order(order_id):
    order = Order.query.filter(Order.order_id == order_id).first()
    if not order:
        return jsonify({"message": "Order not found"}), 404
    if order_id not in dir(order):
        return jsonify({"message": "Order id not found"}), 500
    if order_id in ["Shipped", "Completed"]:
        return jsonify({"message": "Cannot cancel order. It has already been shipped or completed."}), 400
    db.session.delete(order)
    db.session.commit()
    return jsonify({"message": "Order canceled successfully"}), 200


# Customer

class Customer(Base):
    __tablename__ = "Customers"
    customer_id: Mapped[int] = mapped_column(autoincrement = True, primary_key = True)
    name: Mapped[str] = mapped_column(String(255), nullable = False)
    email: Mapped[str] = mapped_column(String(320), nullable = False)
    phone: Mapped[str] = mapped_column(String(15), nullable = False)
    customer_account: Mapped["CustomerAccount"] = relationship(back_populates = "customer")
    orders: Mapped[List["Order"]] = relationship("Order", back_populates = "customer")
    
class CustomerSchema(ma.Schema):
    customer_id = fields.Integer(required = False)
    name = fields.String(required = True)
    email = fields.String(required = True)
    phone = fields.String(required = True)

    class Meta:
        fields = ("customer_id", "name", "email", "phone")

customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many = True) 

@app.route("/customers", methods = ["GET"])
def get_customers():
    query = select(Customer) 
    result = db.session.execute(query).scalars() 
    print(result)
    customers = result.all() 
    return customers_schema.jsonify(customers)

@app.route("/customers/<int:customer_id>", methods=["GET"])
def get_customer_per_id(customer_id):
    customer = Customer.query.filter(Customer.customer_id == customer_id).first()
    if customer:
        return customer_schema.jsonify(customer)
    else:
        return jsonify({"message": "Customer could not be found with that customer ID"}), 404


@app.route("/customers", methods = ["POST"])
def add_customer():
    try:
        customer_data = customer_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    with Session(db.engine) as session: 
        with session.begin():
            name = customer_data['name']
            email = customer_data['email']
            phone = customer_data['phone']
            new_customer = Customer(name = name, email = email, phone = phone)
            session.add(new_customer)
            session.commit()
    return jsonify({"message": "New customer added successfully"}), 201 

@app.route("/customers/<int:customer_id>", methods=["PUT"]) 
def update_customer(customer_id):
    try:
        customer = Customer.query.filter(Customer.customer_id == customer_id ).first()
        if not customer: 
            return jsonify({"message": "Customer could not be found with that customer ID"}), 404
        customer_data = customer_schema.load(request.json, partial = True)
        for field, value in customer_data.items():
            setattr(customer, field, value)
        db.session.commit()
        return jsonify({"message": "Customer updated successfully"}), 200
    except ValidationError as err:
        return jsonify(err.messages), 400

@app.route("/customers/<int:customer_id>", methods=["DELETE"])
def delete_customer(customer_id):
    customer = Customer.query.filter(Customer.customer_id == customer_id).first()
    if not customer: 
        return jsonify({"message": "Customer could not be found with that customer ID"}), 404
    db.session.delete(customer)
    db.session.commit()
    return jsonify({"message": "Customer deleted successfully."}), 200


# Customer Account
class CustomerAccount(Base):
    __tablename__ = "Customer_Accounts"
    account_id: Mapped[int] = mapped_column(autoincrement = True, primary_key = True)
    username: Mapped[str] = mapped_column(String(255), unique = True, nullable = False)
    password: Mapped[str] = mapped_column(String(255), nullable = False)
    customer_id: Mapped[int] = mapped_column(ForeignKey("Customers.customer_id"))
    customer: Mapped['Customer'] = relationship(back_populates = "customer_account")

class CustomerAccountSchema(ma.Schema):
    account_id = fields.Integer(required = False)
    username = fields.String(required = True)
    password = fields.String(required = True)
    customer_id = fields.Integer(required = True)
    class Meta:
        fields = ("account_id", "username", "password", "customer_id")

customer_account_schema = CustomerAccountSchema()
customer_accounts_schema = CustomerAccountSchema(many = True) 

@app.route("/customer_accounts", methods = ["GET"])
def get_customer_accounts():
    query = select(CustomerAccount) 
    result = db.session.execute(query).scalars() 
    print(result)
    customer_accounts = result.all() 
    return customer_accounts_schema.jsonify(customer_accounts)

@app.route("/customer_accounts", methods = ["POST"])
def add_customer_accounts():
    try:
        customer_accounts_data = customer_account_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    with Session(db.engine) as session: 
        with session.begin():
            username = customer_accounts_data['username']
            password = customer_accounts_data['password']
            customer_id = customer_accounts_data['customer_id']
            new_customer_account = CustomerAccount(username = username, password = password, customer_id = customer_id)
            session.add(new_customer_account)
            session.commit()
    return jsonify({"message": "New customer account added successfully"}), 201 

@app.route("/customer_accounts/<int:customer_account_id>", methods=["PUT"]) 
def update_customer_account(customer_account_id):
    try:
        print(f"Received request to update customer account ID: {customer_account_id}")
        customer_account = CustomerAccount.query.filter(CustomerAccount.account_id == customer_account_id).first()
        if not customer_account: 
            return jsonify({"message": "Customer Account could not be found with that ID"}), 404
        customer_account_data = customer_account_schema.load(request.json, partial=True)
        for field, value in customer_account_data.items():
            setattr(customer_account, field, value)
        db.session.commit()
        return jsonify({"message": "Customer Account updated successfully"}), 200
    except ValidationError as err:
        return jsonify(err.messages), 400

@app.route("/customer_accounts/<int:customer_account_id>", methods=["DELETE"])
def delete_customer_account(customer_account_id):
    print(f"Received request to delete customer account ID: {customer_account_id}")
    customer_account = CustomerAccount.query.filter(CustomerAccount.account_id == customer_account_id).first()
    if not customer_account: 
        return jsonify({"message": "Customer account could not be found with that customer account ID"}), 404
    db.session.delete(customer_account)
    db.session.commit()
    return jsonify({"message": "Customer account deleted successfully."}), 200


if __name__ == "__main__":
    db.create_all()
    app.run(debug=True, port=5001)