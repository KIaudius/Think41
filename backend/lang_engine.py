import os
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from groq import Groq
from services import EcommerceDataService
from memory_service import memory_service
from typing import TypedDict, Optional, List, Dict, Any
import json

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Enhanced state format for LangGraph with memory
class ChatState(TypedDict):
    user_id: int
    session_id: int
    user_message: str
    intent: Optional[str]
    db_result: Optional[dict]
    semantic_memory: Optional[List[Dict[str, Any]]]
    conversation_context: Optional[List[Dict[str, Any]]]
    ai_response: Optional[str]
    error: Optional[str]

def parse_intent_node(state: ChatState) -> ChatState:
    """Enhanced intent parser with memory awareness"""
    msg = state["user_message"].lower()
    
    # Check for memory-related keywords
    if any(word in msg for word in ["remember", "before", "last time", "previously", "earlier"]):
        state["intent"] = "memory_recall"
    elif "order" in msg and ("status" in msg or "track" in msg):
        state["intent"] = "order_status"
    elif "product" in msg or "item" in msg:
        state["intent"] = "product_info"
    else:
        state["intent"] = "general"
    
    return state

def retrieve_memory_node(state: ChatState) -> ChatState:
    """Retrieve relevant semantic memory"""
    try:
        # Get semantic memory
        semantic_memory = memory_service.retrieve_relevant_memory(
            user_id=state["user_id"],
            session_id=state["session_id"],
            query=state["user_message"],
            limit=5
        )
        state["semantic_memory"] = semantic_memory
        
        # Get conversation context
        conversation_context = memory_service.get_conversation_context(
            user_id=state["user_id"],
            session_id=state["session_id"],
            recent_messages=10
        )
        state["conversation_context"] = conversation_context
        
    except Exception as e:
        state["error"] = f"Memory retrieval error: {e}"
        state["semantic_memory"] = []
        state["conversation_context"] = []
    
    return state

def query_db_node(state: ChatState) -> ChatState:
    """Enhanced DB query with memory context"""
    try:
        if state["intent"] == "order_status":
            # Try to extract order_id from message or memory
            import re
            match = re.search(r"order[\s#]*(\d+)", state["user_message"].lower())
            order_id = int(match.group(1)) if match else None
            
            # If no order ID in current message, check memory
            if not order_id and state["semantic_memory"]:
                for memory in state["semantic_memory"]:
                    memory_match = re.search(r"order[\s#]*(\d+)", memory["content"].lower())
                    if memory_match:
                        order_id = int(memory_match.group(1))
                        break
            
            if order_id:
                result = EcommerceDataService.get_order_status(order_id)
                state["db_result"] = result
            else:
                state["db_result"] = {"error": "No order ID found in message or memory."}
                
        elif state["intent"] == "product_info":
            # Try to extract product_id from message or memory
            import re
            match = re.search(r"product[\s#]*(\d+)", state["user_message"].lower())
            product_id = int(match.group(1)) if match else None
            
            # If no product ID in current message, check memory
            if not product_id and state["semantic_memory"]:
                for memory in state["semantic_memory"]:
                    memory_match = re.search(r"product[\s#]*(\d+)", memory["content"].lower())
                    if memory_match:
                        product_id = int(memory_match.group(1))
                        break
            
            if product_id:
                result = EcommerceDataService.get_product_info([product_id])
                state["db_result"] = result[0] if result else {"error": "Product not found."}
            else:
                state["db_result"] = {"error": "No product ID found in message or memory."}
                
        elif state["intent"] == "memory_recall":
            # For memory recall, use semantic memory as context
            state["db_result"] = {
                "memory_context": state["semantic_memory"],
                "conversation_history": state["conversation_context"]
            }
        else:
            state["db_result"] = {}
            
    except Exception as e:
        state["db_result"] = {"error": str(e)}
    
    return state

