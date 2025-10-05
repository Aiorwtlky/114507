# services/__init__.py
"""
AI 服務層
"""

from .ai_service import AIService
from .detection_service import DetectionService

__all__ = ['AIService', 'DetectionService']