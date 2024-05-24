from flask import Flask, jsonify, request 
from flask_cors import CORS 
from flask_sqlalchemy import SQLAlchemy 
from sqlalchemy.orm import Mapped, mapped_column, relationship, Session, MappedCollection, mapper
from sqlalchemy import select, ForeignKey, delete, Column, String, Integer, Table, Float, Date 
from sqlalchemy.ext.declarative import declarative_base
from flask_marshmallow import Marshmallow 
from marshmallow import fields, validate, ValidationError
from typing import List
from datetime import datetime, timedelta, date

# Mini Project: E-commerce API

# In today's digital age, online shopping has become an integral part of our lives.
# E-commerce platforms have revolutionized the way we purchase products, offering convenience, variety, and accessibility like never before.
# However, building a robust e-commerce application from scratch can be a complex task, involving various components such as user management, product listings, shopping carts, and order processing.

# Imagine you are tasked with creating an e-commerce application that empowers both customers and administrators.
# The goal is to build a user-friendly platform where customers can effortlessly browse products, add them to their shopping carts, and place orders.
# Simultaneously, administrators should have tools to manage product inventory, track orders, and ensure a seamless shopping experience.

# To tackle this challenge, we will leverage the power of Python and two essential libraries:
    # Flask and Flask-SQLAlchemy.
        # Flask is a lightweight web framework that simplifies web application development
        # Flask-SQLAlchemy provides a robust toolkit for database interactions.
        # Together, they form the perfect duo to craft our e-commerce solution.

# In this project, we will guide you through the process of building an e-commerce application that closely mimics real-world scenarios.

# Project Requirements

# To successfully build our e-commerce application and achieve the learning objectives, we need to establish clear project requirements.
# These requirements outline the key features and functionalities that our application must encompass.
# Below, you'll find a comprehensive list of project requirements based on our learning objectives:
    # 💡 **Note:** We've already developed key functionalities for our e-commerce project in the "Module 6: API REST Development" lessons, including models, schemas, and endpoints for Customers and Products.
    # To save time and maintain consistency, consider reusing the Flask-SQLAlchemy project as a foundation for Orders and Shopping Cart components.
    # This approach ensures a unified and efficient codebase, making it easier to integrate new features into the existing solution.
    
    # 1. Customer and CustomerAccount Management:
        # Create the CRUD (Create, Read, Update, Delete) endpoints for managing Customers and their associated CustomerAccounts:
            
        # Create Customer: Implement an endpoint to add a new customer to the database. Ensure that you capture essential customer information, including name, email, and phone number.
        # Read Customer: Develop an endpoint to retrieve customer details based on their unique identifier (ID). Provide functionality to query and display customer information.
        # Update Customer: Create an endpoint for updating customer details, allowing modifications to the customer's name, email, and phone number.
        # Delete Customer: Implement an endpoint to delete a customer from the system based on their ID.
    
        # Create CustomerAccount: Develop an endpoint to create a new customer account. This should include fields for a unique username and a secure password.
        # Read CustomerAccount: Implement an endpoint to retrieve customer account details, including the associated customer's information.
        # Update CustomerAccount: Create an endpoint for updating customer account information, including the username and password.
        # Delete CustomerAccount: Develop an endpoint to delete a customer account.
    
    # 2. Product Catalog: Create the CRUD (Create, Read, Update, Delete) endpoints for managing Products:
        # Create Product: Implement an endpoint to add a new product to the e-commerce database. Capture essential product details, such as the product name and price.
        # Read Product: Develop an endpoint to retrieve product details based on the product's unique identifier (ID). Provide functionality to query and display product information.
        # Update Product: Create an endpoint for updating product details, allowing modifications to the product name and price.
        # Delete Product: Implement an endpoint to delete a product from the system based on its unique ID.
        # List Products: Develop an endpoint to list all available products in the e-commerce platform. Ensure that the list provides essential product information.
            # View and Manage Product Stock Levels (Bonus): Create an endpoint that allows to view and manage the stock levels of each product in the catalog. Administrators should be able to see the current stock level and make adjustments as needed.
            # Restock Products When Low (Bonus): Develop an endpoint that monitors product stock levels and triggers restocking when they fall below a specified threshold. Ensure that stock replenishment is efficient and timely.
    
    # 3. Order Processing: Develop comprehensive Orders Management functionality to efficiently handle customer orders, ensuring that customers can place, track, and manage their orders seamlessly.
        # Place Order: Create an endpoint for customers to place new orders, specifying the products they wish to purchase and providing essential order details. Each order should capture the order date and the associated customer.
        # Retrieve Order: Implement an endpoint that allows customers to retrieve details of a specific order based on its unique identifier (ID). Provide a clear overview of the order, including the order date and associated products.
        # Track Order: Develop functionality that enables customers to track the status and progress of their orders. Customers should be able to access information such as order dates and expected delivery dates.
            # Manage Order History (Bonus): Create an endpoint that allows customers to access their order history, listing all previous orders placed. Each order entry should provide comprehensive information, including the order date and associated products.
            # Cancel Order (Bonus): Implement an order cancellation feature, allowing customers to cancel an order if it hasn't been shipped or completed. Ensure that canceled orders are appropriately reflected in the system.
            # Calculate Order Total Price (Bonus): Include an endpoint that calculates the total price of items in a specific order, considering the prices of the products included in the order. This calculation should be specific to each customer and each order, providing accurate pricing information.

    # 4. Database Integration:
        # Utilize Flask-SQLAlchemy to integrate a MySQL database into the application.
        # Design and create the necessary Model to represent customers, orders, products, customer accounts, and any additional features.
        # Establish relationships between tables to model the application's core functionality.
        # Ensure proper database connections and interactions for data storage and retrieval.

    # 5. (BONUS) Data Validation and Error Handling:
        # Implement data validation mechanisms to ensure that user inputs meet specified criteria (e.g., valid email addresses, proper formatting).
        # Use try, except, else, and finally blocks to handle errors gracefully and provide informative error messages to guide users.

    # 6. User Interface (Postman):
        # Develop Postman collections that categorize and group API requests according to their functionality. Separate collections for Customer Management, Product Management, Order Management, and Bonus Features should be created for clarity.

    # 7. GitHub Repository:
        # Create a GitHub repository for the project and commit code regularly.
        # Maintain a clean and interactive README.md file in the GitHub repository, providing clear instructions on how to run the application and explanations of its features.
        # Include a link to the GitHub repository in the project documentation.

