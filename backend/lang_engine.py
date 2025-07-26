import os
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from groq import Groq
from services import EcommerceDataService
from typing import TypedDict, Optional

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Shared state format for LangGraph
class ChatState(TypedDict):
    user_id: int
    session_id: int
    user_message: str
    intent: Optional[str]
    db_result: Optional[dict]
    ai_response: Optional[str]
    error: Optional[str]

def parse_intent_node(state: ChatState) -> ChatState:
    """Basic keyword-based intent parser"""
    msg = state["user_message"].lower()
    if "order" in msg and ("status" in msg or "track" in msg):
        state["intent"] = "order_status"
    elif "product" in msg or "item" in msg:
        state["intent"] = "product_info"
    else:
        state["intent"] = "general"
    return state

def query_db_node(state: ChatState) -> ChatState:
    """Routes based on intent and queries the DB tools"""
    try:
        if state["intent"] == "order_status":
            # Try to extract order_id from message (very basic)
            import re
            match = re.search(r"order[\s#]*(\d+)", state["user_message"].lower())
            order_id = int(match.group(1)) if match else None
            if order_id:
                result = EcommerceDataService.get_order_status(order_id)
                state["db_result"] = result
            else:
                state["db_result"] = {"error": "No order ID found in message."}
        elif state["intent"] == "product_info":
            # Try to extract product_id from message (very basic)
            import re
            match = re.search(r"product[\s#]*(\d+)", state["user_message"].lower())
            product_id = int(match.group(1)) if match else None
            if product_id:
                result = EcommerceDataService.get_product_info([product_id])
                state["db_result"] = result[0] if result else {"error": "Product not found."}
            else:
                state["db_result"] = {"error": "No product ID found in message."}
        else:
            state["db_result"] = {}
    except Exception as e:
        state["db_result"] = {"error": str(e)}
    return state

def generate_response_node(state: ChatState) -> ChatState:
    """Use Groq LLM to turn raw data into user-friendly responses"""
    try:
        client = Groq(api_key=GROQ_API_KEY)
        prompt = f"User: {state['user_message']}\n\nContext: {state['db_result']}\n\nRespond as a helpful e-commerce assistant."
        response = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=256,
            temperature=0.2
        )
        state["ai_response"] = response.choices[0].message.content
    except Exception as e:
        state["error"] = f"Groq LLM error: {e}"
        # Fallback response based on intent
        if state["intent"] == "order_status":
            if state["db_result"] and "error" not in state["db_result"]:
                order_info = state["db_result"]
                state["ai_response"] = f"Your order #{order_info.get('order_id', 'Unknown')} is currently {order_info.get('status', 'Unknown')}. Created on {order_info.get('created_at', 'Unknown')}."
            else:
                state["ai_response"] = "I couldn't find that order. Please check your order number and try again."
        elif state["intent"] == "product_info":
            if state["db_result"] and "error" not in state["db_result"]:
                product_info = state["db_result"]
                state["ai_response"] = f"The product '{product_info.get('name', 'Unknown')}' by {product_info.get('brand', 'Unknown')} is priced at ${product_info.get('retail_price', 'Unknown')}."
            else:
                state["ai_response"] = "I couldn't find that product. Please check the product ID and try again."
        else:
            state["ai_response"] = "I'm here to help with your e-commerce questions! You can ask about order status or product information."
    return state

def build_langgraph_workflow():
    graph = StateGraph(ChatState)
    graph.add_node("parse_intent", parse_intent_node)
    graph.add_node("query_db", query_db_node)
    graph.add_node("generate_response", generate_response_node)
    graph.add_edge("parse_intent", "query_db")
    graph.add_edge("query_db", "generate_response")
    graph.add_edge("generate_response", END)
    graph.set_entry_point("parse_intent")
    return graph.compile()

def run_langgraph_chat(user_id: int, session_id: int, user_message: str) -> dict:
    workflow = build_langgraph_workflow()
    state = ChatState(
        user_id=user_id, 
        session_id=session_id, 
        user_message=user_message,
        intent=None,
        db_result=None,
        ai_response=None,
        error=None
    )
    result = workflow.invoke(state)
    return result 