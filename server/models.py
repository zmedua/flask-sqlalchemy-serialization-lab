from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.ext.associationproxy import association_proxy
from marshmallow import Schema, fields
from sqlalchemy_serializer import SerializerMixin

metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)


class Customer(db.Model, SerializerMixin):
    __tablename__ = 'customers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    reviews = db.relationship("Review", back_populates="customer")
    items = association_proxy("reviews", "item")

    serialize_rules = ("-reviews.customer", "-items.customers", "-items.reviews")
    def __repr__(self):
        return f'<Customer {self.id}, {self.name}>'


class Item(db.Model, SerializerMixin):
    __tablename__ = 'items'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    price = db.Column(db.Float)

    reviews = db.relationship("Review", back_populates="item")
    serialize_rules =("-reviews.item", "-reviews.customer.items")
    def __repr__(self):
        return f'<Item {self.id}, {self.name}, {self.price}>'

class Review(db.Model, SerializerMixin):
    __tablename__ = "reviews"

    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.String)

    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"))
    item_id = db.Column(db.Integer, db.ForeignKey("items.id"))

    customer = db.relationship("Customer", back_populates="reviews")
    item = db.relationship("Item", back_populates="reviews")

    serialize_rules = ("-customer.reviews", "-item.reviews")
    def __repr__(self):
        return f"<review {self.id}, Customer {self.customer_id}, Item {self.item_id}>"

class CustomerSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    reviews = fields.Nested("ReviewSchema", many=True, exclude=("customer",))

class ItemSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    price = fields.Float()
    reviews = fields.Nested("ReviewSchema", many=True, exclude=("item",))

class ReviewSchema(Schema):
    id = fields.Int()
    comment = fields.Str()
    customer = fields.Nested("CustomerSchema", exclude=("reviews",))
    item = fields.Nested("ItemSchema", exclude=("reviews",))