app = Flask(__name__)
cors = CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+mysqlconnector://root:Hammond45!@localhost/e_commerce_db2"
app.json.sort_keys = False
db = SQLAlchemy(app)
ma = Marshmallow(app)
Base = declarative_base(cls = db.Model)
with app.app_context(): # What is this? Where does this go???
    db.create_all()
class OrderProduct(Base): 
    __tablename__ = "Order_Product",
    order_id: Mapped[int] = mapped_column(ForeignKey('Orders.order_id'), primary_key = True)
    product_id: Mapped[int] = mapped_column(ForeignKey('Products.product_id'), primary_key = True)

class OrderProductSchema(ma.Schema):
    order_id = fields.Integer(required = True)
    product_id = fields.Integer(required = False)
    
    class Meta:
        fields = ("order_id", "product_id")

order_product_schema = OrderProductSchema()
order_products_schema = OrderProductSchema(many = True) 

class Product(Base):
    __tablename__ = "Products"
    product_id: Mapped[int] = mapped_column(autoincrement = True, primary_key = True)
    name: Mapped[str] = mapped_column(String(255), nullable = False)
    price: Mapped[float] = mapped_column(Float, nullable = False)
    orders: Mapped["OrderProduct"] = relationship("OrderProduct")

class ProductSchema(ma.Schema):
    product_id = fields.Integer(required = False)
    name = fields.String(required = True)
    price = fields.Float(required = True)

    class Meta:
        fields = ("product_id", "name", "price")

product_schema = ProductSchema()
products_schema = ProductSchema(many = True) 

@app.route("/products", methods = ["GET"])
def get_products():
    query = select(Product) 
    result = db.session.execute(query).scalars() 
    print(result)
    products = result.all() 
    return product_schema.jsonify(products)

@app.route("/products/name_of_product/<string:name>", methods=["GET"])
def get_product_per_name(name):
    product = Product.query.filter_by(name=name).first()
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

@app.route("/products/<int:id>", methods=["PUT"]) # Want to see how Ryan does this... not sure this is correct 
def update_product(id):
    try:
        product = Product.query.get(id)
        if not product: 
            return jsonify({"message": "Product could not be found with that product ID"}), 404
        product_data = product_schema.load(request.json, partial = True)
        for key, value in product_data.items():
            setattr(product, key, value)
        db.session.commit()
        return jsonify({"message": "Product updated successfully"}), 200
    except ValidationError as err:
        return jsonify(err.messages), 400

@app.route("/products/<int:id>", methods=["DELETE"])
def delete_product(id):
    product = Product.query.get(id)
    if not product: 
        return jsonify({"message": "Product could not be found with that product ID"}), 404
    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": "Product deleted successfully."}), 200

@app.route("/restock_products", methods=["POST"]) # This is a bonus option 
def restock_products():
    threshold = request.json.get("threshold", 10) 
    products_to_restock = []
    low_stock_products = Product.query.filter(Product.stock < threshold).all()
    for product in low_stock_products:
        product.stock += 20 
        products_to_restock.append(product)
    db.session.commit()
    return products_schema.jsonify(products_to_restock)




class Order(Base):
    __tablename__ = "Orders"
    order_id: Mapped[int] = mapped_column(autoincrement = True, primary_key = True)
    date: Mapped[datetime.date] = mapped_column(Date, nullable = False)
    customer_id: Mapped[int] = mapped_column(Integer, ForeignKey('Customers.customer_id'))
    customer: Mapped['Customer'] = relationship("Customer", back_populates = "orders")
    products: Mapped[List["Product"]] = relationship("Product", secondary = "Order_product")
    
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
    return order_schema.jsonify(orders)

