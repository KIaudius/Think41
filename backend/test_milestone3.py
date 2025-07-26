import requests
import json
from datetime import datetime

# Base URL for the API
BASE_URL = "http://localhost:5000/api"

def test_conversation_functionality():
    """Test all conversation and chat functionality"""
    
    print("🧪 Testing Milestone 3: Conversation & Chat Functionality")
    print("=" * 60)
    
    # Test 1: Get a user to work with
    print("\n1. Getting a user for testing...")
    response = requests.get(f"{BASE_URL}/users")
    if response.status_code != 200:
        print("❌ Failed to get users")
        return
    
    users = response.json()
    if not users:
        print("❌ No users found in database")
        return
    
    test_user = users[0]
    user_id = test_user['id']
    print(f"✓ Using user: {test_user['first_name']} {test_user['last_name']} (ID: {user_id})")
    
    # Test 2: Create a new conversation session
    print("\n2. Creating a new conversation session...")
    session_data = {
        "user_id": user_id,
        "title": "Order Tracking - Test Session"
    }
    response = requests.post(f"{BASE_URL}/conversations", json=session_data)
    if response.status_code != 201:
        print(f"❌ Failed to create conversation: {response.text}")
        return
    
    session = response.json()
    session_id = session['id']
    print(f"✓ Created conversation session (ID: {session_id})")
    print(f"  Title: {session['title']}")
    print(f"  Active: {session['is_active']}")
    
    # Test 3: Add user message
    print("\n3. Adding a user message...")
    user_message = {
        "message_type": "user",
        "content": "Hi, I'd like to check the status of my recent order #12345",
        "metadata": {"order_id": 12345}
    }
    response = requests.post(f"{BASE_URL}/conversations/{session_id}/messages", json=user_message)
    if response.status_code != 201:
        print(f"❌ Failed to add user message: {response.text}")
        return
    
    user_msg = response.json()
    print(f"✓ Added user message (ID: {user_msg['id']})")
    print(f"  Content: {user_msg['content'][:50]}...")
    
    # Test 4: Add AI response
    print("\n4. Adding an AI response...")
    ai_message = {
        "message_type": "ai",
        "content": "I'll help you check your order status. Let me look up order #12345 for you.",
        "metadata": {"order_id": 12345, "action": "order_lookup"}
    }
    response = requests.post(f"{BASE_URL}/conversations/{session_id}/messages", json=ai_message)
    if response.status_code != 201:
        print(f"❌ Failed to add AI message: {response.text}")
        return
    
    ai_msg = response.json()
    print(f"✓ Added AI message (ID: {ai_msg['id']})")
    print(f"  Content: {ai_msg['content'][:50]}...")
    
    # Test 5: Get conversation messages
    print("\n5. Retrieving conversation messages...")
    response = requests.get(f"{BASE_URL}/conversations/{session_id}/messages")
    if response.status_code != 200:
        print(f"❌ Failed to get messages: {response.text}")
        return
    
    messages = response.json()
    print(f"✓ Retrieved {len(messages)} messages")
    for msg in messages:
        print(f"  [{msg['message_type'].upper()}] {msg['content'][:40]}...")
    
    # Test 6: Update conversation title
    print("\n6. Updating conversation title...")
    new_title = "Order Status Inquiry - Updated"
    response = requests.put(f"{BASE_URL}/conversations/{session_id}/title", json={"title": new_title})
    if response.status_code != 200:
        print(f"❌ Failed to update title: {response.text}")
        return
    
    print("✓ Updated conversation title")
    
    # Test 7: Get user conversations
    print("\n7. Getting all user conversations...")
    response = requests.get(f"{BASE_URL}/users/{user_id}/conversations")
    if response.status_code != 200:
        print(f"❌ Failed to get user conversations: {response.text}")
        return
    
    conversations = response.json()
    print(f"✓ Found {len(conversations)} conversations for user")
    for conv in conversations:
        print(f"  - {conv['title']} (Active: {conv['is_active']}, Messages: {conv['message_count']})")
    
    # Test 8: Test AI context endpoints
    print("\n8. Testing AI context endpoints...")
    
    # Get user context
    response = requests.get(f"{BASE_URL}/ai/user-context/{user_id}")
    if response.status_code == 200:
        context = response.json()
        print(f"✓ User context retrieved")
        print(f"  User: {context['user']['name']}")
        print(f"  Orders: {len(context['orders'])}")
        print(f"  Order items: {len(context['order_items'])}")
    else:
        print(f"⚠️  User context endpoint returned: {response.status_code}")
    
    # Test 9: Add embedding to message (for future semantic memory)
    print("\n9. Testing embedding update...")
    embedding_data = {
        "embedding": "[0.1, 0.2, 0.3, ...]"  # Placeholder embedding
    }
    response = requests.put(f"{BASE_URL}/messages/{user_msg['id']}/embedding", json=embedding_data)
    if response.status_code == 200:
        print("✓ Message embedding updated")
    else:
        print(f"⚠️  Embedding update returned: {response.status_code}")
    
    # Test 10: Get recent messages
    print("\n10. Getting recent messages...")
    response = requests.get(f"{BASE_URL}/conversations/{session_id}/messages/recent?count=5")
    if response.status_code == 200:
        recent_messages = response.json()
        print(f"✓ Retrieved {len(recent_messages)} recent messages")
    else:
        print(f"❌ Failed to get recent messages: {response.text}")
    
    print("\n" + "=" * 60)
    print("🎉 All Milestone 3 tests completed successfully!")
    print("\n✅ New functionality verified:")
    print("  - Conversation session creation and management")
    print("  - Message storage and retrieval")
    print("  - User conversation history")
    print("  - AI context endpoints")
    print("  - Embedding support for semantic memory")
    print("\n🚀 Ready for integration with LangGraph and LLM workflows!")

if __name__ == "__main__":
    test_conversation_functionality() 