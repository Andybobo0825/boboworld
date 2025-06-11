from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import Unicode, Numeric, Integer, DateTime, Float

db = SQLAlchemy()

class Product(db.Model):
    __table_args__ = {'schema': 'dbo'} # 如果需要指定 schema
    __tablename__ = 'Product'
    pId = db.Column(Unicode(8), primary_key=True)
    pName = db.Column(Unicode(50))
    brand = db.Column(Unicode(30))
    category = db.Column(Unicode(20))
    price = db.Column(Numeric(10, 2))
    clickTimes = db.Column(Integer)
    review = db.Column(Float)

class Price_History(db.Model):
    __table_args__ = {'schema': 'dbo'} # 如果需要指定 schema
    __tablename__ = 'Price_History'
    pId = db.Column(Unicode(8), primary_key=True)
    prePrice = db.Column(Numeric(10, 2))
    updateTime = db.Column(DateTime, default=datetime.utcnow,primary_key=True)
    storeName = db.Column(Unicode (50))

class Price_Now(db.Model):
    __table_args__ = {'schema': 'dbo'} # 如果需要指定 schema
    __tablename__ = 'Price_Now'
    pId = db.Column(Unicode(8),primary_key=True)
    store = db.Column(Unicode(50))
    updateTime = db.Column(DateTime, default=datetime.utcnow,primary_key=True)
    storePrice = db.Column(Numeric(10, 2))
    storeDiscount = db.Column(Unicode(200))
    storeLink = db.Column(Unicode(200))

class Client(db.Model):
    __table_args__ = {'schema': 'dbo'} # 如果需要指定 schema
    __tablename__ = 'Client'
    cId = db.Column(Unicode(8), primary_key=True)
    cName = db.Column(Unicode(30))
    account = db.Column(Unicode(20), unique=True)
    password_hash = db.Column('password', db.String(255), nullable=False)
    email = db.Column(Unicode(64), unique=True)
    phone = db.Column(Unicode(10), unique=True)
    sex = db.Column(Unicode(14))
    birthday = db.Column(DateTime)

class Client_Favorites(db.Model):
    __table_args__ = {'schema': 'dbo'} # 如果需要指定 schema
    __tablename__ = 'Client_Favorites'
    cId = db.Column(Unicode(8), primary_key=True)
    pId = db.Column(Unicode(8), primary_key=True)

class Good_Review(db.Model):
    __table_args__ = {'schema': 'dbo'} # 如果需要指定 schema
    __tablename__ = 'Good_Review'
    pId = db.Column(Unicode(8),primary_key=True)
    userName = db.Column(Unicode(30))
    date = db.Column(DateTime, default=datetime.utcnow,primary_key=True)
    rating = db.Column(Float)
    reviewText = db.Column(Unicode)