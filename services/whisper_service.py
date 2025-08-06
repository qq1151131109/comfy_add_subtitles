"""
Whisper转录服务
负责音频转文字处理
"""

import logging
from typing import Dict, Optional
from faster_whisper import WhisperModel

# 导入配置
try:
    from ..config import LANGUAGE_MAP
except ImportError:
    # 简化版语言映射（独立运行时使用）
    LANGUAGE_MAP = {
        'en': '英语',
        'zh': '中文',
        'ja': '日语',
        'ko': '韩语',
        'es': '西班牙语',
        'fr': '法语',
        'de': '德语',
        'ru': '俄语',
        'ar': '阿拉伯语',
        'hi': '印地语',
        'pt': '葡萄牙语',
        'it': '意大利语',
        'th': '泰语',
        'vi': '越南语'
    }

logger = logging.getLogger(__name__)


class WhisperService:
    """Whisper转录服务类"""
    
    def __init__(self):
        self._model = None
        self._current_model_config = None
    
    def _load_model(self, model_size: str, device: str, compute_type: str) -> WhisperModel:
        """
        加载Whisper模型（带缓存）
        
        Args:
            model_size: 模型大小
            device: 设备类型
            compute_type: 计算类型
            
        Returns:
            WhisperModel实例
        """
        current_config = (model_size, device, compute_type)
        
        # 如果模型配置相同，直接返回缓存的模型
        if self._model is not None and self._current_model_config == current_config:
            return self._model
        
        logger.info(f"正在加载Whisper模型: {model_size}, 设备: {device}, 计算类型: {compute_type}")
        
        try:
            # 根据设备选择计算类型
            if device == "cuda":
                model = WhisperModel(model_size, device=device, compute_type=compute_type)
            else:
                # CPU模式强制使用int8
                model = WhisperModel(model_size, device="cpu", compute_type="int8")
            
            # 缓存模型和配置
            self._model = model
            self._current_model_config = current_config
            
            logger.info(f"Whisper模型加载完成: {model_size}")
            return model
            
        except Exception as e:
            logger.error(f"Whisper模型加载失败: {e}")
            raise
    
    def transcribe_audio(self, audio_path: str, model_size: str = "large-v3", 
                        device: str = "cuda", compute_type: str = "float16") -> Optional[Dict]:
        """
        使用Whisper模型转录音频为文案
        
        Args:
            audio_path: 音频文件路径
            model_size: 模型大小
            device: 设备类型
            compute_type: 计算类型
            
        Returns:
            转录结果字典，包含language, language_probability, segments, full_text
            失败返回None
        """
        try:
            # 加载模型
            model = self._load_model(model_size, device, compute_type)
            
            logger.info(f"开始转录音频: {audio_path}")
            segments, info = model.transcribe(audio_path, beam_size=5)
            
            logger.info(f"检测到语言: {info.language} (置信度: {info.language_probability:.2f})")
            
            # 收集所有文案
            transcript_lines = []
            full_text = ""
            
            for segment in segments:
                timestamp_line = f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}"
                transcript_lines.append(timestamp_line)
                full_text += segment.text + " "
            
            return {
                'language': info.language,
                'language_probability': info.language_probability,
                'segments': transcript_lines,
                'full_text': full_text.strip()
            }
            
        except Exception as e:
            logger.error(f"音频转录失败: {e}")
            return None
    
    def get_language_name(self, language_code: str) -> str:
        """
        获取语言的中文名称
        
        Args:
            language_code: 语言代码
            
        Returns:
            语言的中文名称
        """
        return LANGUAGE_MAP.get(language_code, language_code)
    
    def clear_model_cache(self):
        """清除模型缓存"""
        self._model = None
        self._current_model_config = None
        logger.info("Whisper模型缓存已清除")