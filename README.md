**📝 Module 3 Project | Building an E-commerce API with Flask, SQLAlchemy, Marshmallow, and MySQL

### OVERVIEW

In this assignment, you will create a fully functional e-commerce API using Flask, Flask-SQLAlchemy, Flask-Marshmallow, and MySQL. The API will manage Users, Orders, and Products with proper relationships, including One-to-Many and Many-to-Many associations. You will also learn to set up a MySQL database, define models, implement serialization with Marshmallow, and develop RESTful CRUD endpoints.

---

## 🎯 LEARNING OBJECTIVES

* Database Design: Create models with relationships in SQLAlchemy and MySQL.
* API Development: Develop a RESTful API with CRUD operations using Flask.
* Serialization: Use Marshmallow schemas for input validation and data serialization.
* Testing: Ensure the API is fully functional using Postman and MySQL Workbench.

---

## 🗂 RELATIONSHIPS

* One User → Many Orders (One-to-Many): A user can place multiple orders.
* Many Orders ←→ Many Products (Many-to-Many): An order can contain multiple products, and a product can belong to multiple orders. (This will require an association table.)

---

## 🔧 REQUIREMENTS

### Set Up MySQL Database

1. Open MySQL Workbench.
2. Create a new database named ecommerce_api.

### Install Dependencies and Initialize Flask App

Set up a virtual environment:

python3-mvenvvenv

Activate the virtual environment:	

Mac/Linux:sourcevenv/bin/activate

Windows:venv\Scripts\activate

Install dependencies:

pipinstallFlaskFlask-SQLAlchemyFlask-Marshmallowmarshmallow-sqlalchemymysql-connector-python

### Configure App with Database URI

Update the SQLAlchemy URI in your app.py file:

app.config['SQLALCHEMY_DATABASE_URI']= 'mysql+mysqlconnector://root:`<YOUR PASSWORD>`@localhost/ecommerce_api'

---

## 🗃 DATABASE MODELS

Create the following tables in SQLAlchemy:

### User Table

* id: Integer, primary key, auto-increment
* name: String
* address: String
* email: String (must be unique)

### Order Table

* id: Integer, primary key, auto-increment
* order_date: DateTime (learn to use DateTime in SQLAlchemy)
* user_id: Integer, foreign key referencing User

### Product Table

* id: Integer, primary key, auto-increment
* product_name: String
* price: Float

### Order_Product Association Table

* order_id: Integer, foreign key referencing Order
* product_id: Integer, foreign key referencing Product

Ensure this association table prevents duplicate entries for the same product in an order.

---

## 📦 MARSHMALLOW SCHEMAS

Implement the following Marshmallow schemas for serialization and validation:

* UserSchema
* OrderSchema
* ProductSchema

Include appropriate fields and validation for each schema.

## 🚀 IMPLEMENT CRUD ENDPOINTS

Develop the following RESTful endpoints:

### User Endpoints

* GET /users: Retrieve all users
* GET /users/`<id>`: Retrieve a user by ID
* POST /users: Create a new user
* PUT /users/`<id>`: Update a user by ID
* DELETE /users/`<id>`: Delete a user by ID

### Product Endpoints

* GET /products: Retrieve all products
* GET /products/`<id>`: Retrieve a product by ID
* POST /products: Create a new product
* PUT /products/`<id>`: Update a product by ID
* DELETE /products/`<id>`: Delete a product by ID

### Order Endpoints

* POST /orders: Create a new order (requires user ID and order date)
* GET /orders/<order_id>/add_product/<product_id>: Add a product to an order (prevent duplicates)
* DELETE /orders/<order_id>/remove_product: Remove a product from an order
* GET /orders/user/<user_id>: Get all orders for a user
* GET /orders/<order_id>/products: Get all products for an order

---

## 🧪 TESTING

* Run Database Setup: Ensure that calling db.create_all() creates all required tables in MySQL.
* Use Postman: Test each endpoint to confirm they work as expected.
* Verify Data: Use MySQL Workbench to ensure data is being correctly stored in the database.

---

## 📋 DELIVERABLES

Submit a Python script containing:

* Database models for Users, Orders, Products, and Order_Product association.
* Fully functional CRUD endpoints for users, products, and orders.
* Validated and serialized data using Marshmallow schemas.

---

## 🚀 BONUS TASKS (Optional):

* Add additional endpoints for advanced order management.
* Implement pagination for user or product listings.
* Add JWT authentication for user operations.

---

## 📥 HOW TO SUBMIT

* Submit your completed Python script via Google Classroom in a GitHub Repository.
* Ensure all endpoints are functional, and data is correctly stored in MySQL.

**
