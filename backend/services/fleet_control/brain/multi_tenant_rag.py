"""
Multi-Tenant RAG System

Scalable RAG system supporting multiple clients with isolation,
shared knowledge, and personalized context management.
"""

import asyncio
import json
import sqlite3
import aiosqlite
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Tuple
from uuid import uuid4

try:
    import numpy as np
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False
    print("Warning: Embeddings not available. Using mock similarity.")


class RAGDocument:
    """Document structure for RAG system."""
    
    def __init__(self, id: str, content: str, metadata: Dict[str, Any], 
                 client_id: str = "shared", scope: str = "shared"):
        self.id = id
        self.content = content
        self.metadata = metadata
        self.client_id = client_id
        self.scope = scope
        self.created_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)
        self.access_count = 0
        self.effectiveness_score = 1.0
        self.embedding = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "content": self.content,
            "metadata": self.metadata,
            "client_id": self.client_id,
            "scope": self.scope,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "access_count": self.access_count,
            "effectiveness_score": self.effectiveness_score
        }


class ClientContext:
    """Client context and configuration."""
    
    def __init__(self, client_id: str, config: Dict[str, Any]):
        self.client_id = client_id
        self.client_type = config.get("type", "cottage")
        self.description = config.get("description", "")
        self.knowledge_base = config.get("knowledge_base", "hybrid")
        self.storage_quota = config.get("storage_quota", {})
        self.features = config.get("features", {})
        self.privacy_settings = config.get("privacy_settings", {})
        self.created_at = datetime.now(timezone.utc)
        self.last_activity = datetime.now(timezone.utc)
        self.query_count = 0
        self.success_rate = 0.0


