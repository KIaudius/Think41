from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'  # Using SQLite for simplicity
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Models
class User(db.Model):
    __tablename__ = 'UserTable'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    email = db.Column(db.String(200))
    age = db.Column(db.Integer)
    gender = db.Column(db.String(1))
    state = db.Column(db.String(100))
    city = db.Column(db.String(100))
    country = db.Column(db.String(100))
    traffic_source = db.Column(db.String(100))
    created_at = db.Column(db.DateTime)

class DistributionCenter(db.Model):
    __tablename__ = 'DistributionCenter'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)

class Product(db.Model):
    __tablename__ = 'Product'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    brand = db.Column(db.String(100))
    category = db.Column(db.String(100))
    department = db.Column(db.String(50))
    sku = db.Column(db.String(100))
    cost = db.Column(db.Float)
    retail_price = db.Column(db.Float)
    distribution_center_id = db.Column(db.Integer, db.ForeignKey('DistributionCenter.id'))

class InventoryItem(db.Model):
    __tablename__ = 'InventoryItem'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('Product.id'))
    created_at = db.Column(db.DateTime)
    sold_at = db.Column(db.DateTime)
    cost = db.Column(db.Float)
    product_category = db.Column(db.String(100))
    product_name = db.Column(db.String(255))
    product_brand = db.Column(db.String(100))
    product_retail_price = db.Column(db.Float)
    product_department = db.Column(db.String(100))
    product_sku = db.Column(db.String(100))
    product_distribution_center_id = db.Column(db.Integer)

class Order(db.Model):
    __tablename__ = 'OrderTable'
    order_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('UserTable.id'))
    status = db.Column(db.String(50))
    gender = db.Column(db.String(1))
    created_at = db.Column(db.DateTime)
    returned_at = db.Column(db.DateTime)
    shipped_at = db.Column(db.DateTime)
    delivered_at = db.Column(db.DateTime)
    num_of_item = db.Column(db.Integer)

class OrderItem(db.Model):
    __tablename__ = 'OrderItem'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('OrderTable.order_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('UserTable.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('Product.id'))
    inventory_item_id = db.Column(db.Integer, db.ForeignKey('InventoryItem.id'))
    status = db.Column(db.String(50))
    created_at = db.Column(db.DateTime)
    shipped_at = db.Column(db.DateTime)
    delivered_at = db.Column(db.DateTime)
    returned_at = db.Column(db.DateTime)
    sale_price = db.Column(db.Float)

# Routes
@app.route('/api/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([{
        'id': user.id,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
        'age': user.age,
        'gender': user.gender,
        'state': user.state,
        'city': user.city,
        'country': user.country,
        'traffic_source': user.traffic_source,
        'created_at': user.created_at.isoformat() if user.created_at else None
    } for user in users])

@app.route('/api/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    return jsonify([{
        'id': product.id,
        'name': product.name,
        'brand': product.brand,
        'category': product.category,
        'department': product.department,
        'sku': product.sku,
        'cost': product.cost,
        'retail_price': product.retail_price,
        'distribution_center_id': product.distribution_center_id
    } for product in products])

@app.route('/api/orders', methods=['GET'])
def get_orders():
    orders = Order.query.all()
    return jsonify([{
        'order_id': order.order_id,
        'user_id': order.user_id,
        'status': order.status,
        'gender': order.gender,
        'created_at': order.created_at.isoformat() if order.created_at else None,
        'returned_at': order.returned_at.isoformat() if order.returned_at else None,
        'shipped_at': order.shipped_at.isoformat() if order.shipped_at else None,
        'delivered_at': order.delivered_at.isoformat() if order.delivered_at else None,
        'num_of_item': order.num_of_item
    } for order in orders])

@app.route('/api/order-items', methods=['GET'])
def get_order_items():
    order_items = OrderItem.query.all()
    return jsonify([{
        'id': item.id,
        'order_id': item.order_id,
        'user_id': item.user_id,
        'product_id': item.product_id,
        'inventory_item_id': item.inventory_item_id,
        'status': item.status,
        'created_at': item.created_at.isoformat() if item.created_at else None,
        'shipped_at': item.shipped_at.isoformat() if item.shipped_at else None,
        'delivered_at': item.delivered_at.isoformat() if item.delivered_at else None,
        'returned_at': item.returned_at.isoformat() if item.returned_at else None,
        'sale_price': item.sale_price
    } for item in order_items])

@app.route('/api/distribution-centers', methods=['GET'])
def get_distribution_centers():
    centers = DistributionCenter.query.all()
    return jsonify([{
        'id': center.id,
        'name': center.name,
        'latitude': center.latitude,
        'longitude': center.longitude
    } for center in centers])

@app.route('/api/inventory-items', methods=['GET'])
def get_inventory_items():
    items = InventoryItem.query.all()
    return jsonify([{
        'id': item.id,
        'product_id': item.product_id,
        'created_at': item.created_at.isoformat() if item.created_at else None,
        'sold_at': item.sold_at.isoformat() if item.sold_at else None,
        'cost': item.cost,
        'product_category': item.product_category,
        'product_name': item.product_name,
        'product_brand': item.product_brand,
        'product_retail_price': item.product_retail_price,
        'product_department': item.product_department,
        'product_sku': item.product_sku,
        'product_distribution_center_id': item.product_distribution_center_id
    } for item in items])

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
