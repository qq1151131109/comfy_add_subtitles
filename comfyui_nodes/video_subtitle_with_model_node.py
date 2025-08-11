"""
ComfyUI视频字幕生成节点（使用预加载模型版本）
支持接收预加载的Whisper模型，避免重复加载
"""

import os
import sys
import tempfile
import logging
import time
from typing import Dict, Any, Tuple
import folder_paths
# 添加父目录到Python路径以支持导入
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

# 导入服务和核心模块
try:
    from ..services.audio_service import AudioService
    from ..services.subtitle_service import SubtitleService
    from ..services.video_service import VideoService
    from ..services.whisper_service import WhisperService
    from ..core.subtitle_style import SubtitlePosition, PresetStyles
except ImportError:
    try:
        from services.audio_service import AudioService
        from services.subtitle_service import SubtitleService
        from services.video_service import VideoService
        from services.whisper_service import WhisperService
        from core.subtitle_style import SubtitlePosition, PresetStyles
    except ImportError:
        from audio_service import AudioService
        from subtitle_service import SubtitleService
        from video_service import VideoService
        from whisper_service import WhisperService


def flush_line(line_text, line_start, end_time, transcript_lines):
    """将当前累计的行写入 transcript_lines，并重置行状态。

    返回重置后的 (line_text, line_start)。
    """
    text_out = (line_text or "").strip()
    if text_out and line_start is not None:
        transcript_lines.append(
            f"[{line_start:.2f}s -> {end_time:.2f}s] {text_out}"
        )
    return "", None