class MultiTenantRAG:
    """Multi-tenant RAG system with client isolation."""
    
    def __init__(self, base_db_path: str, client_storage_path: str):
        self.base_db_path = base_db_path
        self.client_storage_path = Path(client_storage_path)
        self.client_storage_path.mkdir(parents=True, exist_ok=True)
        
        self.embedding_model = None
        if EMBEDDINGS_AVAILABLE:
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        self.clients = {}  # client_id -> ClientContext
        self.document_cache = {}  # client_id -> List[RAGDocument]
    
    async def initialize(self) -> None:
        """Initialize the RAG system."""
        await self._create_databases()
        await self._load_existing_clients()
        print("✅ Multi-tenant RAG system initialized")
    
    async def _create_databases(self) -> None:
        """Create shared and client databases."""
        # Shared knowledge database
        shared_db_path = Path(self.base_db_path)
        shared_db_path.parent.mkdir(parents=True, exist_ok=True)
        
        async with aiosqlite.connect(shared_db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    metadata TEXT NOT NULL,
                    client_id TEXT NOT NULL,
                    scope TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    access_count INTEGER DEFAULT 0,
                    effectiveness_score REAL DEFAULT 1.0,
                    embedding BLOB
                )
            """)
            
            await db.execute("""
                CREATE TABLE IF NOT EXISTS clients (
                    client_id TEXT PRIMARY KEY,
                    config TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    last_activity TEXT NOT NULL,
                    query_count INTEGER DEFAULT 0,
                    success_rate REAL DEFAULT 0.0
                )
            """)
            
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_documents_client_id ON documents(client_id)
            """)
            
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_documents_scope ON documents(scope)
            """)
            
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_documents_metadata ON documents(metadata)
            """)
            
            await db.commit()
    
    async def _load_existing_clients(self) -> None:
        """Load existing client configurations."""
        try:
            async with aiosqlite.connect(self.base_db_path) as db:
                async with db.execute("SELECT * FROM clients") as cursor:
                    async for row in cursor:
                        config = json.loads(row[1])
                        client = ClientContext(row[0], config)
                        client.created_at = datetime.fromisoformat(row[2])
                        client.last_activity = datetime.fromisoformat(row[3])
                        client.query_count = row[4]
                        client.success_rate = row[5]
                        self.clients[row[0]] = client
        except Exception as e:
            print(f"Warning: Could not load existing clients: {e}")
    
    async def register_client(self, config: Dict[str, Any]) -> str:
        """Register a new client."""
        client_id = f"{config.get('type', 'cottage')[:3]}_{uuid4().hex[:8]}"
        
        client = ClientContext(client_id, config)
        self.clients[client_id] = client
        
        # Save to database
        async with aiosqlite.connect(self.base_db_path) as db:
            await db.execute(
                "INSERT OR REPLACE INTO clients VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    client_id,
                    json.dumps(config),
                    client.created_at.isoformat(),
                    client.last_activity.isoformat(),
                    client.query_count,
                    client.success_rate
                )
            )
            await db.commit()
        
        # Create client-specific storage
        client_db_path = self.client_storage_path / f"{client_id}.db"
        await self._create_client_database(client_db_path)
        
        print(f"✅ Client registered: {client_id}")
        return client_id
    
    async def _create_client_database(self, client_db_path: str) -> None:
        """Create database for specific client."""
        client_db_path = Path(client_db_path)
        client_db_path.parent.mkdir(parents=True, exist_ok=True)
        
        async with aiosqlite.connect(client_db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS personal_documents (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    metadata TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    access_count INTEGER DEFAULT 0,
                    effectiveness_score REAL DEFAULT 1.0
                )
            """)
            
            await db.execute("""
                CREATE TABLE IF NOT EXISTS user_interactions (
                    interaction_id TEXT PRIMARY KEY,
                    client_id TEXT NOT NULL,
                    query TEXT NOT NULL,
                    response TEXT NOT NULL,
                    context_used TEXT,
                    success BOOLEAN,
                    timestamp TEXT NOT NULL,
                    feedback TEXT
                )
            """)
            
            await db.commit()
    
    async def add_document(self, client_id: str, document: Dict[str, Any]) -> None:
        """Add a document to the RAG system."""
        doc = RAGDocument(
            id=document["id"],
            content=document["content"],
            metadata=document["metadata"],
            client_id=document.get("client_id", client_id),
            scope=document.get("scope", "shared")
        )
        
        # Generate embedding
        if EMBEDDINGS_AVAILABLE and self.embedding_model:
            doc.embedding = self.embedding_model.encode(doc.content).tolist()
        
        # Store in shared database
        async with aiosqlite.connect(self.base_db_path) as db:
            await db.execute(
                """INSERT OR REPLACE INTO documents 
                   (id, content, metadata, client_id, scope, created_at, updated_at, embedding) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    doc.id, doc.content, json.dumps(doc.metadata),
                    doc.client_id, doc.scope, doc.created_at.isoformat(),
                    doc.updated_at.isoformat(),
                    json.dumps(doc.embedding) if doc.embedding else None
                )
            )
            await db.commit()
        
        # Update cache
        if client_id not in self.document_cache:
            self.document_cache[client_id] = []
        self.document_cache[client_id].append(doc)
    
    async def search(self, client_id: str, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search for relevant documents."""
        # Generate query embedding
        query_embedding = None
        if EMBEDDINGS_AVAILABLE and self.embedding_model:
            query_embedding = self.embedding_model.encode(query).tolist()
        
        # Search in shared and client-specific documents
        results = []
        
        async with aiosqlite.connect(self.base_db_path) as db:
            if query_embedding:
                # Vector similarity search
                await db.execute("""
                    SELECT id, content, metadata, client_id, scope, embedding,
                           1 - (ABS(embedding - ?) / 
                                   (SELECT MAX(ABS(embedding - ?)) FROM documents)) as similarity_score
                    FROM documents 
                    WHERE client_id IN ('shared', ?)
                    ORDER BY similarity_score DESC
                    LIMIT ?
                """, (json.dumps(query_embedding), json.dumps(query_embedding), client_id, limit))
            else:
                # Keyword search fallback
                await db.execute("""
                    SELECT id, content, metadata, client_id, scope
                    FROM documents 
                    WHERE client_id IN ('shared', ?)
                    AND (content LIKE ? OR metadata LIKE ?)
                    ORDER BY 
                        CASE WHEN client_id = ? THEN 1 ELSE 2 END,
                        access_count DESC
                    LIMIT ?
                """, (client_id, f"%{query}%", f"%{query}%", client_id, limit))
            
            async for row in db:
                doc_data = {
                    "id": row[0],
                    "content": row[1],
                    "metadata": json.loads(row[2]),
                    "client_id": row[3],
                    "scope": row[4],
                    "similarity_score": row[5] if len(row) > 5 else 1.0
                }
                results.append(doc_data)
        
        # Update access count
        await self._update_access_count([r["id"] for r in results])
        
        return results
    
    async def _update_access_count(self, document_ids: List[str]) -> None:
        """Update access count for documents."""
        if not document_ids:
            return
        
        placeholders = ",".join(["?" for _ in document_ids])
        async with aiosqlite.connect(self.base_db_path) as db:
            await db.execute(f"""
                UPDATE documents 
                SET access_count = access_count + 1 
                WHERE id IN ({placeholders})
            """, document_ids)
            await db.commit()
    
    async def get_client_context(self, client_id: str) -> Optional[ClientContext]:
        """Get client context."""
        return self.clients.get(client_id)
    
    async def update_client_activity(self, client_id: str, success: bool = True) -> None:
        """Update client activity metrics."""
        if client_id in self.clients:
            client = self.clients[client_id]
            client.last_activity = datetime.now(timezone.utc)
            client.query_count += 1
            
            # Update success rate with exponential moving average
            alpha = 0.1  # Learning rate
            client.success_rate = (alpha * (1.0 if success else 0.0) + 
                               (1 - alpha) * client.success_rate)
            
            # Save to database
            async with aiosqlite.connect(self.base_db_path) as db:
                await db.execute("""
                    UPDATE clients 
                    SET last_activity = ?, query_count = ?, success_rate = ?
                    WHERE client_id = ?
                """, (
                    client.last_activity.isoformat(),
                    client.query_count,
                    client.success_rate,
                    client_id
                ))
                await db.commit()
    
    async def setup_monitoring(self, client_id: str, config: Dict[str, Any]) -> None:
        """Setup monitoring for client."""
        monitoring_config = {
            "client_id": client_id,
            "config": config,
            "setup_time": datetime.now(timezone.utc).isoformat()
        }
        
        # Save monitoring configuration
        monitoring_path = self.client_storage_path / f"{client_id}_monitoring.json"
        with open(monitoring_path, "w") as f:
            json.dump(monitoring_config, f, indent=2)
        
        print(f"✅ Monitoring setup for client: {client_id}")
    
    async def get_system_stats(self) -> Dict[str, Any]:
        """Get system-wide statistics."""
        async with aiosqlite.connect(self.base_db_path) as db:
            # Client count
            async with db.execute("SELECT COUNT(*) FROM clients") as cursor:
                client_count = (await cursor.fetchone())[0]
            
            # Document count by scope
            async with db.execute("""
                SELECT scope, COUNT(*) as count 
                FROM documents 
                GROUP BY scope
            """) as cursor:
                scope_counts = {row[0]: row[1] async for row in cursor}
            
            # Total documents
            async with db.execute("SELECT COUNT(*) FROM documents") as cursor:
                total_documents = (await cursor.fetchone())[0]
            
            return {
                "total_clients": client_count,
                "total_documents": total_documents,
                "documents_by_scope": scope_counts,
                "embedding_model": "all-MiniLM-L6-v2" if EMBEDDINGS_AVAILABLE else "none",
                "system_status": "active"
            }


class ClientRegistry:
    """Registry for managing multiple clients."""
    
    def __init__(self):
        self.rag_system = None
    
    async def initialize(self, rag_system: MultiTenantRAG) -> None:
        """Initialize registry with RAG system."""
        self.rag_system = rag_system
    
    async def register_client(self, config: Dict[str, Any]) -> str:
        """Register a new client."""
        if not self.rag_system:
            raise RuntimeError("RAG system not initialized")
        
        return await self.rag_system.register_client(config)
    
    async def get_client(self, client_id: str) -> Optional[ClientContext]:
        """Get client by ID."""
        if not self.rag_system:
            return None
        return await self.rag_system.get_client_context(client_id)
    
    async def list_clients(self) -> List[ClientContext]:
        """List all registered clients."""
        if not self.rag_system:
            return []
        return list(self.rag_system.clients.values())
    
    async def search_client_knowledge(self, client_id: str, query: str) -> List[Dict[str, Any]]:
        """Search knowledge for specific client."""
        if not self.rag_system:
            return []
        return await self.rag_system.search(client_id, query)


# Mock similarity for when embeddings aren't available
class MockSimilarity:
    """Mock similarity calculation when embeddings aren't available."""
    
    @staticmethod
    def calculate_similarity(query: str, content: str) -> float:
        """Simple keyword-based similarity."""
        query_words = set(query.lower().split())
        content_words = set(content.lower().split())
        
        if not query_words or not content_words:
            return 0.0
        
        intersection = query_words & content_words
        union = query_words | content_words
        
        return len(intersection) / len(union) if union else 0.0


if not EMBEDDINGS_AVAILABLE:
    print("Warning: Using mock similarity. Install sentence-transformers for better results.")
