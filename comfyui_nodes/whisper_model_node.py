"""
ComfyUI Whisper模型加载节点
单独管理Whisper模型的加载和缓存
"""

import os
import sys
import logging
from typing import Dict, Any, Tuple, Optional

# 添加父目录到Python路径以支持导入
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

# 导入服务
try:
    from ..services.whisper_service import WhisperService
except ImportError:
    try:
        from services.whisper_service import WhisperService
    except ImportError:
        from whisper_service import WhisperService


class WhisperModelNode:
    """Whisper模型加载节点"""
    
    # 全局模型缓存，避免重复加载
    _model_cache = {}
    
    def __init__(self):
        pass
        
    @classmethod
    def INPUT_TYPES(cls):
        """定义节点输入类型"""
        return {
            "required": {
                "model_size": ([
                    "tiny", "base", "small", "medium", 
                    "large", "large-v2", "large-v3"
                ], {
                    "default": "large-v3",
                    "tooltip": "Whisper模型大小，越大越准确但需要更多内存"
                }),
                "device": (["cuda", "cpu"], {
                    "default": "cuda",
                    "tooltip": "计算设备，GPU加速需要CUDA支持"
                }),
                "compute_type": ([
                    "float16", "float32", "int8", "int16"
                ], {
                    "default": "float16",
                    "tooltip": "计算精度，float16节省内存，int8更快但精度稍低"
                })
            },
            "optional": {
                "force_reload": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "强制重新加载模型，即使已缓存"
                })
            }
        }
    
    RETURN_TYPES = ("WHISPER_MODEL", "STRING")
    RETURN_NAMES = ("whisper_model", "model_info")
    FUNCTION = "load_model"
    CATEGORY = "Audio/Whisper"
    
    def load_model(self, model_size: str, device: str, compute_type: str, 
                   force_reload: bool = False) -> Tuple[WhisperService, str]:
        """
        加载Whisper模型
        
        Args:
            model_size: 模型大小
            device: 计算设备
            compute_type: 计算类型
            force_reload: 是否强制重新加载
            
        Returns:
            (WhisperService实例, 模型信息字符串)
        """
        try:
            # 创建模型标识符
            model_key = f"{model_size}_{device}_{compute_type}"
            
            # 检查缓存
            if not force_reload and model_key in self._model_cache:
                cached_service = self._model_cache[model_key]
                model_info = f"✅ 使用缓存模型: {model_size} ({device}, {compute_type})"
                return cached_service, model_info
            
            # 创建新的WhisperService实例
            whisper_service = WhisperService()
            
            # 预加载模型以验证可用性
            model_info_lines = [
                f"🔄 加载Whisper模型...",
                f"模型大小: {model_size}",
                f"计算设备: {device}",
                f"计算类型: {compute_type}"
            ]
            
            # 尝试加载模型
            try:
                # 通过调用内部方法预加载模型
                model = whisper_service._load_model(model_size, device, compute_type)
                
                # 获取模型信息
                model_info_lines.extend([
                    f"✅ 模型加载成功",
                    f"模型类型: {type(model).__name__}",
                    f"缓存键: {model_key}"
                ])
                
                # 缓存模型服务
                self._model_cache[model_key] = whisper_service
                
                model_info = "\n".join(model_info_lines)
                return whisper_service, model_info
                
            except Exception as e:
                error_info = f"❌ 模型加载失败: {str(e)}"
                model_info_lines.append(error_info)
                model_info = "\n".join(model_info_lines)
                
                # 返回None和错误信息
                return None, model_info
                
        except Exception as e:
            error_msg = f"❌ 节点执行错误: {str(e)}"
            return None, error_msg
    
    @classmethod
    def clear_cache(cls):
        """清除所有缓存的模型"""
        for service in cls._model_cache.values():
            if hasattr(service, 'clear_model_cache'):
                service.clear_model_cache()
        cls._model_cache.clear()
    
    @classmethod
    def get_cache_info(cls) -> str:
        """获取缓存信息"""
        if not cls._model_cache:
            return "📭 没有缓存的模型"
        
        info_lines = ["📦 缓存的模型:"]
        for key in cls._model_cache.keys():
            info_lines.append(f"  - {key}")
        
        return "\n".join(info_lines)


