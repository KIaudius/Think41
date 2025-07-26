import requests
import json

BASE_URL = "http://localhost:5000/api/chat"

def test_chat_api():
    # Example user and message
    user_id = 1  # Change as needed
    session_id = None  # Set to None to create a new session
    user_message = "What is the status of order #12345?"

    payload = {
        "user_id": user_id,
        "message": user_message,
        "session_id": session_id
    }

    print(f"Sending to /api/chat: {payload}")
    response = requests.post(BASE_URL, json=payload)
    print(f"Status code: {response.status_code}")
    try:
        print("Response:")
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"Error parsing response: {e}")
        print(response.text)

if __name__ == "__main__":
    test_chat_api() 