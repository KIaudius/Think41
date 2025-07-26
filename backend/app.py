from flask import Flask, jsonify, request
from flask_cors import CORS
from models import db, User, Product, Order, OrderItem, DistributionCenter, InventoryItem, ConversationSession, ChatMessage
from services import UserService, ProductService, OrderService, ConversationService, ChatMessageService, EcommerceDataService
import os
from lang_engine import run_langgraph_chat
from memory_service import memory_service

app = Flask(__name__)
CORS(app)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

# ============================================================================
# ROOT ENDPOINT
# ============================================================================

@app.route('/', methods=['GET'])
def root():
    """Root endpoint to show API is running"""
    return jsonify({
        'message': 'E-commerce AI Chat API is running!',
        'version': '1.0.0',
        'milestone': '3 - Conversation & Chat Support',
        'endpoints': {
            'ecommerce': [
                '/api/users',
                '/api/products', 
                '/api/orders',
                '/api/distribution-centers'
            ],
            'conversations': [
                '/api/conversations',
                '/api/users/{id}/conversations'
            ],
            'ai_context': [
                '/api/ai/user-context/{user_id}',
                '/api/ai/products',
                '/api/ai/order-status/{order_id}'
            ]
        },
        'docs': '/api/docs' if hasattr(app, 'swagger') else 'No docs available'
    })

# ============================================================================
# EXISTING E-COMMERCE ENDPOINTS
# ============================================================================

@app.route('/api/users', methods=['GET'])
def get_users():
    """Get all users"""
    users = UserService.get_all_users()
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