class VideoSubtitleWithModelNode:
    """ComfyUI视频字幕添加节点（使用预加载模型）"""
    
    def __init__(self):
        self.audio_service = AudioService()
        self.subtitle_service = SubtitleService()
        self.video_service = VideoService()
        
    @classmethod
    def INPUT_TYPES(cls):
        """定义节点输入类型"""
        return {
            "required": {
                "whisper_model": ("WHISPER_MODEL", {
                    "tooltip": "从Whisper模型加载节点获取的预加载模型"
                }),
                "video_path": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "placeholder": "输入视频文件路径"
                }),
                "output_prefix": ("STRING", {
                    "default": "subtitle_output",
                    "multiline": False,
                    "placeholder": "输出目录前缀（将拼接到ComfyUI输出目录后）"
                }),
                "output_mode": ([
                    "line",
                    "word",
                ], {
                    "default": "line",
                    "tooltip": "字幕输出粒度：line=按标点换行的句子；word=按词"
                }),
                "subtitle_style": ([
                    "default", "cinema", "youtube", "minimal", 
                    "top_news", "strong_shadow", "dramatic_shadow"
                ], {
                    "default": "strong_shadow",
                    "tooltip": "预设字幕样式"
                })
            },
            "optional": {
                "custom_font_size": ("INT", {
                    "default": 24,
                    "min": 12,
                    "max": 72,
                    "step": 1,
                    "tooltip": "自定义字体大小"
                }),
                "max_chars_per_line": ("INT", {
                    "default": 30,
                    "min": 10,
                    "max": 120,
                    "step": 1,
                    "tooltip": "行模式：单条字幕最大字符数，达到后提前换行"
                }),
                "custom_position": ([
                    "none", "bottom_center", "bottom_left", "bottom_right",
                    "top_center", "top_left", "top_right", "center"
                ], {
                    "default": "none",
                    "tooltip": "自定义字幕位置"
                }),
                "font_color_r": ("INT", {
                    "default": 255,
                    "min": 0,
                    "max": 255,
                    "step": 1,
                    "tooltip": "字体红色分量"
                }),
                "font_color_g": ("INT", {
                    "default": 255,
                    "min": 0,
                    "max": 255,
                    "step": 1,
                    "tooltip": "字体绿色分量"
                }),
                "font_color_b": ("INT", {
                    "default": 255,
                    "min": 0,
                    "max": 255,
                    "step": 1,
                    "tooltip": "字体蓝色分量"
                }),
                "enable_shadow": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "是否启用字幕阴影"
                }),
                "language_hint": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "placeholder": "语言提示(如:zh,en)，留空自动检测",
                    "tooltip": "指定音频语言以提高识别准确度"
                })
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("output_video_path", "subtitle_file_path", "transcription_text", "error_msg")
    FUNCTION = "process_video"
    CATEGORY = "Video/Subtitle"
    OUTPUT_NODE = True
    
    def _build_ui_output(self, output_video_path: str, srt_path: str, transcription_text: str, error_msg: str):
        """将关键结果暴露到 Comfy 的 UI 输出，以便 API 返回的 outputs 能读取。
        文本放在 ui['text']，文件以类似 SaveImage 的结构放在 ui['files']。
        """
        ui_text_items = []
        ui_files = []
        if len(output_video_path) > 0:
            ui_text_items.append({"title": "output_video_path", "content": output_video_path})
            ui_files.append({
                "filename": os.path.basename(output_video_path),
                "subfolder": os.path.dirname(output_video_path),
                "type": "output",
            })
        else:
            ui_text_items.append({"title": "output_video_path", "content": "None"})
        if len(srt_path) > 0:
            ui_text_items.append({"title": "subtitle_file_path", "content": srt_path})
            ui_files.append({
                "filename": os.path.basename(srt_path),
                "subfolder": os.path.dirname(srt_path),
                "type": "subtitle",
            })
        else:
            ui_text_items.append({"title": "subtitle_file_path", "content": "None"})

        if len(transcription_text) > 0:
            ui_text_items.append({"title": "transcription_text", "content": transcription_text})
        else:
            ui_text_items.append({"title": "transcription_text", "content": "None"})

        if len(error_msg) > 0:
            ui_text_items.append({"title": "error_msg", "content": error_msg})
        else:
            ui_text_items.append({"title": "error_msg", "content": "None"})

        ui = {}
        ui["text"] = ui_text_items
        ui["files"] = ui_files
        return ui

    def process_video(self, whisper_model: WhisperService, video_path: str, 
                     output_prefix: str, subtitle_style: str, **kwargs) -> Tuple[str, str, str, str]:
        """
        处理视频添加字幕（使用预加载模型）
        
        Args:
            whisper_model: 预加载的Whisper模型服务
            video_path: 输入视频路径
            output_prefix: 输出目录前缀(拼接到ComfyUI输出目录后)
            subtitle_style: 字幕样式
            **kwargs: 可选参数
            
        Returns:
            (输出视频路径, 字幕文件路径, 转录文本, 处理日志)
        """
        try:
            # 验证模型
            if whisper_model is None:
                error_msg = "❌ Whisper模型未加载或加载失败,请先使用Whisper模型加载节点"
                return {
                    "ui": self._build_ui_output("", "", "", error_msg),
                    "result": ("", "", "", error_msg)
                }
            
            # 验证输入文件
            if not os.path.exists(video_path):
                error_msg = f"❌ 视频文件不存在: {video_path}"
                return {
                    "ui": self._build_ui_output("", "", "", error_msg),
                    "result": ("", "", "", error_msg)
                }
            
            # 获取ComfyUI输出目录并拼接前缀
            if folder_paths is not None:
                comfy_output_dir = folder_paths.get_output_directory()
                output_dir = os.path.join(comfy_output_dir, output_prefix)
            else:
                # 如果不在ComfyUI环境中，使用默认输出目录
                output_dir = os.path.join("./output", output_prefix)
            
            # 创建输出目录
            os.makedirs(output_dir, exist_ok=True)
            
            # 设置日志记录
            # 生成唯一文件名（使用时间戳避免冲突）
            video_name = os.path.splitext(os.path.basename(video_path))[0]
            timestamp = int(time.time())
            unique_suffix = f"_{timestamp}"
            
            audio_path = os.path.join(output_dir, f"{video_name}{unique_suffix}.wav")
            srt_path = os.path.join(output_dir, f"{video_name}{unique_suffix}.srt")
            output_video_path = os.path.join(output_dir, f"{video_name}{unique_suffix}_with_subtitles.mp4")
            
            # 步骤1: 从视频中提取音频
            print("🎵 步骤1: 提取音频...")
            if not self.audio_service.extract_audio_from_video(video_path, audio_path):
                error_msg = "❌ 音频提取失败"
                return {
                    "ui": self._build_ui_output("", "", "", error_msg),
                    "result": ("", "", "", error_msg)
                }
            
            # 验证音频文件
            if not self.audio_service.validate_audio_file(audio_path):
                error_msg = "❌ 音频文件验证失败"
                return {
                    "ui": self._build_ui_output("", "", "", error_msg),
                    "result": ("", "", "", error_msg)
                }
            
            # 步骤2: 使用预加载的Whisper模型进行语音识别（支持词级或行级输出）
            print("🎙️ 步骤2: 语音识别...")

            # 使用预加载模型直接转录
            if hasattr(whisper_model, '_model') and whisper_model._model is not None:
                try:
                    # 启用词级时间戳，便于两种模式的时间计算
                    segments, info = whisper_model._model.transcribe(
                        audio_path,
                        beam_size=5,
                        word_timestamps=True
                    )

                    # 根据输出模式组装字幕条目
                    output_mode = kwargs.get("output_mode", "line")
                    max_chars_per_line = kwargs.get("max_chars_per_line", 30)
                    transcript_lines = []
                    full_text = ""

                    # 简易的中英文标点集合
                    punctuation_chars = set(
                        list(",.!?;:") + list("，。！？；：、")
                    )

                    def needs_space(prev_char: str, next_char: str) -> bool:
                        import re
                        return bool(re.match(r"[A-Za-z0-9]", prev_char or "")) and bool(re.match(r"[A-Za-z0-9]", next_char or ""))

                    if output_mode == "word":
                        # 每个词一条
                        for segment in segments:
                            if hasattr(segment, 'words') and segment.words:
                                for w in segment.words:
                                    word_text = (w.word or "").strip()
                                    if not word_text:
                                        continue
                                    transcript_lines.append(
                                        f"[{getattr(w, 'start', segment.start):.2f}s -> {getattr(w, 'end', segment.end):.2f}s] {word_text}"
                                    )
                                    full_text += word_text + " "
                            else:
                                transcript_lines.append(
                                    f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}"
                                )
                                full_text += (segment.text or "") + " "
                    else:
                        # line: 按标点换行，将词合并为句子
                        for segment in segments:
                            if hasattr(segment, 'words') and segment.words:
                                line_start = None
                                line_text = ""
                                last_char = ""
                                last_word_end = None

                                for w in segment.words:
                                    word_text_raw = (w.word or "")
                                    word_text = word_text_raw.strip()
                                    if not word_text:
                                        continue

                                    if line_start is None:
                                        line_start = getattr(w, 'start', segment.start)

                                    # 拼接时中英文间自动加空格（仅英文字母/数字之间）
                                    pending = word_text
                                    add_space = line_text and needs_space(last_char[-1:] if last_char else "", word_text[:1] if word_text else "")
                                    candidate_text = (line_text + (" " if add_space else "") + pending) if line_text else pending

                                    # 字符长度限制：超过则以上一词结束时间断开
                                    if line_text and len(candidate_text) > max_chars_per_line and last_word_end is not None:
                                        line_text, line_start = flush_line(line_text, line_start, last_word_end, transcript_lines)
                                        # 断行后重新开始本词
                                        line_start = getattr(w, 'start', segment.start)
                                        line_text = pending
                                    else:
                                        # 接受追加
                                        if add_space:
                                            line_text += " "
                                        line_text += pending
                                    last_char = pending

                                    # 碰到标点则换行
                                    ending_char = word_text[-1]
                                    if ending_char in punctuation_chars:
                                        end_time = getattr(w, 'end', segment.end)
                                        line_text, line_start = flush_line(line_text, line_start, end_time, transcript_lines)
                                        last_word_end = end_time
                                        continue

                                    # 记录当前词结束时间，用于后续长度断行或收尾
                                    last_word_end = getattr(w, 'end', segment.end)

                                # 处理残留行
                                if line_text and line_start is not None:
                                    end_time = last_word_end if last_word_end is not None else getattr(segment.words[-1], 'end', segment.end)
                                    line_text, line_start = flush_line(line_text, line_start, end_time, transcript_lines)
                            else:
                                # 无词级别信息时，整段作为一行
                                transcript_lines.append(
                                    f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}"
                                )
                                
                            # 汇总全文
                            full_text += (segment.text or "") + " "

                    whisper_result = {
                        'language': info.language,
                        'language_probability': info.language_probability,
                        'segments': transcript_lines,
                        'full_text': full_text.strip()
                    }

                except Exception as e:
                    error_msg = f"❌ 模型转录失败: {str(e)}"
                    return {
                        "ui": self._build_ui_output("", "", "", error_msg),
                        "result": ("", "", "", error_msg)
                    }
            else:
                error_msg = "❌ 模型未正确加载"
                return {
                    "ui": self._build_ui_output("", "", "", error_msg),
                    "result": ("", "", "", error_msg)
                }
            
            if not whisper_result:
                error_msg = "❌ 语音识别失败"
                return {
                    "ui": self._build_ui_output("", "", "", error_msg),
                    "result": ("", "", "", error_msg)
                }
            
            # 输出识别信息
            language = whisper_result.get('language', 'unknown')
            language_name = whisper_model.get_language_name(language)
            confidence = whisper_result.get('language_probability', 0)
            full_text = whisper_result.get('full_text', '')
            
            print(f"✅ 识别语言: {language_name} (置信度: {confidence:.2f})")
            print(f"📝 识别到 {len(whisper_result['segments'])} 个语音段落")
            
            # 步骤3: 生成SRT字幕文件
            print("📄 步骤3: 生成字幕文件...")
            if not self.subtitle_service.generate_srt_from_whisper_result(whisper_result, srt_path):
                error_msg = "❌ 字幕文件生成失败"
                return {
                    "ui": self._build_ui_output("", "", "", error_msg),
                    "result": ("", "", "", error_msg)
                }
            
            # 验证字幕文件
            if not self.subtitle_service.validate_srt_file(srt_path):
                error_msg = "❌ 字幕文件验证失败"
                return {
                    "ui": self._build_ui_output("", srt_path, full_text, error_msg),
                    "result": ("", srt_path, full_text, error_msg)
                }
            
            # 输出字幕信息
            subtitle_info = self.subtitle_service.get_subtitle_info(srt_path)
            if subtitle_info:
                print(f"📊 字幕条目数: {subtitle_info['entry_count']}")
                print(f"📏 字幕文件大小: {subtitle_info['file_size']} 字节")
            
            # 处理自定义样式
            custom_style = self._create_custom_style(subtitle_style, **kwargs)
            
            # 步骤4: 将字幕嵌入视频
            print("🎬 步骤4: 嵌入字幕...")
            
            # 确定使用的字幕样式
            if custom_style:
                # 使用自定义样式
                if not self.video_service.embed_subtitles(video_path, srt_path, output_video_path, custom_style):
                    error_msg = "❌ 字幕嵌入失败"
                    return {
                        "ui": self._build_ui_output("", srt_path, full_text, error_msg),
                        "result": ("", srt_path, full_text, error_msg)
                    }
            else:
                # 使用预设样式
                if not self.video_service.embed_subtitles_with_preset(video_path, srt_path, output_video_path, subtitle_style):
                    error_msg = "❌ 字幕嵌入失败"
                    return {
                        "ui": self._build_ui_output("", srt_path, full_text, error_msg),
                        "result": ("", srt_path, full_text, error_msg)
                    }
            
            # 获取输出视频信息
            video_info = self.video_service.get_video_info_local(output_video_path)
            if video_info:
                duration = video_info.get('duration', 0)
                size_mb = video_info.get('size', 0) / (1024 * 1024)
                print(f"⏱️ 输出视频时长: {duration:.2f}秒")
                print(f"💾 输出视频大小: {size_mb:.2f}MB")
            
            print("🎉 处理完成！输出文件:")
            print(f"  📹 带字幕视频: {output_video_path}")
            print(f"  📄 字幕文件: {srt_path}")
            
            # 清理临时音频文件
            try:
                os.remove(audio_path)
                print("🧹 临时音频文件已清理")
            except:
                pass
            
            # 返回 UI + 结果，UI 用于 API 直接读取
            return {
                "ui": self._build_ui_output(output_video_path, srt_path, full_text, ""),
                "result": (output_video_path, srt_path, full_text, "")
            }
            
        except Exception as e:
            error_msg = f"❌ 处理过程中发生错误: {str(e)}"
            return {
                "ui": self._build_ui_output("", "", "", error_msg),
                "result": ("", "", "", error_msg)
            }
    
    def _create_custom_style(self, base_style_name: str, **kwargs):
        """
        创建自定义样式
        
        Args:
            base_style_name: 基础样式名称
            **kwargs: 自定义参数
            
        Returns:
            自定义样式对象或None
        """
        custom_font_size = kwargs.get("custom_font_size", 24)
        custom_position = kwargs.get("custom_position", "none")
        font_color_r = kwargs.get("font_color_r", 255)
        font_color_g = kwargs.get("font_color_g", 255)
        font_color_b = kwargs.get("font_color_b", 255)
        enable_shadow = kwargs.get("enable_shadow", True)
        
        # 检查是否有自定义设置
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
            
            return base_style
        
        return None


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


