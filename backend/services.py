from models import db, User, Product, Order, OrderItem, DistributionCenter, InventoryItem, ConversationSession, ChatMessage, MessageType
from datetime import datetime
import json
from typing import List, Optional, Dict, Any

class UserService:
    @staticmethod
    def get_all_users():
        return User.query.all()
    
    @staticmethod
    def get_user_by_id(user_id: int):
        return User.query.get(user_id)
    
    @staticmethod
    def get_user_orders(user_id: int):
        return Order.query.filter_by(user_id=user_id).all()
    
    @staticmethod
    def get_user_conversations(user_id: int):
        return ConversationSession.query.filter_by(user_id=user_id).order_by(ConversationSession.updated_at.desc()).all()

class ProductService:
    @staticmethod
    def get_all_products():
        return Product.query.all()
    
    @staticmethod
    def get_product_by_id(product_id: int):
        return Product.query.get(product_id)
    
    @staticmethod
    def search_products(query: str):
        return Product.query.filter(
            Product.name.contains(query) | 
            Product.brand.contains(query) | 
            Product.category.contains(query)
        ).all()

class OrderService:
    @staticmethod
    def get_all_orders():
        return Order.query.all()
    
    @staticmethod
    def get_order_by_id(order_id: int):
        return Order.query.get(order_id)
    
    @staticmethod
    def get_order_items(order_id: int):
        return OrderItem.query.filter_by(order_id=order_id).all()
    
    @staticmethod
    def get_user_order_history(user_id: int):
        return Order.query.filter_by(user_id=user_id).order_by(Order.created_at.desc()).all()

class ConversationService:
    @staticmethod
    def create_session(user_id: int, title: Optional[str] = None) -> ConversationSession:
        """Create a new conversation session for a user"""
        session = ConversationSession(
            user_id=user_id,
            title=title or f"Chat Session - {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}",
            is_active=True
        )
        db.session.add(session)
        db.session.commit()
        return session
    
    @staticmethod
    def get_session(session_id: int) -> Optional[ConversationSession]:
        """Get a conversation session by ID"""
        return ConversationSession.query.get(session_id)
    
    @staticmethod
    def get_user_sessions(user_id: int, active_only: bool = True) -> List[ConversationSession]:
        """Get all conversation sessions for a user"""
        query = ConversationSession.query.filter_by(user_id=user_id)
        if active_only:
            query = query.filter_by(is_active=True)
        return query.order_by(ConversationSession.updated_at.desc()).all()
    
    @staticmethod
    def update_session_title(session_id: int, title: str) -> bool:
        """Update the title of a conversation session"""
        session = ConversationSession.query.get(session_id)
        if session:
            session.title = title
            session.updated_at = datetime.utcnow()
            db.session.commit()
            return True
        return False
    
    @staticmethod
    def deactivate_session(session_id: int) -> bool:
        """Mark a conversation session as inactive"""
        session = ConversationSession.query.get(session_id)
        if session:
            session.is_active = False
            session.updated_at = datetime.utcnow()
            db.session.commit()
            return True
        return False

class ChatMessageService:
    @staticmethod
    def add_message(session_id: int, message_type: str, content: str, 
                   metadata: Optional[Dict[str, Any]] = None) -> ChatMessage:
        """Add a new message to a conversation session"""
        message = ChatMessage(
            session_id=session_id,
            message_type=message_type,
            content=content,
            message_metadata=json.dumps(metadata) if metadata else None
        )
        db.session.add(message)
        
        # Update session timestamp
        session = ConversationSession.query.get(session_id)
        if session:
            session.updated_at = datetime.utcnow()
        
        db.session.commit()
        return message
    
    @staticmethod
    def get_session_messages(session_id: int, limit: Optional[int] = None) -> List[ChatMessage]:
        """Get all messages for a conversation session"""
        query = ChatMessage.query.filter_by(session_id=session_id).order_by(ChatMessage.created_at)
        if limit:
            query = query.limit(limit)
        return query.all()
    
    @staticmethod
    def get_recent_messages(session_id: int, count: int = 10) -> List[ChatMessage]:
        """Get the most recent messages from a session"""
        return ChatMessage.query.filter_by(session_id=session_id)\
            .order_by(ChatMessage.created_at.desc())\
            .limit(count)\
            .all()
    
    @staticmethod
    def update_message_embedding(message_id: int, embedding: str) -> bool:
        """Update the embedding for a message (for semantic memory)"""
        message = ChatMessage.query.get(message_id)
        if message:
            message.embedding = embedding
            db.session.commit()
            return True
        return False

class EcommerceDataService:
    """Service to provide e-commerce data context for AI conversations"""
    
    @staticmethod
    def get_user_context(user_id: int) -> Dict[str, Any]:
        """Get comprehensive user context including orders, products, etc."""
        user = User.query.get(user_id)
        if not user:
            return {}
        
        orders = Order.query.filter_by(user_id=user_id).all()
        order_items = []
        for order in orders:
            items = OrderItem.query.filter_by(order_id=order.order_id).all()
            order_items.extend(items)
        
        return {
            'user': {
                'id': user.id,
                'name': f"{user.first_name} {user.last_name}",
                'email': user.email,
                'location': f"{user.city}, {user.state}, {user.country}"
            },
            'orders': [{
                'order_id': order.order_id,
                'status': order.status,
                'created_at': order.created_at.isoformat() if order.created_at else None,
                'num_items': order.num_of_item
            } for order in orders],
            'order_items': [{
                'id': item.id,
                'order_id': item.order_id,
                'product_id': item.product_id,
                'status': item.status,
                'sale_price': item.sale_price
            } for item in order_items]
        }
    
    @staticmethod
    def get_product_info(product_ids: List[int]) -> List[Dict[str, Any]]:
        """Get detailed product information"""
        products = Product.query.filter(Product.id.in_(product_ids)).all()
        return [{
            'id': product.id,
            'name': product.name,
            'brand': product.brand,
            'category': product.category,
            'department': product.department,
            'retail_price': product.retail_price,
            'sku': product.sku
        } for product in products]
    
    @staticmethod
    def get_order_status(order_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed order status information"""
        order = Order.query.get(order_id)
        if not order:
            return None
        
        items = OrderItem.query.filter_by(order_id=order_id).all()
        return {
            'order_id': order.order_id,
            'status': order.status,
            'created_at': order.created_at.isoformat() if order.created_at else None,
            'shipped_at': order.shipped_at.isoformat() if order.shipped_at else None,
            'delivered_at': order.delivered_at.isoformat() if order.delivered_at else None,
            'returned_at': order.returned_at.isoformat() if order.returned_at else None,
            'num_items': order.num_of_item,
            'items': [{
                'id': item.id,
                'product_id': item.product_id,
                'status': item.status,
                'sale_price': item.sale_price
            } for item in items]
        } 