# E-commerce Backend API with AI Chat Support

This is a Flask-based REST API for the e-commerce dataset with **Milestone 3** conversation and chat functionality.

## 🚀 Milestone 3 Features

### New Data Models
- **ConversationSession**: Manages chat sessions for users
- **ChatMessage**: Stores individual messages in conversations
- **Embedding Support**: Ready for semantic memory (Milestone 5+)

### New API Endpoints
- `POST /api/conversations` - Create new conversation session
- `GET /api/conversations/{id}` - Get conversation details
- `PUT /api/conversations/{id}/title` - Update conversation title
- `POST /api/conversations/{id}/deactivate` - Deactivate session
- `POST /api/conversations/{id}/messages` - Add message to session
- `GET /api/conversations/{id}/messages` - Get all messages
- `GET /api/conversations/{id}/messages/recent` - Get recent messages
- `PUT /api/messages/{id}/embedding` - Update message embedding

### AI Context Endpoints
- `GET /api/ai/user-context/{user_id}` - Get user context for AI
- `GET /api/ai/products` - Get product info for AI
- `GET /api/ai/order-status/{order_id}` - Get order status for AI

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Load data into the database:
```bash
python load_data.py
```

3. Run database migration (adds new tables):
```bash
python migrate_db.py
```

4. Run the Flask application:
```bash
python app.py
```

The API will be available at `http://localhost:5000`

## Testing

Run the comprehensive test suite:
```bash
python test_milestone3.py
```

## API Endpoints

### E-commerce Endpoints
- `GET /api/users` - Get all users
- `GET /api/users/{id}` - Get specific user
- `GET /api/users/{id}/orders` - Get user orders
- `GET /api/products` - Get all products
- `GET /api/products/search?q=query` - Search products
- `GET /api/orders` - Get all orders
- `GET /api/orders/{id}` - Get specific order
- `GET /api/orders/{id}/items` - Get order items
- `GET /api/distribution-centers` - Get distribution centers
- `GET /api/inventory-items` - Get inventory items

### Conversation Endpoints
- `POST /api/conversations` - Create conversation session
- `GET /api/conversations/{id}` - Get conversation
- `GET /api/users/{id}/conversations` - Get user conversations
- `PUT /api/conversations/{id}/title` - Update title
- `POST /api/conversations/{id}/deactivate` - Deactivate session
- `POST /api/conversations/{id}/messages` - Add message
- `GET /api/conversations/{id}/messages` - Get messages
- `GET /api/conversations/{id}/messages/recent` - Get recent messages
- `PUT /api/messages/{id}/embedding` - Update embedding

### AI Context Endpoints
- `GET /api/ai/user-context/{user_id}` - User context for AI
- `GET /api/ai/products?product_ids=1,2,3` - Product info for AI
- `GET /api/ai/order-status/{order_id}` - Order status for AI

## Database Schema

### New Tables (Milestone 3)
```sql
-- ConversationSession table
CREATE TABLE ConversationSession (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 1,
    FOREIGN KEY (user_id) REFERENCES UserTable(id)
);

-- ChatMessage table
CREATE TABLE ChatMessage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    message_type VARCHAR(10) NOT NULL,
    content TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    embedding TEXT,
    metadata TEXT,
    FOREIGN KEY (session_id) REFERENCES ConversationSession(id)
);
```

## Service Layer

The application uses a modular service layer:
- `UserService` - User management
- `ProductService` - Product operations
- `OrderService` - Order management
- `ConversationService` - Conversation session management
- `ChatMessageService` - Message handling
- `EcommerceDataService` - AI context data

## Integration with LangGraph

The API is designed to integrate seamlessly with LangGraph workflows:
- User context endpoints provide comprehensive user data
- Conversation history enables memory and context
- Embedding support ready for semantic search
- Metadata fields for storing AI workflow state

## Database

The application uses SQLite as the database for simplicity. The database file `ecommerce.db` will be created automatically when you run the application.

## Data Loading

The `load_data.py` script will load CSV files from the `../dataset/` directory into the SQLite database. Make sure your CSV files are in the correct location before running the script.

## Troubleshooting

If you encounter the `'mssql.runQuery' not found` error, this solution replaces the Microsoft SQL Server connection with SQLAlchemy and SQLite, which is more suitable for development and doesn't require additional database setup. 