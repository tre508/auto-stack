import json
import sqlite3
import requests
from typing import List, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class SimpleMemoryService:
    """
    Simple memory service that bypasses Mem0's embedding dimension issues.
    Stores memories in SQLite and uses direct embedding API calls.
    """
    
    def __init__(self, db_path: str = "/app/simple_memory.db", embedding_endpoint: str = None):
        self.db_path = db_path
        self.embedding_endpoint = embedding_endpoint or "http://bge_embedding_auto:7860/v1/embeddings"
        self.init_db()
    
    def init_db(self):
        """Initialize SQLite database for memory storage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                memory_text TEXT NOT NULL,
                embedding BLOB,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_embedding(self, text: str) -> List[float]:
        """Get embedding for text using BGE service"""
        try:
            response = requests.post(
                self.embedding_endpoint,
                json={
                    "input": text,
                    "model": "BAAI/bge-base-en-v1.5"
                },
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            return data["data"][0]["embedding"]
        except Exception as e:
            logger.error(f"Failed to get embedding: {e}")
            return []
    
    def add_memory(self, user_id: str, memory_text: str, metadata: Dict = None) -> bool:
        """Add a memory to the database"""
        try:
            embedding = self.get_embedding(memory_text)
            if not embedding:
                return False
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO memories (user_id, memory_text, embedding, metadata)
                VALUES (?, ?, ?, ?)
            ''', (
                user_id,
                memory_text,
                json.dumps(embedding),
                json.dumps(metadata or {})
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Failed to add memory: {e}")
            return False
    
    def search_memories(self, user_id: str, query: str, limit: int = 10) -> List[Dict]:
        """Search memories using cosine similarity"""
        try:
            query_embedding = self.get_embedding(query)
            if not query_embedding:
                return []
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, memory_text, embedding, metadata, created_at
                FROM memories
                WHERE user_id = ?
            ''', (user_id,))
            
            memories = []
            for row in cursor.fetchall():
                memory_id, memory_text, embedding_blob, metadata, created_at = row
                try:
                    memory_embedding = json.loads(embedding_blob)
                    similarity = self.cosine_similarity(query_embedding, memory_embedding)
                    
                    memories.append({
                        "id": memory_id,
                        "memory": memory_text,
                        "score": similarity,
                        "metadata": json.loads(metadata),
                        "created_at": created_at
                    })
                except Exception as e:
                    logger.warning(f"Failed to process memory {memory_id}: {e}")
                    continue
            
            # Sort by similarity score and return top results
            memories.sort(key=lambda x: x["score"], reverse=True)
            conn.close()
            
            return memories[:limit]
        except Exception as e:
            logger.error(f"Failed to search memories: {e}")
            return []
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        try:
            import math
            
            dot_product = sum(a * b for a, b in zip(vec1, vec2))
            magnitude1 = math.sqrt(sum(a * a for a in vec1))
            magnitude2 = math.sqrt(sum(a * a for a in vec2))
            
            if magnitude1 == 0 or magnitude2 == 0:
                return 0
            
            return dot_product / (magnitude1 * magnitude2)
        except Exception:
            return 0
    
    def get_recent_memories(self, user_id: str, limit: int = 10) -> List[Dict]:
        """Get recent memories for a user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, memory_text, metadata, created_at
                FROM memories
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            ''', (user_id, limit))
            
            memories = []
            for row in cursor.fetchall():
                memory_id, memory_text, metadata, created_at = row
                memories.append({
                    "id": memory_id,
                    "memory": memory_text,
                    "metadata": json.loads(metadata),
                    "created_at": created_at
                })
            
            conn.close()
            return memories
        except Exception as e:
            logger.error(f"Failed to get recent memories: {e}")
            return [] 