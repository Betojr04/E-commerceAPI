from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import (
    String,
    ForeignKey,
    DateTime,
    Integer,
    Float,
    Table,
    Column,
    select,
)
from datetime import datetime
from flask_marshmallow import Marshmallow
from marshmallow import ValidationError, fields, validate
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from typing import List
import os

app = Flask(__name__)


"""========== CONFIGURATION =========="""


app.config["SQLALCHEMY_DATABASE_URI"] = (
    "mysql+mysqlconnector://root:@localhost/ecommerce_api"
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


class Base(DeclarativeBase):
    pass


# Initialize SQLAlchemy and Marshmallow
db = SQLAlchemy(model_class=Base)
db.init_app(app)
ma = Marshmallow(app)


"""========= ASSOCIATION TABLE =========="""


order_product_table = Table(
    "order_product",
    Base.metadata,
    Column("order_id", Integer, ForeignKey("orders.id"), primary_key=True),
    Column("product_id", Integer, ForeignKey("products.id"), primary_key=True),
)


"""========== TABLES =========="""


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(30), nullable=False)
    email: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)

    # one to many declaration
    orders: Mapped[List["OrderTable"]] = relationship(
        back_populates="owner", cascade="all, delete-orphan"
    )


class OrderTable(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )

    # many to one relationship declaration
    owner: Mapped["User"] = relationship(back_populates="orders")

    products: Mapped[List["ProductTable"]] = relationship(
        secondary="order_product", back_populates="orders"
    )


class ProductTable(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    product_name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    price: Mapped[float] = mapped_column(nullable=False)
    category_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("categories.id"), nullable=False
    )

    categories: Mapped["CategoryTable"] = relationship(back_populates="products")

    orders: Mapped[List["OrderTable"]] = relationship(
        secondary="order_product", back_populates="products"
    )


class CategoryTable(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    category_name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)

    products: Mapped[List["ProductTable"]] = relationship(
        back_populates="categories", cascade="all, delete-orphan"
    )


"""========= SCHEMAS =========="""


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        include_relationships = True
        # this is like putting the json back into python objects, deserializing
        # load_instance = True

    name = fields.Str(required=True, validate=validate.Length(min=1))
    email = fields.Email(required=True)


class OrderSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = OrderTable
        include_relationships = True
        # load_instance = True

        order_date = fields.DateTime(dump_only=True)

        user_id = fields.Int(required=True)


class ProductSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ProductTable
        include_relationships = False
        # load_instance = True

    product_name = fields.Str(required=True)
    price = fields.Float(
        required=True, validate=validate.Range(min=0, error="Price must be positive!")
    )
    category_id = fields.Int(required=True)


class CategorySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = CategoryTable
        include_reationships = True
        # load_instance = True

    category_name = fields.Str(required=True)


user_schema = UserSchema()
users_schema = UserSchema(many=True)

order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)

product_schema = ProductSchema()
products_schema = ProductSchema(many=True)

category_schema = CategorySchema()
categories_schema = CategorySchema(many=True)

"""
========== USER ROUTES ==========
"""


# ROUTE TO CREATE A NEW USER


@app.route("/users", methods=["POST"])
def create_user():
    try:
        # this below is also deserializing the data
        # you have to have this line exactly if you do not have load_instance
        # set to true inside of the schema above
        # if you do have it then this line below is necessary
        # user_data = requeset.json
        user_data = user_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    try:
        new_user = User(name=user_data["name"], email=user_data["email"])
        db.session.add(new_user)
        db.session.commit()
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return user_schema.jsonify(new_user), 201


# ROUTE TO RETRIEVE ALL USERS


@app.route("/users", methods=["GET"])
def get_users():
    try:

        query = select(User)
        users = db.session.execute(query).scalars().all()
        # this line above means
        # "Go to the database, get all the User records, clean them up, and store them in a list called users."
        for user in users:
            print(f"User Id: {user.id}, Name: {user.name}, Email: {user.email}")
    except ValidationError as e:
        return jsonify(e.messages), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    return users_schema.jsonify(users), 200


# ROUTE TO RETRIEVE SINGLE USER


@app.route("/user/<int:id>", methods=["GET"])
def get_user(id):
    user = db.session.get(User, id)
    return user_schema.jsonify(user), 200


# ROUTE TO UPDATE A USER


@app.route("/user/<int:id>", methods=["PUT"])
def update_user(id):
    user = db.session.get(User, id)

    if not user:
        return jsonify(e.messages), 400

    try:
        user_data = user_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.nessages), 400

    user.name = user_data["name"]
    user.email = user_data["email"]

    db.session.commit()

    return user_schema.jsonify(user), 200


# ROUTE TO DELETE A USER


@app.route("/user/<int:id>", methods=["DELETE"])
def delete_user(id):
    user = db.session.get(User, id)

    if not user:
        return jsonify({"message": "Invalid user id"}), 400

    db.session.delete(user)
    db.session.commit()

    return jsonify({"message": f"successfully deleted user: {id}, {user.name}"}), 200


"""
========== CATEGORY ROUTES ==========
"""

# ROUTE TO ADD A CATEGORY


@app.route("/category", methods=["POST"])
def add_category():
    try:
        category_data = category_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    try:
        new_category = CategoryTable(category_name=category_data["category_name"])

        db.session.add(new_category)
        db.session.commit()
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return category_schema.jsonify(new_category), 201


# ROUTE TO RETREIVE ALL CATEGORIES
@app.route("/categories", methods=["GET"])
def get_categories():
    try:
        query = select(CategoryTable)
        categories = db.session.execute(query).scalars().all()

        for category in categories:
            print(
                f"Category Id: {category.id}, Category Name: {category.category_name}"
            )
    except ValidationError as e:
        return jsonify(e.messages), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return categories_schema.jsonify(categories), 200


