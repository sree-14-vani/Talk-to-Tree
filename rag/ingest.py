"""Data ingestion module for RAG pipeline"""
import os
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
try:
    import chromadb
    from chromadb.config import Settings
except ImportError:
    chromadb = None
    Settings = None

from .embeddings import get_embedding_model


class PlantDocument:
    """Represents a plant document with metadata"""

    def __init__(self, plant_name: str, content: str, file_path: str):
        self.plant_name = plant_name
        self.content = content
        self.file_path = file_path
        self.metadata = self._extract_metadata()

    def _extract_metadata(self) -> Dict[str, Any]:
        """Extract structured metadata from document"""
        metadata = {
            "plant_name": self.plant_name,
            "source_file": os.path.basename(self.file_path),
        }

        patterns = {
            "scientific_name": r"Scientific Name:\s*(.+)",
            "plant_type": r"Plant Type:\s*(.+)",
            "family": r"Family:\s*(.+)",
            "native_distribution": r"Native Distribution:\s*(.+)",
            "habitat": r"Habitat:\s*(.+)",
        }

        for key, pattern in patterns.items():
            match = re.search(pattern, self.content, re.IGNORECASE)
            if match:
                metadata[key] = match.group(1).strip()

        return metadata

    def chunk(self, chunk_size: int = 500, overlap: int = 50) -> List[Dict[str, Any]]:
        """Split document into overlapping chunks with metadata"""
        chunks = []
        sections = self._split_by_sections()

        for section_name, section_content in sections:
            words = section_content.split()
            if len(words) <= chunk_size:
                chunks.append({
                    "text": section_content,
                    "metadata": {
                        **self.metadata,
                        "section": section_name,
                        "plant_name": self.plant_name,
                    }
                })
            else:
                for i in range(0, len(words), chunk_size - overlap):
                    chunk_words = words[i:i + chunk_size]
                    chunk_text = " ".join(chunk_words)
                    chunks.append({
                        "text": chunk_text,
                        "metadata": {
                            **self.metadata,
                            "section": section_name,
                            "plant_name": self.plant_name,
                        }
                    })

        return chunks

    def _split_by_sections(self) -> List[tuple]:
        """Split content by section headers"""
        sections = []
        current_section = "General"
        current_content = []

        lines = self.content.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue

            if line.endswith(':') and len(line) < 50 and line[0].isupper():
                if current_content:
                    sections.append((current_section, '\n'.join(current_content)))
                current_section = line[:-1]
                current_content = []
            else:
                current_content.append(line)

        if current_content:
            sections.append((current_section, '\n'.join(current_content)))

        return sections if sections else [("Full Document", self.content)]


def load_plant_documents(data_dir: str = "data/plants") -> List[PlantDocument]:
    """Load all plant documents from data directory"""
    documents = []
    data_path = Path(data_dir)

    if not data_path.exists():
        return documents

    for file_path in data_path.glob("*.txt"):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            plant_name = file_path.stem.replace('_', ' ').title()
            doc = PlantDocument(plant_name, content, str(file_path))
            documents.append(doc)
        except Exception as e:
            print(f"Error loading {file_path}: {e}")

    return documents


def ingest_documents(
    data_dir: str = "data/plants",
    vector_store_path: str = "vector_store",
    collection_name: str = "plants",
    chunk_size: int = 500,
    overlap: int = 50
) -> Any:
    """Ingest plant documents into vector database"""

    if chromadb is None:
        raise RuntimeError("ChromaDB is required for ingestion. Install it with: pip install chromadb")

    client = chromadb.PersistentClient(
        path=vector_store_path,
        settings=Settings(anonymized_telemetry=False)
    )

    try:
        collection = client.get_collection(collection_name)
        print(f"Collection '{collection_name}' already exists. Recreating...")
        client.delete_collection(collection_name)
    except Exception:
        pass

    collection = client.create_collection(
        name=collection_name,
        metadata={"description": "Plant knowledge base for Talk to a Tree"}
    )

    documents = load_plant_documents(data_dir)
    print(f"Loaded {len(documents)} plant documents")

    embedding_model = get_embedding_model()

    all_chunks = []
    all_embeddings = []
    all_metadatas = []
    all_ids = []

    for doc in documents:
        chunks = doc.chunk(chunk_size, overlap)
        texts = [c["text"] for c in chunks]

        if texts:
            embeddings = embedding_model.encode(texts)

            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                chunk_id = f"{doc.plant_name.lower().replace(' ', '_')}_{i}"
                all_chunks.append(chunk["text"])
                all_embeddings.append(embedding.tolist())
                all_metadatas.append(chunk["metadata"])
                all_ids.append(chunk_id)

    if all_chunks:
        collection.add(
            documents=all_chunks,
            embeddings=all_embeddings,
            metadatas=all_metadatas,
            ids=all_ids
        )
        print(f"Added {len(all_chunks)} chunks to vector store")
    else:
        print("No chunks to add")

    return collection


def get_collection(vector_store_path: str = "vector_store", collection_name: str = "plants") -> chromadb.Collection:
    """Get existing collection"""
    client = chromadb.PersistentClient(
        path=vector_store_path,
        settings=Settings(anonymized_telemetry=False)
    )
    return client.get_collection(collection_name)


if __name__ == "__main__":
    ingest_documents()