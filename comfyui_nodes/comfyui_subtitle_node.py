"""
ComfyUI自定义节点：视频字幕添加器
将视频字幕生成功能封装为ComfyUI节点
"""

import os
import sys
import tempfile
import logging
from typing import Dict, Any, Tuple

# 添加父目录到Python路径以支持导入
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

# 导入主生成器和样式
try:
    from ..main import SubtitleGenerator
    from ..core.subtitle_style import SubtitlePosition, PresetStyles
except ImportError:
    try:
        from main import SubtitleGenerator
        from core.subtitle_style import SubtitlePosition, PresetStyles
    except ImportError:
        # 创建简化版本的SubtitleGenerator
        from services.audio_service import AudioService
        from services.whisper_service import WhisperService
        from services.subtitle_service import SubtitleService
        from services.video_service import VideoService
        from core.subtitle_style import SubtitlePosition, PresetStyles
        
        class SubtitleGenerator:
            def __init__(self):
                self.audio_service = AudioService()
                self.whisper_service = WhisperService()
                self.subtitle_service = SubtitleService()
                self.video_service = VideoService()


class VideoSubtitleNode:
    """ComfyUI视频字幕添加节点"""
    
    def __init__(self):
        self.generator = SubtitleGenerator()
        
    @classmethod
    def INPUT_TYPES(cls):
        """定义节点输入类型"""
        return {
            "required": {
                "video_path": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "placeholder": "输入视频文件路径"
                }),
                "output_dir": ("STRING", {
                    "default": "./output",
                    "multiline": False,
                    "placeholder": "输出目录路径"
                }),
                "whisper_model": (["tiny", "base", "small", "medium", "large", "large-v2", "large-v3"], {
                    "default": "large-v3"
                }),
                "device": (["cuda", "cpu"], {
                    "default": "cuda"
                }),
                "subtitle_style": ([
                    "default", "cinema", "youtube", "minimal", 
                    "top_news", "strong_shadow", "dramatic_shadow",
                    "background_black", "background_blur", "colorful_background",
                    "elegant", "gaming"
                ], {
                    "default": "background_black"
                })
            },
            "optional": {
                "custom_font_size": ("INT", {
                    "default": 24,
                    "min": 12,
                    "max": 72,
                    "step": 1
                }),
                "custom_position": ([
                    "none", "bottom_center", "bottom_left", "bottom_right",
                    "bottom_10", "bottom_20", "bottom_30",
                    "top_center", "top_left", "top_right", 
                    "top_10", "top_20",
                    "center", "center_30", "center_70"
                ], {
                    "default": "none"
                }),
                "font_color_r": ("INT", {
                    "default": 255,
                    "min": 0,
                    "max": 255,
                    "step": 1
                }),
                "font_color_g": ("INT", {
                    "default": 255,
                    "min": 0,
                    "max": 255,
                    "step": 1
                }),
                "font_color_b": ("INT", {
                    "default": 255,
                    "min": 0,
                    "max": 255,
                    "step": 1
                }),
                "enable_shadow": ("BOOLEAN", {
                    "default": True
                })
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("output_video_path", "subtitle_file_path", "processing_log")
    FUNCTION = "process_video"
    CATEGORY = "Video/Subtitle"
    OUTPUT_NODE = True
    
    def process_video(self, video_path: str, output_dir: str, whisper_model: str, 
                     device: str, subtitle_style: str, **kwargs) -> Tuple[str, str, str]:
        """
        处理视频添加字幕
        
        Args:
            video_path: 输入视频路径
            output_dir: 输出目录
            whisper_model: Whisper模型大小
            device: 计算设备
            subtitle_style: 字幕样式
            **kwargs: 可选参数
            
        Returns:
            (输出视频路径, 字幕文件路径, 处理日志)
        """
        try:
            # 验证输入文件
            if not os.path.exists(video_path):
                error_msg = f"错误: 视频文件不存在 - {video_path}"
                return "", "", error_msg
            
            # 创建输出目录
            os.makedirs(output_dir, exist_ok=True)
            
            # 设置日志记录
            log_messages = []
            log_handler = LogHandler(log_messages)
            logger = logging.getLogger()
            logger.addHandler(log_handler)
            logger.setLevel(logging.INFO)
            
            # 处理自定义样式
            custom_style = None
            custom_font_size = kwargs.get("custom_font_size", 24)
            custom_position = kwargs.get("custom_position", "none")
            font_color_r = kwargs.get("font_color_r", 255)
            font_color_g = kwargs.get("font_color_g", 255)
            font_color_b = kwargs.get("font_color_b", 255)
            enable_shadow = kwargs.get("enable_shadow", True)
            
            if any([
                custom_position != "none",
                custom_font_size != 24,
                (font_color_r, font_color_g, font_color_b) != (255, 255, 255),
                enable_shadow is not True
            ]):
                # 创建自定义样式
                base_style = PresetStyles.default()
                
                # 应用自定义设置
                if custom_position != "none":
                    base_style.position = SubtitlePosition(custom_position)
                
                if custom_font_size != 24:
                    base_style.font_size = custom_font_size
                
                # 自定义颜色
                if (font_color_r, font_color_g, font_color_b) != (255, 255, 255):
                    base_style.font_color = (font_color_r, font_color_g, font_color_b)
                
                # 阴影设置
                base_style.shadow_enabled = enable_shadow
                
                custom_style = base_style
                subtitle_style = None  # 使用自定义样式时不使用预设
            
            # 处理视频
            log_messages.append(f"开始处理视频: {os.path.basename(video_path)}")
            log_messages.append(f"使用模型: {whisper_model}, 设备: {device}")
            log_messages.append(f"字幕样式: {subtitle_style if subtitle_style else 'custom'}")
            
            success = self.generator.generate_subtitles_for_video(
                video_path=video_path,
                output_dir=output_dir,
                model_size=whisper_model,
                device=device,
                subtitle_style=custom_style,
                preset_style=subtitle_style if not custom_style else None
            )
            
            if success:
                # 构建输出文件路径
                video_name = os.path.splitext(os.path.basename(video_path))[0]
                output_video_path = os.path.join(output_dir, f"{video_name}_with_subtitles.mp4")
                subtitle_file_path = os.path.join(output_dir, f"{video_name}.srt")
                
                log_messages.append("✅ 视频处理完成!")
                log_messages.append(f"输出视频: {output_video_path}")
                log_messages.append(f"字幕文件: {subtitle_file_path}")
                
                # 清理日志处理器
                logger.removeHandler(log_handler)
                
                return output_video_path, subtitle_file_path, "\n".join(log_messages)
            else:
                error_msg = "❌ 视频处理失败"
                log_messages.append(error_msg)
                logger.removeHandler(log_handler)
                return "", "", "\n".join(log_messages)
                
        except Exception as e:
            error_msg = f"❌ 处理过程中发生错误: {str(e)}"
            log_messages.append(error_msg)
            if 'logger' in locals() and 'log_handler' in locals():
                logger.removeHandler(log_handler)
            return "", "", "\n".join(log_messages)


class LogHandler(logging.Handler):
    """自定义日志处理器，用于收集日志消息"""
    
    def __init__(self, log_messages):
        super().__init__()
        self.log_messages = log_messages
    
    def emit(self, record):
        msg = self.format(record)
        # 过滤掉一些不必要的日志
        if any(skip in msg for skip in ['faster_whisper', 'Processing audio']):
            return
        self.log_messages.append(msg)


# ComfyUI节点注册（仅注册此文件中的节点）
NODE_CLASS_MAPPINGS = {
    "VideoSubtitleNode": VideoSubtitleNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "VideoSubtitleNode": "🎬 Video Subtitle Generator (Legacy)"
}

# 如果直接运行此文件，进行测试
if __name__ == "__main__":
    # 测试节点
    node = VideoSubtitleNode()
    
    # 测试参数
    test_video = "test.mp4"
    if os.path.exists(test_video):
        print("🧪 测试ComfyUI节点...")
        
        output_video, subtitle_file, log = node.process_video(
            video_path=test_video,
            output_dir="./comfyui_output",
            whisper_model="small",
            device="cuda",
            subtitle_style="strong_shadow"
        )
        
        print("📋 处理结果:")
        print(f"输出视频: {output_video}")
        print(f"字幕文件: {subtitle_file}")
        print(f"日志:\n{log}")
    else:
        print("❌ 未找到测试视频文件 test.mp4")