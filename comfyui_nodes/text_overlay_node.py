"""
ComfyUI自定义节点：文本覆盖视频节点
为视频添加自定义文本覆盖功能
"""

import os
import sys
import logging
import tempfile
import time
from typing import Dict, Any, Tuple, Optional
from datetime import datetime

# 添加父目录到Python路径以支持导入
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

try:
    from ..services.text_overlay_service import TextOverlayService, TextOverlayStyle, TextAlignment, TextEffectType
    from ..core.subtitle_style import PresetStyles, SubtitleStyle, SubtitlePosition, FontWeight
except ImportError:
    from services.text_overlay_service import TextOverlayService, TextOverlayStyle, TextAlignment, TextEffectType
    from core.subtitle_style import PresetStyles, SubtitleStyle, SubtitlePosition, FontWeight


class ProgressLogger:
    """进度日志记录器"""
    
    def __init__(self, task_name: str):
        self.task_name = task_name
        self.start_time = time.time()
        self.last_update = self.start_time
        
    def log_progress(self, step: str, detail: str = "", progress_percent: float = None):
        """记录进度信息"""
        current_time = time.time()
        elapsed = current_time - self.start_time
        
        # 格式化输出
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        if progress_percent is not None:
            progress_bar = self._create_progress_bar(progress_percent)
            print(f"\033[32m[{timestamp}]\033[0m \033[36m{self.task_name}\033[0m - {step}")
            print(f"         {progress_bar} {progress_percent:.1f}%")
            if detail:
                print(f"         📝 {detail}")
        else:
            print(f"\033[32m[{timestamp}]\033[0m \033[36m{self.task_name}\033[0m - 🔄 {step}")
            if detail:
                print(f"         📝 {detail}")
        
        print(f"         ⏱️  已用时: {elapsed:.1f}秒")
        print()  # 空行分隔
        
    def log_success(self, message: str):
        """记录成功信息"""
        elapsed = time.time() - self.start_time
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"\033[32m[{timestamp}]\033[0m \033[36m{self.task_name}\033[0m - ✅ {message}")
        print(f"         ⏱️  总用时: {elapsed:.1f}秒")
        print()
        
    def log_error(self, message: str):
        """记录错误信息"""
        elapsed = time.time() - self.start_time
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"\033[31m[{timestamp}]\033[0m \033[36m{self.task_name}\033[0m - ❌ {message}")
        print(f"         ⏱️  用时: {elapsed:.1f}秒")
        print()
        
    def _create_progress_bar(self, percent: float, width: int = 30) -> str:
        """创建进度条"""
        filled = int(width * percent / 100)
        bar = "█" * filled + "░" * (width - filled)
        return f"[{bar}]"


