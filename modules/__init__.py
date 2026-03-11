"""
Moduli per la generazione di presentazioni
"""

from .document_parser import DocumentParser
from .image_extractor import ImageExtractor
from .ollama_client import OllamaClient
from .presentation_generator import PresentationGenerator

__all__ = [
    "DocumentParser",
    "ImageExtractor",
    "OllamaClient",
    "PresentationGenerator"
]