@app.route("/orders/<int:customer_id>", methods=["GET"])
def get_order_per_customer_id(customer_id):
    orders = Order.query.filter_by(customer_id=customer_id).all() 
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
            new_order = CustomerAccount(date = date, customer_id = customer_id)
            session.add(new_order)
            session.commit()
    return jsonify({"message": "New order added successfully"}), 201 

@app.route("/orders/<int:id>", methods=["PUT"]) # Want to see how Ryan does this... not sure this is correct 
def update_order(id):
    try:
        order = Order.query.get(id)
        if not order: 
            return jsonify({"message": "Order could not be found with that order ID"}), 404
        order_data = order_schema.load(request.json, partial = True)
        for key, value in order_data.items():
            setattr(order, key, value)
        db.session.commit()
        return jsonify({"message": "Order updated successfully"}), 200
    except ValidationError as err:
        return jsonify(err.messages), 400

@app.route("/orders/<int:id>", methods=["DELETE"])
def delete_order(id):
    order = Order.query.get(id)
    if not order: 
        return jsonify({"message": "Order could not be found with that order ID"}), 404
    db.session.delete(order)
    db.session.commit()
    return jsonify({"message": "Order deleted successfully."}), 200

@app.route("/track_order/<int:order_id>", methods=["GET"]) 
def track_order(order_id):
    order = Order.query.get(order_id)
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

@app.route("/cancel_order/<int:order_id>", methods=["DELETE"]) #This is a bonus option
def cancel_order(order_id):
    order = Order.query.get(order_id)
    if not order:
        return jsonify({"message": "Order not found"}), 404
    if order.status in ["Shipped", "Completed"]:
        return jsonify({"message": "Cannot cancel order. It has already been shipped or completed."}), 400
    db.session.delete(order)
    db.session.commit()
    return jsonify({"message": "Order canceled successfully"}), 200







class Customer(Base):
    __tablename__ = "Customers"
    customer_id: Mapped[int] = mapped_column(autoincrement = True, primary_key = True)
    name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(320))
    phone: Mapped[str] = mapped_column(String(15))
    customer_account: Mapped["CustomerAccount"] = relationship(back_populates = "customer")
    # orders: Mapped[List["Order"]] = db.relationship(back_populates = "customer")
    orders: MappedCollection = mapped_column([])
    
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

@app.route("/customers/<int:id>", methods=["GET"])
def get_customer_per_id(id):
    customer = Customer.query.filter_by(customer_id=id).first()
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

@app.route("/customers/<int:customer_id>", methods=["PUT"]) # Want to see how Ryan does this... not sure this is correct 
def update_customer(customer_id):
    try:
        customer = Customer.query.filter(Customer.customer_id == customer_id ).first()
        # result = session.execute(query).scalars().first() 
        # customer = Customer.query.get(customer_id)
        if not customer: 
            return jsonify({"message": "Customer could not be found with that customer ID"}), 404
        customer_data = customer_schema.load(request.json, partial = True)
        for field, value in customer_data.items():
            setattr(customer, field, value)
        db.session.commit()
        return jsonify({"message": "Customer updated successfully"}), 200
    except ValidationError as err:
        return jsonify(err.messages), 400

@app.route("/customers/<int:id>", methods=["DELETE"])
def delete_customer(id):
    customer = Customer.query.get(id)
    if not customer: 
        return jsonify({"message": "Customer could not be found with that customer ID"}), 404
    db.session.delete(customer)
    db.session.commit()
    return jsonify({"message": "Customer deleted successfully."}), 200






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
    return customer_account_schema.jsonify(customer_accounts)

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

@app.route("/customer_accounts/<int:id>", methods=["PUT"]) # Want to see how Ryan does this... not sure this is correct 
def update_customer_account(id):
    try:
        customer_account = CustomerAccount.query.get(id)
        if not customer_account: 
            return jsonify({"message": "Customer Account could not be found with that ID"}), 404
        customer_account_data = customer_account_schema.load(request.json, partial = True)
        for key, value in customer_account_data.items():
            setattr(customer_account, key, value)
        db.session.commit()
        return jsonify({"message": "Customer Account updated successfully"}), 200
    except ValidationError as err:
        return jsonify(err.messages), 400

@app.route("/customer_accounts/<int:id>", methods=["DELETE"])
def delete_customer_account(id):
    customer_account = CustomerAccount.query.get(id)
    if not customer_account: 
        return jsonify({"message": "Customer account could not be found with that customer account ID"}), 404
    db.session.delete(customer_account)
    db.session.commit()
    return jsonify({"message": "Customer account deleted successfully."}), 200



mapper(Order, Table("Orders", Base.metadata, autoload = True))
mapper(Product, Table("Products", Base.metadata, autoload = True))
mapper(Customer, Table("Customers", Base.metadata, autoload = True))
mapper(CustomerAccount, Table("Customer_Accounts", Base.metadata, autoload = True))
mapper(OrderProduct, Table("Order_Product", Base.metadata, autoload = True))


if __name__ == "__main__":
    app.run(debug = True, port = 5001)