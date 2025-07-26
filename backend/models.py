from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from enum import Enum

db = SQLAlchemy()

class MessageType(Enum):
    USER = "user"
    AI = "ai"

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

    # Relationships
    conversation_sessions = db.relationship('ConversationSession', backref='user', lazy=True)
    orders = db.relationship('Order', backref='user', lazy=True)

class DistributionCenter(db.Model):
    __tablename__ = 'DistributionCenter'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)

    # Relationships
    products = db.relationship('Product', backref='distribution_center', lazy=True)

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

    # Relationships
    inventory_items = db.relationship('InventoryItem', backref='product', lazy=True)
    order_items = db.relationship('OrderItem', backref='product', lazy=True)

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

    # Relationships
    order_items = db.relationship('OrderItem', backref='inventory_item', lazy=True)

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

    # Relationships
    order_items = db.relationship('OrderItem', backref='order', lazy=True)

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

# NEW MODELS FOR MILESTONE 3

class ConversationSession(db.Model):
    __tablename__ = 'ConversationSession'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('UserTable.id'), nullable=False)
    title = db.Column(db.String(255))  # Optional title for the conversation
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)  # To mark sessions as active/inactive

    # Relationships
    messages = db.relationship('ChatMessage', backref='session', lazy=True, order_by='ChatMessage.created_at')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_active': self.is_active,
            'message_count': len(self.messages)
        }

class ChatMessage(db.Model):
    __tablename__ = 'ChatMessage'
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('ConversationSession.id'), nullable=False)
    message_type = db.Column(db.String(10), nullable=False)  # 'user' or 'ai'
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    embedding = db.Column(db.Text)  # For semantic memory (Milestone 5+)
    message_metadata = db.Column(db.Text)  # JSON string for additional data (e.g., order references, product info)

    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'message_type': self.message_type,
            'content': self.content,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'embedding': self.embedding,
            'metadata': self.message_metadata
        } 