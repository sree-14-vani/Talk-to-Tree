"""Image service for plant identification (demo mode)"""
import os
import base64
from typing import Dict, Any, Optional
from pathlib import Path
from PIL import Image
import io


class ImageService:
    """Service for plant image identification (demo mode)"""

    DEMO_PLANT_MAPPING = {
        "banyan": "Banyan",
        "neem": "Neem",
        "peepal": "Peepal",
        "mango": "Mango",
        "coconut": "Coconut",
        "bamboo": "Bamboo",
        "gulmohar": "Gulmohar",
        "sandalwood": "Sandalwood",
        "ashoka": "Ashoka",
        "jackfruit": "Jackfruit",
        "rain tree": "Rain Tree",
        "indian gooseberry": "Indian Gooseberry",
        "tamarind": "Tamarind",
        "teak": "Teak",
        "curry leaf": "Curry Leaf",
        "kadamba": "Kadamba",
        "semal": "Semal",
        "pongam": "Pongam",
        "bel": "Bel",
        "mahua": "Mahua",
    }

    def __init__(self, upload_dir: str = "uploads"):
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(exist_ok=True)
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        self.allowed_extensions = {".jpg", ".jpeg", ".png", ".webp", ".gif"}

    def validate_image(self, file) -> Dict[str, Any]:
        """Validate uploaded image file"""
        if not file or not file.filename:
            return {"valid": False, "error": "No file provided"}

        ext = Path(file.filename).suffix.lower()
        if ext not in self.allowed_extensions:
            return {"valid": False, "error": f"Invalid file type. Allowed: {', '.join(self.allowed_extensions)}"}

        file.seek(0, 2)
        size = file.tell()
        file.seek(0)

        if size > self.max_file_size:
            return {"valid": False, "error": f"File too large. Max size: {self.max_file_size // (1024*1024)}MB"}

        try:
            img = Image.open(file.stream)
            img.verify()
            file.seek(0)
        except Exception:
            return {"valid": False, "error": "Invalid image file"}

        return {"valid": True}

    def save_image(self, file) -> str:
        """Save uploaded image and return path"""
        import uuid
        ext = Path(file.filename).suffix.lower()
        filename = f"{uuid.uuid4().hex}{ext}"
        filepath = self.upload_dir / filename
        file.save(filepath)
        return str(filepath)

    def identify_plant(self, image_path: str) -> Dict[str, Any]:
        """
        Identify plant from image.
        DEMO MODE: Returns a mock identification based on filename or random selection.
        """
        import random

        filename = Path(image_path).stem.lower()

        for key, plant in self.DEMO_PLANT_MAPPING.items():
            if key in filename:
                return {
                    "plant_name": plant,
                    "confidence": 0.95,
                    "demo_mode": True,
                    "message": f"Demo identification: This appears to be a {plant} based on filename analysis."
                }

        plant_name = random.choice(list(self.DEMO_PLANT_MAPPING.values()))
        return {
            "plant_name": plant_name,
            "confidence": 0.72,
            "demo_mode": True,
            "message": f"Demo identification: Randomly selected {plant_name} for demonstration. In production, this would use a trained ML model."
        }

    def get_image_base64(self, image_path: str) -> str:
        """Convert image to base64 for display"""
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")


def get_image_service(upload_dir: str = "uploads") -> ImageService:
    """Factory function"""
    return ImageService(upload_dir)