"""Chat service for RAG-based plant conversations"""
from typing import List, Dict, Any, Optional

from rag.retriever import get_retriever
from rag.generator import generate_rag_response, get_llm_provider, RAGResponse


class ChatService:
    """Service for plant chat conversations"""

    def __init__(self, vector_store_path: str = "vector_store"):
        self.vector_store_path = vector_store_path
        self._retriever = None
        self._llm_provider = None

    @property
    def retriever(self):
        if self._retriever is None:
            self._retriever = get_retriever(self.vector_store_path)
        return self._retriever

    @property
    def llm_provider(self):
        if self._llm_provider is None:
            self._llm_provider = get_llm_provider()
        return self._llm_provider

    def ask(
        self,
        question: str,
        plant_name: Optional[str] = None,
        top_k: int = 5,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> RAGResponse:
        """Ask a question about a plant"""
        context_chunks = self.retriever.retrieve(question, plant_name, top_k)

        if conversation_history:
            context_str = "\n".join([
                f"{msg['role']}: {msg['content']}"
                for msg in conversation_history[-4:]
            ])
            question_with_context = f"Previous conversation:\n{context_str}\n\nCurrent question: {question}"
        else:
            question_with_context = question

        response = generate_rag_response(
            question_with_context,
            context_chunks,
            plant_name,
            self.llm_provider
        )

        return response

    def get_suggested_questions(self, plant_name: str) -> List[str]:
        """Get suggested questions for a plant"""
        base_questions = [
            f"Where does {plant_name} grow naturally?",
            f"What animals depend on {plant_name}?",
            f"How does {plant_name} grow and reproduce?",
            f"What is the cultural importance of {plant_name}?",
            f"What is the scientific name of {plant_name}?",
            f"Tell me something surprising about {plant_name}.",
            f"What are the ecological roles of {plant_name}?",
            f"How do you identify {plant_name}?"
        ]
        return base_questions

    def get_knowledge_story(self, plant_name: str) -> RAGResponse:
        """Generate a knowledge-based story about a plant"""
        question = f"Tell me the complete story of {plant_name} combining its scientific information, ecological role, and cultural significance."
        return self.ask(question, plant_name, top_k=10)

    def is_demo_mode(self) -> bool:
        """Check if running in demo mode"""
        return isinstance(self.llm_provider, type(get_llm_provider())) and \
            get_llm_provider().__class__.__name__ == "DemoLLMProvider"


def get_chat_service(vector_store_path: str = "vector_store") -> ChatService:
    """Factory function"""
    return ChatService(vector_store_path)