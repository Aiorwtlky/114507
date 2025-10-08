# ai_core/__init__.py
"""
AI 核心模組
提供攝影機管理、幀處理、事件分發等基礎設施
"""

from .camera_manager import CameraManager
from .frame_processor import FrameProcessor
from .event_dispatcher import EventDispatcher

__all__ = ['CameraManager', 'FrameProcessor', 'EventDispatcher']