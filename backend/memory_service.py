import os
import json
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import numpy as np
from services import ChatMessageService
from models import ChatMessage, ConversationSession

class SemanticMemoryService:
    """Service for managing semantic memory using ChromaDB"""
    
    def __init__(self):
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path="./chroma_db",
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Create collections for different types of memory
        self.user_memory_collection = self.client.get_or_create_collection(
            name="user_memory",
            metadata={"description": "User conversation memory"}
        )
        
        self.session_memory_collection = self.client.get_or_create_collection(
            name="session_memory", 
            metadata={"description": "Session-specific memory"}
        )
        
        # Memory expiration settings (in days)
        self.memory_expiry_days = 30
        
    def _generate_embedding_id(self, user_id: int, session_id: int, message_id: int) -> str:
        """Generate unique ID for embedding"""
        return f"user_{user_id}_session_{session_id}_msg_{message_id}"
    
    def _create_memory_metadata(self, user_id: int, session_id: int, message_type: str, 
                               created_at: datetime, metadata: Optional[Dict] = None) -> Dict:
        """Create metadata for memory entry"""
        return {
            "user_id": user_id,
            "session_id": session_id,
            "message_type": message_type,
            "created_at": created_at.isoformat(),
            "timestamp": created_at.timestamp(),
            **(metadata or {})
        }
    
    def store_message_memory(self, user_id: int, session_id: int, message_id: int,
                           content: str, message_type: str, metadata: Optional[Dict] = None) -> bool:
        """Store a message in semantic memory"""
        try:
            # Generate embedding using a simple text embedding (you can replace with better embeddings)
            embedding = self._generate_simple_embedding(content)
            
            # Create unique ID
            embedding_id = self._generate_embedding_id(user_id, session_id, message_id)
            
            # Create metadata
            memory_metadata = self._create_memory_metadata(
                user_id, session_id, message_type, datetime.utcnow(), metadata
            )
            
            # Store in both collections
            self.user_memory_collection.add(
                embeddings=[embedding],
                documents=[content],
                metadatas=[memory_metadata],
                ids=[embedding_id]
            )
            
            self.session_memory_collection.add(
                embeddings=[embedding],
                documents=[content],
                metadatas=[memory_metadata],
                ids=[f"session_{embedding_id}"]
            )
            
            return True
            
        except Exception as e:
            print(f"Error storing memory: {e}")
            return False
    
    def _generate_simple_embedding(self, text: str) -> List[float]:
        """Generate a simple embedding (placeholder - replace with proper embedding model)"""
        # This is a simple hash-based embedding for demonstration
        # In production, use a proper embedding model like sentence-transformers
        import hashlib
        hash_obj = hashlib.md5(text.encode())
        hash_bytes = hash_obj.digest()
        
        # Convert to 128-dimensional vector
        embedding = []
        for i in range(0, len(hash_bytes), 4):
            chunk = hash_bytes[i:i+4]
            value = int.from_bytes(chunk, byteorder='big')
            embedding.append(value / 2**32)  # Normalize to [0, 1]
        
        # Pad or truncate to 128 dimensions
        while len(embedding) < 128:
            embedding.append(0.0)
        embedding = embedding[:128]
        
        return embedding
    
    def retrieve_relevant_memory(self, user_id: int, session_id: int, query: str, 
                               limit: int = 5) -> List[Dict[str, Any]]:
        """Retrieve relevant memory based on semantic similarity"""
        try:
            # Generate embedding for query
            query_embedding = self._generate_simple_embedding(query)
            
            # Query user memory
            user_results = self.user_memory_collection.query(
                query_embeddings=[query_embedding],
                n_results=limit,
                where={"user_id": user_id}
            )
            
            # Query session memory
            session_results = self.session_memory_collection.query(
                query_embeddings=[query_embedding],
                n_results=limit,
                where={"session_id": session_id}
            )
            
            # Combine and deduplicate results
            all_memories = []
            
            # Process user memories
            if user_results['documents']:
                for i, doc in enumerate(user_results['documents'][0]):
                    all_memories.append({
                        'content': doc,
                        'metadata': user_results['metadatas'][0][i],
                        'distance': user_results['distances'][0][i],
                        'source': 'user_memory'
                    })
            
            # Process session memories
            if session_results['documents']:
                for i, doc in enumerate(session_results['documents'][0]):
                    all_memories.append({
                        'content': doc,
                        'metadata': session_results['metadatas'][0][i],
                        'distance': session_results['distances'][0][i],
                        'source': 'session_memory'
                    })
            
            # Sort by relevance (lower distance = more relevant)
            all_memories.sort(key=lambda x: x['distance'])
            
            # Remove duplicates and limit results
            seen_contents = set()
            unique_memories = []
            for memory in all_memories:
                if memory['content'] not in seen_contents:
                    seen_contents.add(memory['content'])
                    unique_memories.append(memory)
                    if len(unique_memories) >= limit:
                        break
            
            return unique_memories
            
        except Exception as e:
            print(f"Error retrieving memory: {e}")
            return []
    
    def get_conversation_context(self, user_id: int, session_id: int, 
                               recent_messages: int = 10) -> List[Dict[str, Any]]:
        """Get recent conversation context for the session"""
        try:
            # Get recent messages from database
            recent_messages = ChatMessageService.get_recent_messages(session_id, recent_messages)
            
            context = []
            for msg in recent_messages:
                context.append({
                    'role': msg.message_type,
                    'content': msg.content,
                    'timestamp': msg.created_at.isoformat(),
                    'metadata': json.loads(msg.message_metadata) if msg.message_metadata else {}
                })
            
            return context
            
        except Exception as e:
            print(f"Error getting conversation context: {e}")
            return []
    
    def cleanup_expired_memory(self, days: Optional[int] = None) -> int:
        """Remove old memory entries"""
        try:
            expiry_days = days or self.memory_expiry_days
            cutoff_time = datetime.utcnow() - timedelta(days=expiry_days)
            cutoff_timestamp = cutoff_time.timestamp()
            
            # Get old entries from both collections
            old_user_memories = self.user_memory_collection.get(
                where={"timestamp": {"$lt": cutoff_timestamp}}
            )
            
            old_session_memories = self.session_memory_collection.get(
                where={"timestamp": {"$lt": cutoff_timestamp}}
            )
            
            # Delete old entries
            deleted_count = 0
            if old_user_memories['ids']:
                self.user_memory_collection.delete(ids=old_user_memories['ids'])
                deleted_count += len(old_user_memories['ids'])
            
            if old_session_memories['ids']:
                self.session_memory_collection.delete(ids=old_session_memories['ids'])
                deleted_count += len(old_session_memories['ids'])
            
            return deleted_count
            
        except Exception as e:
            print(f"Error cleaning up memory: {e}")
            return 0
    
    def get_memory_stats(self, user_id: int) -> Dict[str, Any]:
        """Get memory statistics for a user"""
        try:
            user_memories = self.user_memory_collection.get(
                where={"user_id": user_id}
            )
            
            session_memories = self.session_memory_collection.get(
                where={"user_id": user_id}
            )
            
            return {
                "user_memory_count": len(user_memories['ids']) if user_memories['ids'] else 0,
                "session_memory_count": len(session_memories['ids']) if session_memories['ids'] else 0,
                "total_memory_count": (len(user_memories['ids']) if user_memories['ids'] else 0) + 
                                   (len(session_memories['ids']) if session_memories['ids'] else 0)
            }
            
        except Exception as e:
            print(f"Error getting memory stats: {e}")
            return {"user_memory_count": 0, "session_memory_count": 0, "total_memory_count": 0}

# Global instance
memory_service = SemanticMemoryService() 