# ComfyUI节点注册
NODE_CLASS_MAPPINGS = {
    "VideoSubtitleWithModelNode": VideoSubtitleWithModelNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "VideoSubtitleWithModelNode": "🎬 Video Subtitle (with Model)"
}

# 测试代码
if __name__ == "__main__":
    print("🧪 测试视频字幕节点（预加载模型版本）...")
    
    # 先测试Whisper模型加载
    from whisper_model_node import WhisperModelNode
    
    model_node = WhisperModelNode()
    whisper_service, model_info = model_node.load_model("small", "cuda", "float16")
    
    print("📋 模型加载结果:")
    print(model_info)
    
    if whisper_service and os.path.exists("test.mp4"):
        # 测试视频字幕生成
        subtitle_node = VideoSubtitleWithModelNode()
        
        output_video, subtitle_file, transcription, log = subtitle_node.process_video(
            whisper_model=whisper_service,
            video_path="test.mp4",
            output_prefix="test_with_model_output",
            subtitle_style="strong_shadow"
        )
        
        print("\n📋 字幕生成结果:")
        print(f"输出视频: {output_video}")
        print(f"字幕文件: {subtitle_file}")
        print(f"转录文本: {transcription[:100]}...")
        print(f"\n处理日志:\n{log}")
    
    print("\n✅ 测试完成!")