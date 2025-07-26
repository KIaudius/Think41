import sqlite3
import os
from datetime import datetime

def migrate_database():
    """Add new conversation and chat tables to existing database"""
    
    # Connect to existing database
    conn = sqlite3.connect('ecommerce.db')
    cursor = conn.cursor()
    
    print("Starting database migration...")
    
    # Check if new tables already exist
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ConversationSession'")
    conversation_exists = cursor.fetchone() is not None
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ChatMessage'")
    chat_message_exists = cursor.fetchone() is not None
    
    if conversation_exists and chat_message_exists:
        print("New tables already exist. Migration not needed.")
        conn.close()
        return
    
    # Create ConversationSession table
    if not conversation_exists:
        print("Creating ConversationSession table...")
        cursor.execute('''
            CREATE TABLE ConversationSession (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title VARCHAR(255),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES UserTable(id)
            )
        ''')
        print("✓ ConversationSession table created")
    
    # Create ChatMessage table
    if not chat_message_exists:
        print("Creating ChatMessage table...")
        cursor.execute('''
            CREATE TABLE ChatMessage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                message_type VARCHAR(10) NOT NULL,
                content TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                embedding TEXT,
                message_metadata TEXT,
                FOREIGN KEY (session_id) REFERENCES ConversationSession(id)
            )
        ''')
        print("✓ ChatMessage table created")
    
    # Create indexes for better performance
    print("Creating indexes...")
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_conversation_user_id ON ConversationSession(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_conversation_active ON ConversationSession(is_active)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_chat_session_id ON ChatMessage(session_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_chat_created_at ON ChatMessage(created_at)')
    print("✓ Indexes created")
    
    # Commit changes
    conn.commit()
    conn.close()
    
    print("Database migration completed successfully!")
    print("\nNew tables added:")
    print("- ConversationSession: Manages chat sessions for users")
    print("- ChatMessage: Stores individual messages in conversations")
    print("\nNew API endpoints available:")
    print("- POST /api/conversations - Create new conversation")
    print("- GET /api/conversations/{id} - Get conversation details")
    print("- POST /api/conversations/{id}/messages - Add message")
    print("- GET /api/conversations/{id}/messages - Get messages")

if __name__ == "__main__":
    migrate_database() 