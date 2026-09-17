"""Plant service for managing plant data"""
import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from functools import lru_cache

from rag.ingest import load_plant_documents, get_collection
from rag.retriever import get_retriever


class PlantService:
    """Service for plant data operations"""

    def __init__(self, data_dir: str = "data/plants", vector_store_path: str = "vector_store"):
        self.data_dir = data_dir
        self.vector_store_path = vector_store_path
        self._retriever = None
        self._plant_cache = None

    @property
    def retriever(self):
        if self._retriever is None:
            self._retriever = get_retriever(self.vector_store_path)
        return self._retriever

    def get_all_plants(self) -> List[Dict[str, Any]]:
        """Get summary info for all plants"""
        if self._plant_cache is not None:
            return self._plant_cache

        documents = load_plant_documents(self.data_dir)
        plants = []

        for doc in documents:
            plants.append({
                "name": doc.plant_name,
                "scientific_name": doc.metadata.get("scientific_name", ""),
                "plant_type": doc.metadata.get("plant_type", ""),
                "family": doc.metadata.get("family", ""),
                "native_distribution": doc.metadata.get("native_distribution", ""),
                "habitat": doc.metadata.get("habitat", ""),
                "description": self._get_short_description(doc.content),
            })

        self._plant_cache = sorted(plants, key=lambda x: x["name"])
        return self._plant_cache

    def _get_short_description(self, content: str) -> str:
        """Extract a short description from content"""
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if line and not line.endswith(':') and len(line) > 20 and not any(
                k in line.lower() for k in ['scientific', 'plant type', 'family', 'native', 'habitat']
            ):
                return line[:200] + "..." if len(line) > 200 else line
        return "A remarkable plant with unique characteristics."

    def get_plant_by_name(self, plant_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed plant information"""
        documents = load_plant_documents(self.data_dir)

        for doc in documents:
            if doc.plant_name.lower() == plant_name.lower():
                return self._format_plant_profile(doc)

        return None

    def _format_plant_profile(self, doc) -> Dict[str, Any]:
        """Format plant document as profile"""
        content = doc.content
        sections = self._parse_sections(content)

        return {
            "name": doc.plant_name,
            "scientific_name": doc.metadata.get("scientific_name", ""),
            "plant_type": doc.metadata.get("plant_type", ""),
            "family": doc.metadata.get("family", ""),
            "native_distribution": doc.metadata.get("native_distribution", ""),
            "habitat": doc.metadata.get("habitat", ""),
            "sections": sections,
            "safety_note": self._extract_safety_note(content),
        }

    def _parse_sections(self, content: str) -> Dict[str, str]:
        """Parse content into sections"""
        sections = {}
        current_section = "Overview"
        current_content = []

        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue

            if line.endswith(':') and len(line) < 60 and line[0].isupper():
                if current_content:
                    sections[current_section] = '\n'.join(current_content)
                current_section = line[:-1]
                current_content = []
            else:
                current_content.append(line)

        if current_content:
            sections[current_section] = '\n'.join(current_content)

        return sections

    def _extract_safety_note(self, content: str) -> str:
        """Extract safety notes from content"""
        lines = content.split('\n')
        for line in lines:
            line = line.strip().lower()
            if 'safety' in line or 'caution' in line or 'toxic' in line or 'do not consume' in line:
                return line
        return "Do not consume or use this plant based only on this information. Consult an appropriate expert."

    def search_plants(self, query: str) -> List[Dict[str, Any]]:
        """Search plants by name or characteristics"""
        plants = self.get_all_plants()
        query_lower = query.lower()

        results = []
        for plant in plants:
            if (query_lower in plant["name"].lower() or
                query_lower in plant["scientific_name"].lower() or
                query_lower in plant["family"].lower() or
                query_lower in plant["habitat"].lower()):
                results.append(plant)

        return results

    def filter_plants(self, plant_type: str = "", habitat: str = "") -> List[Dict[str, Any]]:
        """Filter plants by type and habitat"""
        plants = self.get_all_plants()

        if plant_type:
            plants = [p for p in plants if plant_type.lower() in p["plant_type"].lower()]

        if habitat:
            plants = [p for p in plants if habitat.lower() in p["habitat"].lower()]

        return plants

    def compare_plants(self, plant1_name: str, plant2_name: str) -> Dict[str, Any]:
        """Compare two plants"""
        plant1 = self.get_plant_by_name(plant1_name)
        plant2 = self.get_plant_by_name(plant2_name)

        if not plant1 or not plant2:
            return {"error": "One or both plants not found"}

        categories = [
            "scientific_name", "plant_type", "family", "native_distribution",
            "habitat"
        ]

        comparison = {
            "plant1": {"name": plant1_name, "data": {}},
            "plant2": {"name": plant2_name, "data": {}},
            "categories": []
        }

        for cat in categories:
            comparison["plant1"]["data"][cat] = plant1.get(cat, "N/A")
            comparison["plant2"]["data"][cat] = plant2.get(cat, "N/A")
            comparison["categories"].append(cat.replace("_", " ").title())

        for section in ["Ecological Importance", "Cultural Historical Significance", "Interesting Facts"]:
            comparison["plant1"]["data"][section.lower().replace(" ", "_")] = plant1["sections"].get(section, "N/A")
            comparison["plant2"]["data"][section.lower().replace(" ", "_")] = plant2["sections"].get(section, "N/A")
            if section not in comparison["categories"]:
                comparison["categories"].append(section)

        return comparison

    def get_random_fact(self) -> Dict[str, Any]:
        """Get a random fact from knowledge base"""
        import random

        documents = load_plant_documents(self.data_dir)
        all_facts = []

        for doc in documents:
            sections = self._parse_sections(doc.content)
            for section_name in ["Interesting Facts", "Ecological Importance", "Cultural Historical Significance"]:
                if section_name in sections:
                    lines = sections[section_name].split('.')
                    for line in lines:
                        line = line.strip()
                        if len(line) > 30:
                            all_facts.append({
                                "plant": doc.plant_name,
                                "section": section_name,
                                "fact": line + "."
                            })

        if all_facts:
            fact = random.choice(all_facts)
            return {
                "plant": fact["plant"],
                "section": fact["section"],
                "fact": fact["fact"]
            }

        return {
            "plant": "Nature",
            "section": "General",
            "fact": "Trees communicate through underground fungal networks called the Wood Wide Web."
        }


def get_plant_service(data_dir: str = "data/plants", vector_store_path: str = "vector_store") -> PlantService:
    """Factory function"""
    return PlantService(data_dir, vector_store_path)