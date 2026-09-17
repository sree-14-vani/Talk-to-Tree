"""Retriever module for RAG pipeline"""
from typing import List, Dict, Any, Optional
try:
    import chromadb
    from chromadb.config import Settings
except ImportError:
    chromadb = None
    Settings = None

from .embeddings import get_embedding_model


class PlantRetriever:
    """Retrieves relevant plant information from vector store"""

    def __init__(
        self,
        vector_store_path: str = "vector_store",
        collection_name: str = "plants",
        top_k: int = 5
    ):
        self.vector_store_path = vector_store_path
        self.collection_name = collection_name
        self.top_k = top_k
        self._client = None
        self._collection = None
        self._embedding_model = get_embedding_model()

    @property
    def client(self):
        if chromadb is None:
            raise RuntimeError("ChromaDB is required for plant chat. Install it with: pip install chromadb")
        if self._client is None:
            self._client = chromadb.PersistentClient(
                path=self.vector_store_path,
                settings=Settings(anonymized_telemetry=False)
            )
        return self._client

    @property
    def collection(self):
        if self._collection is None:
            try:
                self._collection = self.client.get_collection(self.collection_name)
            except Exception:
                raise RuntimeError(
                    f"Collection '{self.collection_name}' not found. "
                    f"Run 'python rag/ingest.py' to create the vector database."
                )
        return self._collection

    def retrieve(self, query: str, plant_name: Optional[str] = None, top_k: Optional[int] = None) -> List[Dict[str, Any]]:
        """Retrieve relevant chunks for a query"""
        k = top_k or self.top_k

        query_embedding = self._embedding_model.encode_single(query)

        where_filter = {}
        if plant_name:
            where_filter["plant_name"] = plant_name

        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=k,
            where=where_filter if where_filter else None,
            include=["documents", "metadatas", "distances"]
        )

        retrieved = []
        if results["documents"] and results["documents"][0]:
            for i, doc in enumerate(results["documents"][0]):
                metadata = results["metadatas"][0][i] if results["metadatas"] else {}
                distance = results["distances"][0][i] if results["distances"] else 0
                retrieved.append({
                    "text": doc,
                    "metadata": metadata,
                    "distance": distance,
                    "relevance_score": 1 - distance if distance <= 1 else 0
                })

        return retrieved

    def retrieve_by_plant(self, plant_name: str, top_k: Optional[int] = None) -> List[Dict[str, Any]]:
        """Retrieve all chunks for a specific plant"""
        k = top_k or 20

        results = self.collection.get(
            where={"plant_name": plant_name},
            include=["documents", "metadatas"],
            limit=k
        )

        retrieved = []
        if results["documents"]:
            for i, doc in enumerate(results["documents"]):
                metadata = results["metadatas"][i] if results["metadatas"] else {}
                retrieved.append({
                    "text": doc,
                    "metadata": metadata,
                    "distance": 0,
                    "relevance_score": 1.0
                })

        return retrieved

    def get_all_plants(self) -> List[str]:
        """Get list of all plant names in the collection"""
        results = self.collection.get(include=["metadatas"], limit=1000)
        plants = set()
        if results["metadatas"]:
            for meta in results["metadatas"]:
                if "plant_name" in meta:
                    plants.add(meta["plant_name"])
        return sorted(list(plants))


def get_retriever(
    vector_store_path: str = "vector_store",
    collection_name: str = "plants",
    top_k: int = 5
) -> PlantRetriever:
    """Factory function to get retriever"""
    return PlantRetriever(vector_store_path, collection_name, top_k)