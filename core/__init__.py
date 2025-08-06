"""
核心模块
包含字幕样式配置等核心功能
"""

from .subtitle_style import (
    SubtitleStyle, 
    SubtitlePosition, 
    PresetStyles, 
    FontWeight
)

__all__ = [
    "SubtitleStyle",
    "SubtitlePosition", 
    "PresetStyles",
    "FontWeight"
]