class TextOverlayVideoNode:
    """ComfyUI文本覆盖视频节点"""
    
    def __init__(self):
        try:
            self.service = TextOverlayService()
            print("✅ TextOverlayService 初始化成功")
            
            # 初始化字体列表
            self._available_fonts = None
            self._load_available_fonts()
            
        except Exception as e:
            print(f"❌ TextOverlayService 初始化失败: {e}")
            import traceback
            print(traceback.format_exc())
            raise
        self.setup_logging()
    
    def _load_available_fonts(self):
        """加载系统可用字体"""
        try:
            fonts = self.service.get_available_fonts()
            if fonts and len(fonts) > 0:
                self._available_fonts = fonts
                print(f"✅ 成功检测到 {len(fonts)} 种可用字体")
                # 显示前10个字体作为示例
                print("📝 可用字体示例:", fonts[:10])
            else:
                print("⚠️ 未检测到系统字体，使用默认字体列表")
                self._available_fonts = self._get_fallback_fonts()
        except Exception as e:
            print(f"⚠️ 检测系统字体时出错: {e}")
            self._available_fonts = self._get_fallback_fonts()
    
    def _get_fallback_fonts(self):
        """获取备用字体列表"""
        return [
            "DejaVu Sans",
            "DejaVu Serif", 
            "DejaVu Sans Mono",
            "Liberation Sans",
            "Liberation Serif",
            "Liberation Mono",
            "WenQuanYi Zen Hei",
            "Lato",
            "Noto Sans",
            "Arial",
            "Times New Roman",
            "Courier New"
        ]
    
    def setup_logging(self):
        """设置日志配置"""
        # 配置终端日志输出
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            force=True
        )
        self.logger = logging.getLogger(f"TextOverlay_{id(self)}")
    
    def get_color_rgb(self, color_name: str) -> tuple:
        """将颜色名称转换为RGB值"""
        color_map = {
            # 中文颜色名称映射
            "黑色": (0, 0, 0),
            "白色": (255, 255, 255),
            "红色": (255, 0, 0),
            "绿色": (0, 255, 0),
            "蓝色": (0, 0, 255),
            "黄色": (255, 255, 0),
            "青色": (0, 255, 255),
            "洋红": (255, 0, 255),
            "橙色": (255, 165, 0),
            "紫色": (128, 0, 128),
            "灰色": (128, 128, 128),
            "深灰": (64, 64, 64),
            "浅灰": (192, 192, 192),
            "透明": (0, 0, 0),  # 透明背景用黑色，但会设置为完全透明
            # 兼容英文名称（向下兼容）
            "black": (0, 0, 0),
            "white": (255, 255, 255),
            "red": (255, 0, 0),
            "green": (0, 255, 0),
            "blue": (0, 0, 255),
            "yellow": (255, 255, 0),
            "cyan": (0, 255, 255),
            "magenta": (255, 0, 255),
            "orange": (255, 165, 0),
            "purple": (128, 0, 128),
            "gray": (128, 128, 128),
            "darkgray": (64, 64, 64),
            "lightgray": (192, 192, 192),
            "transparent": (0, 0, 0)
        }
        return color_map.get(color_name, (0, 0, 0))
    
    def get_position_preset(self, position_name: str) -> str:
        """将中文位置名称转换为英文预设名称"""
        position_map = {
            "底部居中": "bottom",
            "底部偏下": "bottom_low", 
            "底部偏上": "bottom_high",
            "屏幕中央": "center",
            "中央偏下": "center_low",
            "中央偏上": "center_high",
            "顶部居中": "top",
            "顶部偏下": "top_low",
            "顶部偏上": "top_high",
            # 兼容英文名称（向下兼容）
            "bottom": "bottom",
            "bottom_low": "bottom_low",
            "bottom_high": "bottom_high",
            "center": "center",
            "center_low": "center_low",
            "center_high": "center_high",
            "top": "top",
            "top_low": "top_low",
            "top_high": "top_high"
        }
        return position_map.get(position_name, "bottom")
    
    def get_text_alignment(self, alignment_name: str) -> str:
        """将中文对齐方式转换为英文"""
        alignment_map = {
            "居中": "center",
            "左对齐": "left",
            "右对齐": "right",
            # 兼容英文名称（向下兼容）
            "center": "center",
            "left": "left",
            "right": "right"
        }
        return alignment_map.get(alignment_name, "center")
    
    def get_tiktok_preset_style(self, preset_name: str) -> Optional[SubtitleStyle]:
        """获取TikTok预设样式"""
        preset_map = {
            "🔥 TikTok经典": PresetStyles.tiktok_classic,
            "✨ TikTok霓虹": PresetStyles.tiktok_neon,
            "💪 TikTok粗体": PresetStyles.tiktok_bold,
            "🌈 TikTok彩色": PresetStyles.tiktok_colorful,
            "🌟 TikTok简约": PresetStyles.tiktok_minimal,
            "📖 TikTok故事": PresetStyles.tiktok_story,
            "💃 TikTok舞蹈": PresetStyles.tiktok_dance,
            "💎 TikTok奢华": PresetStyles.tiktok_luxury
        }
        
        if preset_name in preset_map:
            return preset_map[preset_name]()
        return None
    
    def convert_subtitle_style_to_overlay_style(self, subtitle_style: SubtitleStyle) -> TextOverlayStyle:
        """将SubtitleStyle转换为TextOverlayStyle"""
        overlay_style = TextOverlayStyle()
        
        # 位置映射
        position_map = {
            SubtitlePosition.BOTTOM_CENTER: "bottom",
            SubtitlePosition.BOTTOM_LEFT: "bottom",
            SubtitlePosition.BOTTOM_RIGHT: "bottom", 
            SubtitlePosition.TOP_CENTER: "top",
            SubtitlePosition.TOP_LEFT: "top",
            SubtitlePosition.TOP_RIGHT: "top",
            SubtitlePosition.CENTER: "center",
            SubtitlePosition.CUSTOM: "center"
        }
        
        overlay_style.position_preset = position_map.get(subtitle_style.position, "bottom")
        overlay_style.margin_x = subtitle_style.margin_x
        
        # 字体设置
        overlay_style.font_family = subtitle_style.font_family
        overlay_style.font_size = subtitle_style.font_size
        overlay_style.font_color = subtitle_style.font_color
        overlay_style.font_bold = (subtitle_style.font_weight == FontWeight.BOLD)
        
        # 背景设置
        overlay_style.background_enabled = subtitle_style.background_enabled
        if len(subtitle_style.background_color) == 4:  # RGBA
            overlay_style.background_color = subtitle_style.background_color[:3]
            overlay_style.background_opacity = subtitle_style.background_color[3] / 255.0
        else:  # RGB
            overlay_style.background_color = subtitle_style.background_color
            overlay_style.background_opacity = 0.8
        overlay_style.background_padding = subtitle_style.background_padding
        
        # 阴影设置
        overlay_style.enable_shadow = subtitle_style.shadow_enabled
        overlay_style.shadow_color = subtitle_style.shadow_color
        overlay_style.shadow_offset_x = subtitle_style.shadow_offset_x
        overlay_style.shadow_offset_y = subtitle_style.shadow_offset_y
        
        # 边框设置
        overlay_style.enable_border = (subtitle_style.outline_width > 0)
        overlay_style.border_color = subtitle_style.outline_color
        overlay_style.border_width = subtitle_style.outline_width
        
        # 文本排版
        overlay_style.line_spacing = int(subtitle_style.line_spacing * 5)  # 转换为像素值
        
        return overlay_style
    
    def apply_visual_effect(self, style: TextOverlayStyle, effect_name: str) -> None:
        """应用视觉效果到样式"""
        if effect_name == "🌟 发光效果":
            style.glow_enabled = True
            style.glow_color = (255, 255, 255)
            style.glow_intensity = 8
            style.glow_spread = 2
            
        elif effect_name == "🎯 双重描边":
            style.double_outline_enabled = True
            style.outline_inner_width = 2
            style.outline_inner_color = (255, 255, 255)
            style.outline_outer_width = 5
            style.outline_outer_color = (0, 0, 0)
            
        elif effect_name == "💫 霓虹效果":
            style.neon_enabled = True
            style.neon_base_color = (255, 20, 147)  # 霓虹粉
            style.neon_glow_layers = 3
            style.neon_intensity = 10
            
        elif effect_name == "📦 3D立体阴影":
            style.shadow_3d_enabled = True
            style.shadow_3d_layers = 5
            style.shadow_3d_depth = 3
            style.shadow_3d_angle = 225
            
        elif effect_name == "⚡ 故障效果":
            style.glitch_enabled = True
            style.glitch_displacement = 3
            style.glitch_color_shift = True
    
    def wrap_text(self, text: str, max_chars_per_line: int) -> str:
        """
        文本自动换行处理
        
        Args:
            text: 原始文本
            max_chars_per_line: 每行最大字符数
            
        Returns:
            处理后的文本（包含换行符）
        """
        if not text:
            return text
            
        # 先处理已有的换行符
        lines = text.split('\n')
        wrapped_lines = []
        
        for line in lines:
            if len(line) <= max_chars_per_line:
                wrapped_lines.append(line)
                continue
                
            # 对长行进行处理
            current_line = ""
            words = line.split(' ')
            
            for word in words:
                # 如果单个单词就超过了最大长度，强制断开
                if len(word) > max_chars_per_line:
                    # 先添加当前行（如果有内容）
                    if current_line:
                        wrapped_lines.append(current_line.strip())
                        current_line = ""
                    
                    # 强制断开长单词
                    for i in range(0, len(word), max_chars_per_line):
                        chunk = word[i:i + max_chars_per_line]
                        wrapped_lines.append(chunk)
                    continue
                
                # 检查添加这个单词后是否会超过限制
                test_line = current_line + (" " if current_line else "") + word
                
                if len(test_line) <= max_chars_per_line:
                    current_line = test_line
                else:
                    # 当前行已满，开始新行
                    if current_line:
                        wrapped_lines.append(current_line.strip())
                    current_line = word
            
            # 添加最后一行
            if current_line:
                wrapped_lines.append(current_line.strip())
        
        return '\n'.join(wrapped_lines)
    
    @classmethod
    def _get_font_options(cls) -> list:
        """获取带语种标注的字体选项列表"""
        try:
            # 创建临时服务实例来获取字体
            service = TextOverlayService()
            labeled_fonts = service.font_manager.get_fonts_with_language_labels()
            if labeled_fonts and len(labeled_fonts) > 0:
                return labeled_fonts
        except Exception as e:
            print(f"获取字体列表时出错: {e}")
        
        # 返回备用带标签字体列表
        return [
            "[EN] DejaVu Sans",
            "[EN] DejaVu Serif", 
            "[EN] DejaVu Sans Mono",
            "[EN] Liberation Sans",
            "[EN] Liberation Serif",
            "[EN] Liberation Mono",
            "[CN] WenQuanYi Zen Hei",
            "[EN] Lato",
            "[EN] Noto Sans"
        ]
    
    @classmethod
    def _get_default_font(cls) -> str:
        """获取默认字体"""
        fonts = cls._get_font_options()
        if fonts:
            # 优先选择常见的英文无衬线字体（带标签版本）
            preferred_patterns = ["[EN] DejaVu Sans", "[EN] Liberation Sans", "[EN] Arial", "[EN] Lato"]
            for pattern in preferred_patterns:
                for font in fonts:
                    if pattern in font:
                        return font
            return fonts[0]  # 返回第一个可用字体
        return "[EN] DejaVu Sans"  # 最后的备用
    
    def get_text_stats(self, text: str) -> dict:
        """
        获取文本统计信息
        
        Args:
            text: 文本内容
            
        Returns:
            文本统计信息字典
        """
        lines = text.split('\n')
        return {
            'total_chars': len(text),
            'total_lines': len(lines),
            'max_line_length': max(len(line) for line in lines) if lines else 0,
            'avg_line_length': sum(len(line) for line in lines) / len(lines) if lines else 0
        }
        
    @classmethod
    def INPUT_TYPES(cls):
        """定义节点输入类型"""
        return {
            "required": {
                "images": ("IMAGE", {
                    "tooltip": "输入图像序列（来自视频或图像处理节点）"
                }),
                "文本内容": ("STRING", {
                    "default": "在这里输入文本内容",
                    "multiline": True,
                    "placeholder": "要显示在视频上的文本"
                }),
                "TikTok预设": ([
                    "不使用预设",
                    "🔥 TikTok经典",
                    "✨ TikTok霓虹", 
                    "💪 TikTok粗体",
                    "🌈 TikTok彩色",
                    "🌟 TikTok简约",
                    "📖 TikTok故事",
                    "💃 TikTok舞蹈",
                    "💎 TikTok奢华"
                ], {
                    "default": "不使用预设",
                    "tooltip": "选择专门为TikTok优化的预设样式，将自动覆盖其他样式设置"
                }),
                "文本位置": ([
                    "底部居中",          # bottom
                    "底部偏下",          # bottom_low
                    "底部偏上",          # bottom_high
                    "屏幕中央",          # center
                    "中央偏下",          # center_low
                    "中央偏上",          # center_high
                    "顶部居中",          # top
                    "顶部偏下",          # top_low
                    "顶部偏上"           # top_high
                ], {
                    "default": "底部居中",
                    "tooltip": "文本在视频中的垂直位置（水平方向始终居中）"
                }),
                "字体类型": (cls._get_font_options(), {
                    "default": cls._get_default_font(),
                    "tooltip": "字体类型选择（基于系统实际可用字体）"
                }),
                "字体大小": ("INT", {
                    "default": 24,
                    "min": 12,
                    "max": 72,
                    "step": 1,
                    "tooltip": "字体大小（像素）"
                }),
                "字体颜色": ([
                    "黑色",          # black
                    "白色",          # white
                    "红色",          # red
                    "绿色",          # green
                    "蓝色",          # blue
                    "黄色",          # yellow
                    "青色",          # cyan
                    "洋红",          # magenta
                    "橙色",          # orange
                    "紫色",          # purple
                    "灰色",          # gray
                    "深灰"           # darkgray
                ], {
                    "default": "黑色",
                    "tooltip": "字体颜色预设"
                }),
                "背景颜色": ([
                    "白色",          # white
                    "黑色",          # black
                    "透明",          # transparent
                    "红色",          # red
                    "绿色",          # green
                    "蓝色",          # blue
                    "黄色",          # yellow
                    "青色",          # cyan
                    "洋红",          # magenta
                    "橙色",          # orange
                    "紫色",          # purple
                    "灰色",          # gray
                    "浅灰"           # lightgray
                ], {
                    "default": "白色",
                    "tooltip": "背景颜色预设"
                }),
                "背景透明度": ("FLOAT", {
                    "default": 0.8,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.1,
                    "tooltip": "背景透明度（0=完全透明，1=完全不透明）"
                }),
                "每行字符数": ("INT", {
                    "default": 30,
                    "min": 10,
                    "max": 100,
                    "step": 1,
                    "tooltip": "每行最大字符数（超过自动换行）"
                })
            },
            "optional": {
                "启用背景": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "是否启用文字背景"
                }),
                "粗体字": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "是否使用粗体字"
                }),
                "文本对齐": ([
                    "居中",        # center
                    "左对齐",      # left
                    "右对齐"       # right
                ], {
                    "default": "居中",
                    "tooltip": "文本对齐方式"
                }),
                "启用阴影": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "是否启用文字阴影"
                }),
                "启用边框": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "是否启用文字边框"
                }),
                "水平边距": ("INT", {
                    "default": 50,
                    "min": 0,
                    "max": 200,
                    "step": 5,
                    "tooltip": "水平边距（像素）"
                }),
                "行间距": ("INT", {
                    "default": 4,
                    "min": 0,
                    "max": 20,
                    "step": 1,
                    "tooltip": "多行文本的行间距（像素）"
                }),
                "视觉效果": ([
                    "无效果",
                    "🌟 发光效果",
                    "🎯 双重描边",
                    "💫 霓虹效果",
                    "📦 3D立体阴影",
                    "⚡ 故障效果"
                ], {
                    "default": "无效果",
                    "tooltip": "选择高级视觉特效（将覆盖基础边框和阴影设置）"
                })
            }
        }
    
    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("images", "processing_log")
    FUNCTION = "process_text_overlay"
    CATEGORY = "Video/Text"
    OUTPUT_NODE = False
    
    def process_text_overlay(self, images, 文本内容: str, TikTok预设: str, 文本位置: str, 
                           字体类型: str, 字体大小: int, 字体颜色: str, 背景颜色: str,
                           背景透明度: float, 每行字符数: int, 视觉效果: str, **kwargs) -> Tuple[Any, str]:
        """
        处理文本覆盖
        
        Args:
            images: 输入图像序列
            文本内容: 文本内容
            文本位置: 位置
            字体类型: 字体类型
            字体大小: 字体大小
            字体颜色: 字体颜色预设
            背景颜色: 背景颜色预设
            背景透明度: 背景透明度
            每行字符数: 每行最大字符数
            **kwargs: 其他可选参数
            
        Returns:
            (处理后的图像序列, 处理日志)
        """
        # 创建进度记录器
        progress = ProgressLogger("文本覆盖处理")
        
        # 在终端显示开始信息
        print("\n" + "="*60)
        print("🎬 ComfyUI文本覆盖视频节点开始处理")
        print("="*60)
        
        try:
            # 获取可选参数
            enable_background = kwargs.get("启用背景", True)
            font_bold = kwargs.get("粗体字", False)
            text_alignment_cn = kwargs.get("文本对齐", "居中")
            enable_shadow = kwargs.get("启用阴影", False)
            enable_border = kwargs.get("启用边框", False)
            margin_x = kwargs.get("水平边距", 50)
            line_spacing = kwargs.get("行间距", 4)
            
            log_messages = []
            
            # 检查是否使用TikTok预设
            if TikTok预设 != "不使用预设":
                # 使用TikTok预设样式
                progress.log_progress("应用TikTok预设", f"预设样式: {TikTok预设}", 15.0)
                log_messages.append(f"🎯 使用TikTok预设: {TikTok预设}")
                
                tiktok_style = self.get_tiktok_preset_style(TikTok预设)
                if tiktok_style:
                    style = self.convert_subtitle_style_to_overlay_style(tiktok_style)
                    log_messages.append(f"✅ 成功应用{TikTok预设}样式配置")
                    log_messages.append(f"📝 预设参数: 字体大小{tiktok_style.font_size}px, 描边{tiktok_style.outline_width}px")
                else:
                    log_messages.append(f"❌ 未找到预设样式: {TikTok预设}")
                    return images, "\n".join(log_messages)
            else:
                # 使用手动配置的样式
                progress.log_progress("手动配置样式", f"字体: {字体类型}, 大小: {字体大小}px", 15.0)
                log_messages.append(f"🔧 使用手动配置的样式")
                
                # 转换中文选项为内部使用的英文值
                position_en = self.get_position_preset(文本位置)
                font_rgb = self.get_color_rgb(字体颜色)
                background_rgb = self.get_color_rgb(背景颜色)
                text_alignment = self.get_text_alignment(text_alignment_cn)
                
                # 创建样式配置
                style = TextOverlayStyle()
                style.position_preset = position_en
                style.font_family = 字体类型
                style.font_size = 字体大小
                style.font_color = font_rgb
                style.background_color = background_rgb
                style.background_opacity = 背景透明度 if 背景颜色 != "透明" else 0.0
                style.background_enabled = enable_background and 背景颜色 != "透明"
                style.font_bold = font_bold
                style.text_alignment = text_alignment
                style.enable_shadow = enable_shadow
                style.enable_border = enable_border
                style.margin_x = margin_x
                style.line_spacing = line_spacing
                
                log_messages.append(f"位置: {文本位置}, 字体: {字体类型}, 大小: {字体大小}px")
                log_messages.append(f"字体颜色: {字体颜色} {font_rgb}")
                log_messages.append(f"背景颜色: {背景颜色} {background_rgb}")
                log_messages.append(f"背景透明度: {背景透明度}")
            
            # 应用视觉效果
            if 视觉效果 != "无效果":
                self.apply_visual_effect(style, 视觉效果)
                log_messages.append(f"🎨 应用视觉效果: {视觉效果}")
                progress.log_progress("应用视觉效果", f"特效: {视觉效果}", 22.0)
            
            # 处理文本换行
            wrapped_text = self.wrap_text(文本内容, 每行字符数)
            text_stats = self.get_text_stats(wrapped_text)
            
            # 步骤1: 显示配置信息
            progress.log_progress("初始化配置", f"文本: '{文本内容[:20]}{'...' if len(文本内容) > 20 else ''}'", 20.0)
            log_messages.append(f"开始处理文本覆盖: '{文本内容}'")
            log_messages.append(f"换行后文本: {text_stats['total_lines']}行, 最长{text_stats['max_line_length']}字符")
            log_messages.append(f"位置计算: 按视频高度比例自适应")
            
            # 显示位置计算详情（用于调试）
            x_expr, y_expr = style.get_position_expression(1920, 1080)  # 使用标准分辨率计算示例
            log_messages.append(f"位置表达式: x={x_expr}, y={y_expr}")
            
            # 步骤2: 验证样式配置
            progress.log_progress("验证样式配置", f"验证样式有效性", 25.0)
            print(f"🔍 开始验证样式配置...")
            is_valid, error_msg = self.service.validate_style(style)
            if not is_valid:
                error_message = f"❌ 样式配置错误: {error_msg}"
                print(f"❌ 样式验证失败: {error_msg}")
                progress.log_error(error_message)
                log_messages.append(error_message)
                return images, "\n".join(log_messages)
            print(f"✅ 样式配置验证通过")
            
            # 步骤3: 准备临时文件
            progress.log_progress("准备临时文件", "创建输入输出文件", 35.0)
            
            # 由于ComfyUI中图像处理通常在内存中进行，
            # 这里我们需要将图像序列转换为临时视频文件进行处理
            log_messages.append("正在转换图像序列为临时视频...")
            
            # 创建临时文件
            with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_input:
                temp_input_path = temp_input.name
            
            with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_output:
                temp_output_path = temp_output.name
            
            try:
                # 步骤4: 转换图像序列为视频
                print(f"🎬 开始转换图像序列为视频...")
                print(f"📊 输入图像数量: {len(images)}")
                print(f"📁 临时文件路径: {temp_input_path}")
                progress.log_progress("转换图像序列", f"临时文件: {os.path.basename(temp_input_path)}", 45.0)
                success = self._images_to_video(images, temp_input_path)
                if not success:
                    error_message = "❌ 图像序列转换为视频失败"
                    print(f"❌ 图像序列转换失败")
                    progress.log_error(error_message)
                    log_messages.append(error_message)
                    return images, "\n".join(log_messages)
                print(f"✅ 图像序列转换成功")
                
                progress.log_progress("图像序列转换完成", "准备添加文本覆盖", 65.0)
                log_messages.append("✅ 图像序列转换完成")
                
                # 步骤5: 添加文本覆盖
                progress.log_progress("添加文本覆盖", f"使用FFmpeg处理", 75.0)
                log_messages.append("正在添加文本覆盖...")
                success = self.service.add_text_overlay(
                    temp_input_path, wrapped_text, temp_output_path, style
                )
                
                if not success:
                    error_message = "❌ 文本覆盖添加失败"
                    progress.log_error(error_message)
                    log_messages.append(error_message)
                    return images, "\n".join(log_messages)
                
                progress.log_progress("文本覆盖完成", "开始转换回图像序列", 90.0)
                log_messages.append("✅ 文本覆盖添加完成")
                
                # 步骤6: 将处理后的视频转换回图像序列
                progress.log_progress("转换回图像序列", f"输出文件: {os.path.basename(temp_output_path)}", 95.0)
                log_messages.append("正在转换回图像序列...")
                processed_images = self._video_to_images(temp_output_path)
                
                if processed_images is None:
                    error_message = "❌ 视频转换为图像序列失败"
                    progress.log_error(error_message)
                    log_messages.append(error_message)
                    return images, "\n".join(log_messages)
                
                # 步骤7: 完成处理
                progress.log_success("文本覆盖处理完成！")
                log_messages.append("✅ 处理完成！")
                print("="*60)
                return processed_images, "\n".join(log_messages)
                
            finally:
                # 清理临时文件
                try:
                    os.unlink(temp_input_path)
                    os.unlink(temp_output_path)
                except:
                    pass
                
        except Exception as e:
            import traceback
            error_msg = f"❌ 处理过程中发生错误: {str(e)}"
            traceback_str = traceback.format_exc()
            print(f"错误详情:\n{traceback_str}")
            log_messages.append(error_msg)
            log_messages.append(f"错误详情: {traceback_str}")
            return images, "\n".join(log_messages)
    
    def _images_to_video(self, images, output_path: str) -> bool:
        """
        将图像序列转换为视频文件
        
        Args:
            images: 图像序列
            output_path: 输出视频路径
            
        Returns:
            转换是否成功
        """
        try:
            import torch
            import numpy as np
            from PIL import Image
            import subprocess
            import tempfile
            import os
            
            # 创建临时目录保存图像
            temp_dir = tempfile.mkdtemp()
            
            try:
                # 将张量转换为PIL图像并保存
                if isinstance(images, torch.Tensor):
                    # 确保张量在CPU上
                    images = images.cpu()
                    
                    # 转换张量格式 [batch, height, width, channels] -> [batch, channels, height, width]
                    if images.dim() == 4 and images.shape[-1] in [1, 3, 4]:
                        images = images.permute(0, 3, 1, 2)
                    
                    for i, img_tensor in enumerate(images):
                        # 转换为numpy数组
                        img_np = img_tensor.permute(1, 2, 0).numpy()
                        
                        # 确保值在0-255范围内
                        if img_np.max() <= 1.0:
                            img_np = (img_np * 255).astype(np.uint8)
                        else:
                            img_np = np.clip(img_np, 0, 255).astype(np.uint8)
                        
                        # 转换为PIL图像
                        if img_np.shape[2] == 1:
                            pil_img = Image.fromarray(img_np.squeeze(), mode='L')
                        elif img_np.shape[2] == 3:
                            pil_img = Image.fromarray(img_np, mode='RGB')
                        else:
                            pil_img = Image.fromarray(img_np[:,:,:3], mode='RGB')
                        
                        # 保存图像
                        pil_img.save(os.path.join(temp_dir, f"frame_{i:06d}.png"))
                
                # 使用FFmpeg将图像序列转换为视频
                cmd = [
                    'ffmpeg', '-y',
                    '-framerate', '30',  # 默认帧率
                    '-i', os.path.join(temp_dir, 'frame_%06d.png'),
                    '-c:v', 'libx264',
                    '-pix_fmt', 'yuv420p',
                    output_path
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    return True
                else:
                    logging.error(f"FFmpeg转换失败: {result.stderr}")
                    return False
                    
            finally:
                # 清理临时目录
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)
                
        except Exception as e:
            logging.error(f"图像序列转换为视频时发生错误: {e}")
            return False
    
    def _video_to_images(self, video_path: str):
        """
        将视频文件转换为图像序列
        
        Args:
            video_path: 视频文件路径
            
        Returns:
            图像张量或None
        """
        try:
            import torch
            import numpy as np
            from PIL import Image
            import subprocess
            import tempfile
            import os
            import re
            
            # 创建临时目录
            temp_dir = tempfile.mkdtemp()
            
            try:
                # 使用FFmpeg提取帧
                cmd = [
                    'ffmpeg', '-y',
                    '-i', video_path,
                    '-f', 'image2',
                    os.path.join(temp_dir, 'frame_%06d.png')
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode != 0:
                    logging.error(f"FFmpeg提取帧失败: {result.stderr}")
                    return None
                
                # 读取提取的图像
                frame_files = sorted([f for f in os.listdir(temp_dir) if f.endswith('.png')])
                
                if not frame_files:
                    logging.error("未找到提取的帧")
                    return None
                
                images = []
                for frame_file in frame_files:
                    frame_path = os.path.join(temp_dir, frame_file)
                    pil_img = Image.open(frame_path).convert('RGB')
                    
                    # 转换为numpy数组
                    img_np = np.array(pil_img).astype(np.float32) / 255.0
                    
                    # 转换为张量
                    img_tensor = torch.from_numpy(img_np)
                    images.append(img_tensor)
                
                # 堆叠为批次张量
                if images:
                    return torch.stack(images)
                else:
                    return None
                    
            finally:
                # 清理临时目录
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)
                
        except Exception as e:
            logging.error(f"视频转换为图像序列时发生错误: {e}")
            return None


# ComfyUI节点注册
NODE_CLASS_MAPPINGS = {
    "TextOverlayVideoNode": TextOverlayVideoNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "TextOverlayVideoNode": "📝 Text Overlay Video"
}

# 如果直接运行此文件，进行测试
if __name__ == "__main__":
    # 简单测试
    node = TextOverlayVideoNode()
    print("✅ TextOverlayVideoNode 节点创建成功")
    print("📋 节点输入类型:", node.INPUT_TYPES())