class WhisperTranscribeNode:
    """Whisper音频转录节点"""
    
    def __init__(self):
        pass
        
    @classmethod
    def INPUT_TYPES(cls):
        """定义节点输入类型"""
        return {
            "required": {
                "whisper_model": ("WHISPER_MODEL", {
                    "tooltip": "从Whisper模型加载节点获取的模型"
                }),
                "audio_path": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "placeholder": "音频文件路径"
                })
            },
            "optional": {
                "language": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "placeholder": "指定语言代码(如:zh,en)，留空自动检测"
                }),
                "beam_size": ("INT", {
                    "default": 5,
                    "min": 1,
                    "max": 10,
                    "step": 1,
                    "tooltip": "束搜索大小，越大越准确但越慢"
                })
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "FLOAT", "STRING")
    RETURN_NAMES = ("transcription", "language", "confidence", "segments_info")
    FUNCTION = "transcribe_audio"
    CATEGORY = "Audio/Whisper"
    
    def transcribe_audio(self, whisper_model: WhisperService, audio_path: str,
                        language: str = "", beam_size: int = 5) -> Tuple[str, str, float, str]:
        """
        使用Whisper模型转录音频
        
        Args:
            whisper_model: Whisper模型服务实例
            audio_path: 音频文件路径
            language: 指定语言（可选）
            beam_size: 束搜索大小
            
        Returns:
            (转录文本, 检测语言, 置信度, 段落信息)
        """
        try:
            # 验证模型
            if whisper_model is None:
                error_msg = "❌ Whisper模型未加载或加载失败"
                return "", "", 0.0, error_msg
            
            # 验证音频文件
            if not os.path.exists(audio_path):
                error_msg = f"❌ 音频文件不存在: {audio_path}"
                return "", "", 0.0, error_msg
            
            # 执行转录 - 直接调用内部方法，因为模型已经加载
            if hasattr(whisper_model, '_model') and whisper_model._model is not None:
                # 直接使用已加载的模型进行转录
                try:
                    segments, info = whisper_model._model.transcribe(audio_path, beam_size=beam_size)
                    
                    # 收集所有文案
                    transcript_lines = []
                    full_text = ""
                    
                    for segment in segments:
                        timestamp_line = f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}"
                        transcript_lines.append(timestamp_line)
                        full_text += segment.text + " "
                    
                    result = {
                        'language': info.language,
                        'language_probability': info.language_probability,
                        'segments': transcript_lines,
                        'full_text': full_text.strip()
                    }
                    
                except Exception as e:
                    error_msg = f"❌ 模型转录失败: {str(e)}"
                    return "", "", 0.0, error_msg
            else:
                error_msg = "❌ 模型未正确加载"
                return "", "", 0.0, error_msg
            
            if result is None:
                error_msg = "❌ 音频转录失败"
                return "", "", 0.0, error_msg
            
            # 提取结果
            full_text = result.get('full_text', '')
            language_code = result.get('language', 'unknown')
            confidence = result.get('language_probability', 0.0)
            segments = result.get('segments', [])
            
            # 生成段落信息
            segments_info_lines = [
                f"🎯 转录完成",
                f"检测语言: {whisper_model.get_language_name(language_code)} ({language_code})",
                f"置信度: {confidence:.2f}",
                f"段落数: {len(segments)}",
                f"文本长度: {len(full_text)} 字符"
            ]
            
            if segments:
                segments_info_lines.append("📝 前3个段落:")
                for i, segment in enumerate(segments[:3], 1):
                    segments_info_lines.append(f"  {i}. {segment}")
                
                if len(segments) > 3:
                    segments_info_lines.append(f"  ... 还有 {len(segments) - 3} 个段落")
            
            segments_info = "\n".join(segments_info_lines)
            
            return full_text, language_code, confidence, segments_info
            
        except Exception as e:
            error_msg = f"❌ 转录过程中发生错误: {str(e)}"
            return "", "", 0.0, error_msg


class WhisperCacheManagerNode:
    """Whisper缓存管理节点"""
    
    def __init__(self):
        pass
        
    @classmethod
    def INPUT_TYPES(cls):
        """定义节点输入类型"""
        return {
            "required": {
                "action": (["get_info", "clear_cache"], {
                    "default": "get_info",
                    "tooltip": "选择操作：获取缓存信息或清除缓存"
                })
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("cache_info",)
    FUNCTION = "manage_cache"
    CATEGORY = "Audio/Whisper"
    
    def manage_cache(self, action: str) -> Tuple[str]:
        """
        管理Whisper模型缓存
        
        Args:
            action: 操作类型
            
        Returns:
            缓存信息字符串
        """
        try:
            if action == "get_info":
                cache_info = WhisperModelNode.get_cache_info()
                return (cache_info,)
            elif action == "clear_cache":
                WhisperModelNode.clear_cache()
                return ("🗑️ 所有Whisper模型缓存已清除",)
            else:
                return (f"❌ 未知操作: {action}",)
                
        except Exception as e:
            error_msg = f"❌ 缓存管理错误: {str(e)}"
            return (error_msg,)


# ComfyUI节点注册
NODE_CLASS_MAPPINGS = {
    "WhisperModelNode": WhisperModelNode,
    "WhisperTranscribeNode": WhisperTranscribeNode,
    "WhisperCacheManagerNode": WhisperCacheManagerNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "WhisperModelNode": "🤖 Whisper Model Loader",
    "WhisperTranscribeNode": "🎙️ Whisper Transcribe",
    "WhisperCacheManagerNode": "🗂️ Whisper Cache Manager"
}

# 测试代码
if __name__ == "__main__":
    print("🧪 测试Whisper节点...")
    
    # 测试模型加载节点
    model_node = WhisperModelNode()
    whisper_service, model_info = model_node.load_model("small", "cuda", "float16")
    
    print("📋 模型加载结果:")
    print(model_info)
    
    if whisper_service and os.path.exists("test.mp4"):
        # 先提取音频用于测试
        from audio_service import AudioService
        audio_service = AudioService()
        audio_path = "./test_whisper.wav"
        
        # 从测试视频提取音频
        if audio_service.extract_audio_from_video("test.mp4", audio_path):
            print("\n🎙️ 测试音频转录...")
            
            # 测试转录节点
            transcribe_node = WhisperTranscribeNode()
            text, lang, conf, info = transcribe_node.transcribe_audio(
                whisper_service, audio_path
            )
            
            print("📝 转录结果:")
            print(f"文本: {text[:100]}...")
            print(f"语言: {lang}")
            print(f"置信度: {conf}")
            print("\n" + info)
            
            # 清理测试文件
            os.remove(audio_path)
        
        # 测试缓存管理
        cache_node = WhisperCacheManagerNode()
        cache_info = cache_node.manage_cache("get_info")
        print("\n" + cache_info[0])
    
    print("\n✅ Whisper节点测试完成!")