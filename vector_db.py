# database/vector_db.py

import chromadb
from chromadb.config import Settings
import numpy as np
from typing import List, Dict
import json

class VectorMemory:
    """Gestor de memoria semántica con búsqueda vectorial"""
    
    def __init__(self, persist_dir: str = "./data/vector_db"):
        # Configurar Chroma
        self.settings = Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=persist_dir,
            anonymized_telemetry=False
        )
        self.client = chromadb.Client(self.settings)
        
        # Colecciones
        self.conversations_collection = self.client.get_or_create_collection(
            name="conversations",
            metadata={"hnsw:space": "cosine"}
        )
        
        self.commands_collection = self.client.get_or_create_collection(
            name="commands",
            metadata={"hnsw:space": "cosine"}
        )
        
        self.knowledge_collection = self.client.get_or_create_collection(
            name="knowledge",
            metadata={"hnsw:space": "cosine"}
        )
    
    def add_conversation(self, 
                        conversation_id: str,
                        content: str,
                        embedding: List[float],
                        metadata: Dict = None):
        """Añade una conversación a la base de datos vectorial"""
        self.conversations_collection.add(
            ids=[conversation_id],
            embeddings=[embedding],
            documents=[content],
            metadatas=[metadata or {}]
        )
    
    def search_conversations(self, 
                            query_embedding: List[float],
                            n_results: int = 5) -> List[Dict]:
        """Busca conversaciones similares"""
        results = self.conversations_collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        
        return [
            {
                "id": results["ids"][0][i],
                "content": results["documents"][0][i],
                "distance": results["distances"][0][i],
                "metadata": results["metadatas"][0][i]
            }
            for i in range(len(results["ids"][0]))
        ]
    
    def semantic_search(self,
                       query: str,
                       embedding_model,
                       collection_name: str = "conversations",
                       n_results: int = 5) -> List[Dict]:
        """Búsqueda semántica completa"""
        # Generar embedding de la query
        query_embedding = embedding_model.encode(query).tolist()
        
        # Obtener colección
        collection = self.client.get_collection(name=collection_name)
        
        # Realizar búsqueda
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        
        return results
    
    def add_knowledge(self,
                     knowledge_id: str,
                     content: str,
                     embedding: List[float],
                     category: str = "general"):
        """Añade conocimiento a la base de datos"""
        self.knowledge_collection.add(
            ids=[knowledge_id],
            embeddings=[embedding],
            documents=[content],
            metadatas=[{"category": category}]
        )
    
    def persist(self):
        """Guarda la base de datos vectorial"""
        self.client.persist()

# Uso
# vector_memory = VectorMemory()
# vector_memory.add_conversation("conv_001", "Hola KAGU", embedding_vector)