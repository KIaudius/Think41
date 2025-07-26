import requests
import json
import time

BASE_URL = "http://localhost:5000/api"

def test_semantic_memory():
    """Test semantic memory functionality"""
    
    # Test 1: Create a conversation and test memory
    print("=== Testing Semantic Memory ===")
    
    # Create a conversation session
    session_data = {
        "user_id": 1,
        "title": "Memory Test Session"
    }
    
    response = requests.post(f"{BASE_URL}/conversations", json=session_data)
    if response.status_code == 200:
        session = response.json()
        session_id = session['id']
        print(f"Created session: {session_id}")
        
        # Test messages that should be remembered
        test_messages = [
            "What's the status of my order #102?",
            "I ordered a red shirt last week, when will it arrive?",
            "Can you remind me what I ordered before?",
            "What was the price of the product I asked about earlier?"
        ]
        
        for i, message in enumerate(test_messages):
            print(f"\n--- Message {i+1}: {message} ---")
            
            # Send message
            chat_data = {
                "user_id": 1,
                "message": message,
                "session_id": session_id
            }
            
            response = requests.post(f"{BASE_URL}/chat", json=chat_data)
            if response.status_code == 200:
                result = response.json()
                print(f"AI Response: {result.get('ai_response', 'No response')}")
            else:
                print(f"Error: {response.status_code} - {response.text}")
            
            time.sleep(1)  # Small delay between messages
        
        # Test memory retrieval
        print("\n=== Testing Memory Retrieval ===")
        
        # Search for order-related memories
        search_data = {
            "query": "order status",
            "session_id": session_id,
            "limit": 3
        }
        
        response = requests.post(f"{BASE_URL}/memory/search/1", json=search_data)
        if response.status_code == 200:
            results = response.json()
            print(f"Memory search results: {len(results['results'])} found")
            for i, memory in enumerate(results['results']):
                print(f"Memory {i+1}: {memory['content'][:100]}...")
        
        # Get memory stats
        print("\n=== Memory Statistics ===")
        response = requests.get(f"{BASE_URL}/memory/stats/1")
        if response.status_code == 200:
            stats = response.json()
            print(f"Memory stats: {stats}")
    
    else:
        print(f"Failed to create session: {response.status_code}")

def test_memory_personalization():
    """Test memory-based personalization"""
    print("\n=== Testing Memory Personalization ===")
    
    # Test messages that should trigger memory recall
    personalization_tests = [
        "Do you remember what I asked about earlier?",
        "What was the last thing we discussed?",
        "Can you remind me of our previous conversation?",
        "I mentioned an order before, can you check on it?"
    ]
    
    for i, message in enumerate(personalization_tests):
        print(f"\n--- Personalization Test {i+1}: {message} ---")
        
        chat_data = {
            "user_id": 1,
            "message": message,
            "session_id": 1  # Use existing session
        }
        
        response = requests.post(f"{BASE_URL}/chat", json=chat_data)
        if response.status_code == 200:
            result = response.json()
            print(f"AI Response: {result.get('ai_response', 'No response')}")
        else:
            print(f"Error: {response.status_code} - {response.text}")

if __name__ == "__main__":
    test_semantic_memory()
    test_memory_personalization() 