@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get a specific user by ID"""
    user = UserService.get_user_by_id(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
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
    })

@app.route('/api/users/<int:user_id>/orders', methods=['GET'])
def get_user_orders(user_id):
    """Get all orders for a specific user"""
    orders = UserService.get_user_orders(user_id)
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

@app.route('/api/products', methods=['GET'])
def get_products():
    """Get all products"""
    products = ProductService.get_all_products()
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

@app.route('/api/products/search', methods=['GET'])
def search_products():
    """Search products by name, brand, or category"""
    query = request.args.get('q', '')
    if not query:
        return jsonify({'error': 'Query parameter "q" is required'}), 400
    
    products = ProductService.search_products(query)
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
    """Get all orders"""
    orders = OrderService.get_all_orders()
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

@app.route('/api/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    """Get a specific order by ID"""
    order = OrderService.get_order_by_id(order_id)
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    
    return jsonify({
        'order_id': order.order_id,
        'user_id': order.user_id,
        'status': order.status,
        'gender': order.gender,
        'created_at': order.created_at.isoformat() if order.created_at else None,
        'returned_at': order.returned_at.isoformat() if order.returned_at else None,
        'shipped_at': order.shipped_at.isoformat() if order.shipped_at else None,
        'delivered_at': order.delivered_at.isoformat() if order.delivered_at else None,
        'num_of_item': order.num_of_item
    })

@app.route('/api/orders/<int:order_id>/items', methods=['GET'])
def get_order_items(order_id):
    """Get all items for a specific order"""
    items = OrderService.get_order_items(order_id)
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
    } for item in items])

@app.route('/api/distribution-centers', methods=['GET'])
def get_distribution_centers():
    """Get all distribution centers"""
    centers = DistributionCenter.query.all()
    return jsonify([{
        'id': center.id,
        'name': center.name,
        'latitude': center.latitude,
        'longitude': center.longitude
    } for center in centers])

@app.route('/api/inventory-items', methods=['GET'])
def get_inventory_items():
    """Get all inventory items"""
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

# ============================================================================
# NEW CONVERSATION AND CHAT ENDPOINTS (MILESTONE 3)
# ============================================================================

@app.route('/api/conversations', methods=['POST'])
def create_conversation():
    """Create a new conversation session"""
    data = request.get_json()
    user_id = data.get('user_id')
    title = data.get('title')
    
    if not user_id:
        return jsonify({'error': 'user_id is required'}), 400
    
    # Verify user exists
    user = UserService.get_user_by_id(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    session = ConversationService.create_session(user_id, title)
    return jsonify(session.to_dict()), 201

@app.route('/api/conversations/<int:session_id>', methods=['GET'])
def get_conversation(session_id):
    """Get a specific conversation session"""
    session = ConversationService.get_session(session_id)
    if not session:
        return jsonify({'error': 'Conversation session not found'}), 404
    
    return jsonify(session.to_dict())

@app.route('/api/users/<int:user_id>/conversations', methods=['GET'])
def get_user_conversations(user_id):
    """Get all conversation sessions for a user"""
    active_only = request.args.get('active_only', 'true').lower() == 'true'
    sessions = ConversationService.get_user_sessions(user_id, active_only)
    return jsonify([session.to_dict() for session in sessions])

@app.route('/api/conversations/<int:session_id>/title', methods=['PUT'])
def update_conversation_title(session_id):
    """Update the title of a conversation session"""
    data = request.get_json()
    title = data.get('title')
    
    if not title:
        return jsonify({'error': 'title is required'}), 400
    
    success = ConversationService.update_session_title(session_id, title)
    if not success:
        return jsonify({'error': 'Conversation session not found'}), 404
    
    return jsonify({'message': 'Title updated successfully'})

@app.route('/api/conversations/<int:session_id>/deactivate', methods=['POST'])
def deactivate_conversation(session_id):
    """Deactivate a conversation session"""
    success = ConversationService.deactivate_session(session_id)
    if not success:
        return jsonify({'error': 'Conversation session not found'}), 404
    
    return jsonify({'message': 'Conversation session deactivated'})

@app.route('/api/conversations/<int:session_id>/messages', methods=['POST'])
def add_message(session_id):
    """Add a new message to a conversation session"""
    data = request.get_json()
    message_type = data.get('message_type')
    content = data.get('content')
    metadata = data.get('metadata')
    
    if not message_type or not content:
        return jsonify({'error': 'message_type and content are required'}), 400
    
    if message_type not in ['user', 'ai']:
        return jsonify({'error': 'message_type must be "user" or "ai"'}), 400
    
    # Verify session exists
    session = ConversationService.get_session(session_id)
    if not session:
        return jsonify({'error': 'Conversation session not found'}), 404
    
    message = ChatMessageService.add_message(session_id, message_type, content, metadata)
    return jsonify(message.to_dict()), 201

@app.route('/api/conversations/<int:session_id>/messages', methods=['GET'])
def get_conversation_messages(session_id):
    """Get all messages for a conversation session"""
    limit = request.args.get('limit', type=int)
    messages = ChatMessageService.get_session_messages(session_id, limit)
    return jsonify([message.to_dict() for message in messages])

@app.route('/api/conversations/<int:session_id>/messages/recent', methods=['GET'])
def get_recent_messages(session_id):
    """Get recent messages from a conversation session"""
    count = request.args.get('count', 10, type=int)
    messages = ChatMessageService.get_recent_messages(session_id, count)
    return jsonify([message.to_dict() for message in messages])

@app.route('/api/messages/<int:message_id>/embedding', methods=['PUT'])
def update_message_embedding(message_id):
    """Update the embedding for a message (for semantic memory)"""
    data = request.get_json()
    embedding = data.get('embedding')
    
    if not embedding:
        return jsonify({'error': 'embedding is required'}), 400
    
    success = ChatMessageService.update_message_embedding(message_id, embedding)
    if not success:
        return jsonify({'error': 'Message not found'}), 404
    
    return jsonify({'message': 'Embedding updated successfully'})

# ============================================================================
# E-COMMERCE CONTEXT ENDPOINTS FOR AI
# ============================================================================

@app.route('/api/ai/user-context/<int:user_id>', methods=['GET'])
def get_user_context(user_id):
    """Get comprehensive user context for AI conversations"""
    context = EcommerceDataService.get_user_context(user_id)
    if not context:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify(context)

@app.route('/api/ai/products', methods=['GET'])
def get_products_for_ai():
    """Get product information for AI context"""
    product_ids = request.args.getlist('product_ids', type=int)
    if not product_ids:
        return jsonify({'error': 'product_ids parameter is required'}), 400
    
    products = EcommerceDataService.get_product_info(product_ids)
    return jsonify(products)

@app.route('/api/ai/order-status/<int:order_id>', methods=['GET'])
def get_order_status_for_ai(order_id):
    """Get detailed order status for AI context"""
    order_status = EcommerceDataService.get_order_status(order_id)
    if not order_status:
        return jsonify({'error': 'Order not found'}), 404
    
    return jsonify(order_status)

@app.route('/api/chat', methods=['POST'])
def chat_api():
    """Chat endpoint: user sends message, LLM responds, all persisted"""
    data = request.get_json()
    user_id = data.get('user_id')
    user_message = data.get('message')
    session_id = data.get('session_id')
    
    if not user_id or not user_message:
        return jsonify({'error': 'user_id and message are required'}), 400
    
    # If no session_id, create a new session
    if not session_id:
        session = ConversationService.create_session(user_id)
        session_id = session.id
    else:
        session = ConversationService.get_session(session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404
    
    # Persist user message
    user_msg = ChatMessageService.add_message(
        session_id=session_id,
        message_type='user',
        content=user_message,
        metadata=None
    )
    
    # Run LangGraph workflow
    result = run_langgraph_chat(user_id, session_id, user_message)
    ai_response = result.get('ai_response')
    error = result.get('error')
    db_result = result.get('db_result')
    intent = result.get('intent')
    
    # Persist AI message
    ai_msg = ChatMessageService.add_message(
        session_id=session_id,
        message_type='ai',
        content=ai_response,
        metadata={
            'intent': intent,
            'db_result': db_result,
            'error': error
        }
    )
    
    return jsonify({
        'session_id': session_id,
        'user_message': user_message,
        'ai_response': ai_response,
        'intent': intent,
        'db_result': db_result,
        'error': error,
        'user_message_id': user_msg.id,
        'ai_message_id': ai_msg.id
    })

# Add these new endpoints after the existing ones

@app.route('/api/memory/stats/<int:user_id>', methods=['GET'])
def get_memory_stats(user_id):
    """Get memory statistics for a user"""
    try:
        stats = memory_service.get_memory_stats(user_id)
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/memory/cleanup', methods=['POST'])
def cleanup_memory():
    """Clean up expired memory entries"""
    try:
        data = request.get_json() or {}
        days = data.get('days', 30)
        deleted_count = memory_service.cleanup_expired_memory(days)
        return jsonify({
            'message': f'Cleaned up {deleted_count} expired memory entries',
            'deleted_count': deleted_count
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/memory/search/<int:user_id>', methods=['POST'])
def search_memory(user_id):
    """Search user's memory"""
    try:
        data = request.get_json()
        query = data.get('query', '')
        limit = data.get('limit', 5)
        
        results = memory_service.retrieve_relevant_memory(
            user_id=user_id,
            session_id=data.get('session_id', 0),
            query=query,
            limit=limit
        )
        
        return jsonify({
            'query': query,
            'results': results,
            'count': len(results)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000) 