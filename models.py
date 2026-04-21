from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class users(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column(db.String(100),unique=True, nullable=False)
    email = db.Column(db.String(100))
    password=db.Column(db.String(255),nullable=False)
    refresh_token=db.Column(db.String(255),nullable=True)
    products=db.relationship('Product',backref='owner',lazy=True)
 
    def __init__(self, name, email,password):
        self.name = name
        self.email = email
        self.password= password

class Product(db.Model):
    product_id=db.Column("id",db.Integer,primary_key=True)
    product_name =db.Column(db.String(100), nullable=False)
    product_price =db.Column(db.Float)
    category = db.Column(db.String(50))
    created_by=db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)




