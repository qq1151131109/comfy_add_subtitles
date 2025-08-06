"""
ComfyUI节点模块
包含所有ComfyUI自定义节点
"""

# 导入所有节点
from .comfyui_subtitle_node import VideoSubtitleNode
from .whisper_model_node import (
    WhisperModelNode, 
    WhisperTranscribeNode, 
    WhisperCacheManagerNode
)
from .video_subtitle_with_model_node import VideoSubtitleWithModelNode

# ComfyUI节点注册
NODE_CLASS_MAPPINGS = {
    # 原始节点（向下兼容）
    "VideoSubtitleNode": VideoSubtitleNode,
    
    # 模块化节点
    "WhisperModelNode": WhisperModelNode,
    "WhisperTranscribeNode": WhisperTranscribeNode, 
    "WhisperCacheManagerNode": WhisperCacheManagerNode,
    "VideoSubtitleWithModelNode": VideoSubtitleWithModelNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    # 原始节点
    "VideoSubtitleNode": "🎬 Video Subtitle Generator (Legacy)",
    
    # 模块化节点
    "WhisperModelNode": "🤖 Whisper Model Loader",
    "WhisperTranscribeNode": "🎙️ Whisper Transcribe",
    "WhisperCacheManagerNode": "🗂️ Whisper Cache Manager", 
    "VideoSubtitleWithModelNode": "🎬 Video Subtitle (with Model)"
}

__all__ = [
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS",
    "VideoSubtitleNode",
    "WhisperModelNode",
    "WhisperTranscribeNode", 
    "WhisperCacheManagerNode",
    "VideoSubtitleWithModelNode"
]