"""
ComfyUI视频字幕生成工具
一个功能完整的视频自动字幕生成解决方案
"""

# 导入ComfyUI节点映射
from .comfyui_nodes import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

# ComfyUI所需的导出
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']

# 包信息
__version__ = "1.2.0"
__author__ = "Video Subtitle Generator Team"
__description__ = "ComfyUI nodes for automatic video subtitle generation using Whisper"
__license__ = "MIT"

# 项目信息
PROJECT_NAME = "ComfyUI Video Subtitle Generator"