# RETRIEVE A SINGLE PRODUCT
@app.route("/category/<int:id>", methods=["GET"])
def get_category(id):
    category = db.session.get(CategoryTable, id)

    return category_schema.jsonify(category), 200


# ROUTE TO UPDATE A CATEGORY
@app.route("/category/<int:id>", methods=["PUT"])
def udpate_category(id):
    category = db.session.get(CategoryTable, id)

    if not category:
        return jsonify(e.messages), 400

    try:
        category_data = category_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.nessages), 400

    category.category_name = category_data["category_name"]

    db.session.commit()
    return user_schema.jsonify(category), 200


# DELETE A CATEGORY
@app.route("/category/<int:id>", methods=["DELETE"])
def delete_category(id):
    category = db.session.get(CategoryTable, id)

    if not category:
        return jsonify({"message": "Invalid Category"}), 400

    db.session.delete(category)
    db.session.commit()

    return jsonify(
        {"message": f"successfully deleted category: {id}, {category.category_name}"}
    )


"""
========== PRODUCT ROUTES ==========
"""


# ROUTE TO CREATE A NEW PRODUCT
@app.route("/product", methods=["POST"])
def add_product():
    try:
        product_data = product_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    try:
        # this is looking for the category you are inputting as well to make sure you are adding a product into the correct category
        category_id = product_data.get("category_id")
        category = db.session.get(CategoryTable, category_id)

        if not category:
            return jsonify({"error": "Category not found"}), 400

        # this then adds the new product
        new_product = ProductTable(
            product_name=product_data["product_name"],
            price=product_data["price"],
            category_id=category.id,
        )

        db.session.add(new_product)
        db.session.commit()
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return product_schema.jsonify(new_product), 201


# ROUTE TO RETRIEVE ALL PRODUCTS
@app.route("/products", methods=["GET"])
def get_products():
    try:
        query = select(ProductTable)
        products = db.session.execute(query).scalars().all()

        for product in products:
            print(
                f"Product Id: {product.id}, Name: {product.product_name}, Price: {product.price}"
            )

    except ValidationError as e:
        return jsonify(e.messages), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    return products_schema.jsonify(products), 200


# ROUTES FOR RETRIEVING SINGLE PRODUCT
@app.route("/product/<int:id>", methods=["GET"])
def get_product(id):
    user = db.session.get(ProductTable, id)
    return product_schema.jsonify(user), 200


# ROUTE FOR UPDATING A PRODUCT
@app.route("/product/<int:id>", methods=["PUT"])
def update_product(id):
    product = db.session.get(ProductTable, id)

    if not product:
        return jsonify({"error": "Product not found"}), 404

    try:
        product_data = product_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    product.product_name = product_data["product_name"]
    product.price = product_data["price"]
    product.category_id = product_data["category_id"]

    db.session.commit()

    return product_schema.jsonify(product), 200


# ROUTE FOR DELETING A PRODUCT
@app.route("/product/<int:id>", methods=["DELETE"])
def delete_product(id):
    product = db.session.get(ProductTable, id)

    if not product:
        return jsonify({"message": "Invalid Product"}), 400

    db.session.delete(product)
    db.session.commit()

    return jsonify(
        {"message": f"successfully deleted category: {id}, {product.product_name}"}
    )


"""
========== ORDER ROUTES ==========
"""


@app.route("/orders", methods=["POST"])
def create_order():
    try:
        order_data = request.json

        user_id = order_data.get("user_id")
        user = db.session.get(User, user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404

        product_ids = order_data.get("product_ids", [])
        if not product_ids:
            return jsonify({"error": "At least one product is required"}), 400

        products = (
            db.session.query(ProductTable)
            .filter(ProductTable.id.in_(product_ids))
            .all()
        )
        if len(products) != len(product_ids):
            return jsonify({"error": "One or more products do not exist"}), 404

        new_order = OrderTable(user_id=user_id)
        new_order.products.extend(products)
        db.session.add(new_order)
        db.session.commit()

        return order_schema.jsonify(new_order), 201

    except ValidationError as e:
        return jsonify(e.messages), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ROUTE FOR RETRIEVING ALL ORDERS
@app.route("/orders", methods=["GET"])
def get_orders():
    try:
        query = select(OrderTable)
        orders = db.session.execute(query).scalars().all()

        for order in orders:
            print(f"Order Id: {order.id}, Order Date: {order.order_date}")

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return orders_schema.jsonify(orders), 200


# ROUTE FOR RETRIEVING A SINGLE ORDER
@app.route("/order/<int:id>", methods=["GET"])
def get_order(id):
    order = db.session.get(OrderTable, id)

    if not order:
        return jsonify({"error": "Order not found"}), 404

    return order_schema.jsonify(order), 200


# ROUTE FOR UPDATING AN ORDER
@app.route("/order/<int:id>", methods=["PUT"])
def update_order(id):
    order = db.session.get(OrderTable, id)

    if not order:
        return jsonify({"error": "Order not found"}), 404

    try:
        order_data = order_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    user_id = order_data.get("user_id")
    user = db.session.get(User, user_id)

    if not user:
        return jsonify({"error": "User not found"}), 400

    order.user_id = user.id

    db.session.commit()

    return order_schema.jsonify(order), 200


# ROUTE FOR DELETING AN ORDER
@app.route("/order/<int:id>", methods=["DELETE"])
def delete_order(id):
    order = db.session.get(OrderTable, id)

    if not order:
        return jsonify({"error": "Order not found"}), 404

    db.session.delete(order)
    db.session.commit()

    return jsonify({"message": f"Successfully deleted order: {id}"}), 200


# Starting the app

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