def generate_response_node(state: ChatState) -> ChatState:
    """Enhanced response generation with memory and personalization"""
    try:
        client = Groq(api_key=GROQ_API_KEY)
        
        # Build enhanced prompt with memory
        prompt_parts = [
            f"User: {state['user_message']}",
            f"Current Context: {state['db_result']}"
        ]
        
        # Add semantic memory context
        if state["semantic_memory"]:
            memory_context = "Relevant Past Conversations:\n"
            for i, memory in enumerate(state["semantic_memory"][:3], 1):
                memory_context += f"{i}. {memory['content']}\n"
            prompt_parts.append(memory_context)
        
        # Add conversation history
        if state["conversation_context"]:
            history_context = "Recent Conversation History:\n"
            for msg in state["conversation_context"][-5:]:  # Last 5 messages
                history_context += f"{msg['role']}: {msg['content']}\n"
            prompt_parts.append(history_context)
        
        prompt_parts.append("\nRespond as a helpful e-commerce assistant with memory and personalization. Reference past conversations when relevant.")
        
        full_prompt = "\n\n".join(prompt_parts)
        
        response = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[{"role": "user", "content": full_prompt}],
            max_tokens=512,
            temperature=0.3
        )
        state["ai_response"] = response.choices[0].message.content
        
    except Exception as e:
        state["error"] = f"Groq LLM error: {e}"
        # Enhanced fallback response with memory
        if state["intent"] == "memory_recall":
            if state["semantic_memory"]:
                memory_summary = "Based on our previous conversations, "
                for memory in state["semantic_memory"][:2]:
                    memory_summary += f"I remember {memory['content']}. "
                state["ai_response"] = memory_summary + "How can I help you today?"
            else:
                state["ai_response"] = "I don't have specific memories of our previous conversations, but I'm here to help!"
        elif state["intent"] == "order_status":
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
            state["ai_response"] = "I'm here to help with your e-commerce questions! You can ask about order status, product information, or reference our previous conversations."
    
    return state

def store_memory_node(state: ChatState) -> ChatState:
    """Store the current interaction in memory"""
    try:
        # Store user message
        memory_service.store_message_memory(
            user_id=state["user_id"],
            session_id=state["session_id"],
            message_id=0,  # Will be updated by the calling service
            content=state["user_message"],
            message_type="user",
            metadata={"intent": state["intent"]}
        )
        
        # Store AI response
        if state["ai_response"]:
            memory_service.store_message_memory(
                user_id=state["user_id"],
                session_id=state["session_id"],
                message_id=0,  # Will be updated by the calling service
                content=state["ai_response"],
                message_type="ai",
                metadata={"intent": state["intent"], "db_result": state["db_result"]}
            )
        
    except Exception as e:
        print(f"Error storing memory: {e}")
        # Don't fail the workflow if memory storage fails
    
    return state

def build_langgraph_workflow():
    """Build enhanced LangGraph workflow with memory"""
    graph = StateGraph(ChatState)
    
    # Add nodes
    graph.add_node("parse_intent", parse_intent_node)
    graph.add_node("retrieve_memory", retrieve_memory_node)
    graph.add_node("query_db", query_db_node)
    graph.add_node("generate_response", generate_response_node)
    graph.add_node("store_memory", store_memory_node)
    
    # Add edges
    graph.add_edge("parse_intent", "retrieve_memory")
    graph.add_edge("retrieve_memory", "query_db")
    graph.add_edge("query_db", "generate_response")
    graph.add_edge("generate_response", "store_memory")
    graph.add_edge("store_memory", END)
    
    graph.set_entry_point("parse_intent")
    return graph.compile()

def run_langgraph_chat(user_id: int, session_id: int, user_message: str) -> dict:
    """Run enhanced LangGraph chat with memory"""
    workflow = build_langgraph_workflow()
    state = ChatState(
        user_id=user_id, 
        session_id=session_id, 
        user_message=user_message,
        intent=None,
        db_result=None,
        semantic_memory=None,
        conversation_context=None,
        ai_response=None,
        error=None
    )
    result = workflow.invoke(state)
    return result 