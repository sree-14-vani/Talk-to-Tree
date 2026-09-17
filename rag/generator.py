"""Generator module for RAG pipeline - LLM response generation"""
import os
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class RAGResponse:
    """Response from RAG generator"""
    answer: str
    sources: List[Dict[str, Any]]
    demo_mode: bool = False


class LLMProvider:
    """Abstract base for LLM providers"""

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        raise NotImplementedError


class DemoLLMProvider(LLMProvider):
    """Demo mode LLM - uses template-based responses grounded in retrieved context"""

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        context = prompt.split("Context:\n", 1)[-1].strip()
        if not context:
            return "I couldn't find reliable information about that in the current botanical knowledge base."
        excerpts = context.split("\n\n")[:3]
        return "Demo mode is using the verified local plant notes. Here is the relevant information:\n\n" + "\n\n".join(excerpts)


class OpenAILLMProvider(LLMProvider):
    """OpenAI LLM provider"""

    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        self.api_key = api_key
        self.model = model
        self._client = None

    @property
    def client(self):
        if self._client is None:
            try:
                import openai
                self._client = openai.OpenAI(api_key=self.api_key)
            except ImportError:
                raise RuntimeError("openai package not installed. Run: pip install openai")
        return self._client

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,
                max_tokens=500
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"LLM Error: {str(e)}"


class AnthropicLLMProvider(LLMProvider):
    """Anthropic Claude provider"""

    def __init__(self, api_key: str, model: str = "claude-3-haiku-20240307"):
        self.api_key = api_key
        self.model = model
        self._client = None

    @property
    def client(self):
        if self._client is None:
            try:
                import anthropic
                self._client = anthropic.Anthropic(api_key=self.api_key)
            except ImportError:
                raise RuntimeError("anthropic package not installed. Run: pip install anthropic")
        return self._client

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        try:
            response = self.client.messages.create(
                model=self.model,
                system=system_prompt,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=500
            )
            return response.content[0].text.strip()
        except Exception as e:
            return f"LLM Error: {str(e)}"


def get_llm_provider() -> LLMProvider:
    """Factory to get LLM provider based on environment"""
    openai_key = os.getenv("OPENAI_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")

    if openai_key:
        return OpenAILLMProvider(openai_key)
    elif anthropic_key:
        return AnthropicLLMProvider(anthropic_key)
    else:
        return DemoLLMProvider()


SYSTEM_PROMPT = """You are a knowledgeable botanical assistant for "Talk to a Tree" - an interactive plant knowledge explorer.
Your role is to answer questions about plants using ONLY the provided context from the knowledge base.

Guidelines:
1. Base your answers PRIMARILY on the retrieved context provided
2. If the context doesn't contain enough information, say: "I couldn't find reliable information about that in my current knowledge base."
3. Distinguish between: scientific facts, traditional/cultural information, ecological information, and general care information
4. NEVER make medical, poisoning, or edible-use claims as certain facts
5. If a plant may be toxic or unsafe, include: "Do not consume or use this plant based only on this information. Consult an appropriate expert."
6. Do not invent sources or hallucinate plant information
7. For medical questions, clearly label traditional use versus clinical evidence, never give a diagnosis or dosage, and identify the plant part and preparation only when the context explicitly states it
8. If the question asks for a benefit, treatment, cure, dosage, pregnancy advice, drug interaction, or toxicity detail that is not in the context, say that it is not verified here and recommend a qualified clinician or poison service
9. Keep responses concise but informative
10. Use a warm, educational tone appropriate for a botanical museum"""


def build_rag_prompt(query: str, context_chunks: List[Dict[str, Any]], plant_name: Optional[str] = None) -> str:
    """Build RAG prompt with context"""
    context_parts = []
    for i, chunk in enumerate(context_chunks):
        meta = chunk.get("metadata", {})
        section = meta.get("section", "General")
        source_plant = meta.get("plant_name", plant_name or "Unknown")
        source_file = meta.get("source_file", "Unknown")
        context_parts.append(
            f"[Source {i+1}: {source_plant} - {section} ({source_file})]\n{chunk['text']}"
        )

    context = "\n\n".join(context_parts)

    plant_context = f" about {plant_name}" if plant_name else ""

    prompt = f"""Answer the following question{plant_context} using ONLY the provided context.

Question: {query}

Context:
{context}

Provide a clear, well-structured answer. Include relevant details from the context.
If the context doesn't contain enough information, state that clearly.
Add appropriate safety disclaimers where relevant."""

    return prompt


def generate_rag_response(
    query: str,
    context_chunks: List[Dict[str, Any]],
    plant_name: Optional[str] = None,
    llm_provider: Optional[LLMProvider] = None
) -> RAGResponse:
    """Generate RAG response with sources"""
    if llm_provider is None:
        llm_provider = get_llm_provider()

    is_demo = isinstance(llm_provider, DemoLLMProvider)

    if not context_chunks:
        return RAGResponse(
            answer="I couldn't find relevant information in my knowledge base to answer that question.",
            sources=[],
            demo_mode=is_demo
        )

    prompt = build_rag_prompt(query, context_chunks, plant_name)
    answer = llm_provider.generate(prompt, SYSTEM_PROMPT)

    sources = []
    for chunk in context_chunks:
        meta = chunk.get("metadata", {})
        sources.append({
            "plant": meta.get("plant_name", "Unknown"),
            "source_file": meta.get("source_file", "Unknown"),
            "section": meta.get("section", "General"),
            "relevance_score": round(chunk.get("relevance_score", 0), 3),
            "text_snippet": chunk["text"][:200] + "..." if len(chunk["text"]) > 200 else chunk["text"]
        })

    return RAGResponse(answer=answer, sources=sources, demo_mode=is_demo)