"""
字幕样式配置
定义字幕的位置、字体、颜色、阴影等样式选项
"""

from dataclasses import dataclass
from typing import Tuple, Optional
from enum import Enum


class SubtitlePosition(Enum):
    """字幕位置枚举"""
    BOTTOM_CENTER = "bottom_center"      # 底部居中（默认）
    BOTTOM_LEFT = "bottom_left"          # 底部左对齐
    BOTTOM_RIGHT = "bottom_right"        # 底部右对齐
    BOTTOM_10 = "bottom_10"              # 底部10%位置
    BOTTOM_20 = "bottom_20"              # 底部20%位置
    BOTTOM_30 = "bottom_30"              # 底部30%位置
    TOP_CENTER = "top_center"            # 顶部居中
    TOP_LEFT = "top_left"                # 顶部左对齐
    TOP_RIGHT = "top_right"              # 顶部右对齐
    TOP_10 = "top_10"                    # 顶部10%位置
    TOP_20 = "top_20"                    # 顶部20%位置
    CENTER = "center"                    # 屏幕中央
    CENTER_70 = "center_70"              # 中下70%位置
    CENTER_30 = "center_30"              # 中上30%位置
    CUSTOM = "custom"                    # 自定义位置


class FontWeight(Enum):
    """字体粗细枚举"""
    NORMAL = "normal"
    BOLD = "bold"


@dataclass
class SubtitleStyle:
    """字幕样式配置类"""
    
    # 位置配置
    position: SubtitlePosition = SubtitlePosition.BOTTOM_CENTER
    margin_x: int = 50                   # 左右边距（像素）
    margin_y: int = 50                   # 上下边距（像素）
    custom_x: Optional[int] = None       # 自定义X坐标（仅当position为CUSTOM时使用）
    custom_y: Optional[int] = None       # 自定义Y坐标（仅当position为CUSTOM时使用）
    
    # 字体配置
    font_family: str = "Arial"           # 字体名称
    font_size: int = 24                  # 字体大小
    font_weight: FontWeight = FontWeight.BOLD  # 字体粗细
    
    # 颜色配置（RGB格式）
    font_color: Tuple[int, int, int] = (255, 255, 255)     # 字体颜色（白色）
    outline_color: Tuple[int, int, int] = (0, 0, 0)        # 描边颜色（黑色）
    outline_width: int = 2               # 描边宽度
    
    # 阴影配置
    shadow_enabled: bool = True          # 是否启用阴影
    shadow_color: Tuple[int, int, int] = (0, 0, 0)         # 阴影颜色（黑色）
    shadow_offset_x: int = 2             # 阴影X偏移
    shadow_offset_y: int = 2             # 阴影Y偏移
    shadow_blur: int = 3                 # 阴影模糊度
    
    # 背景配置
    background_enabled: bool = False     # 是否启用背景
    background_color: Tuple[int, int, int, int] = (0, 0, 0, 128)  # 背景颜色（RGBA，半透明黑色）
    background_padding: int = 10         # 背景内边距
    background_margin_h: int = 0         # 背景水平边距
    background_margin_v: int = 0         # 背景垂直边距
    background_radius: int = 0           # 背景圆角半径（ASS不直接支持，但可以通过技巧实现）
    background_full_width: bool = False  # 是否使用全宽背景
    
    # 其他配置
    line_spacing: float = 1.2            # 行间距倍数
    max_width_percent: int = 80          # 最大宽度百分比（相对于视频宽度）
    
    def get_position_filter(self, video_width: int, video_height: int) -> str:
        """
        根据配置生成FFmpeg字幕位置过滤器参数
        
        Args:
            video_width: 视频宽度
            video_height: 视频高度
            
        Returns:
            FFmpeg位置参数字符串
        """
        if self.position == SubtitlePosition.BOTTOM_CENTER:
            x = f"(w-text_w)/2"
            y = f"h-text_h-{self.margin_y}"
        elif self.position == SubtitlePosition.BOTTOM_LEFT:
            x = str(self.margin_x)
            y = f"h-text_h-{self.margin_y}"
        elif self.position == SubtitlePosition.BOTTOM_RIGHT:
            x = f"w-text_w-{self.margin_x}"
            y = f"h-text_h-{self.margin_y}"
        elif self.position == SubtitlePosition.BOTTOM_10:
            x = f"(w-text_w)/2"
            y = f"h*0.9-text_h"
        elif self.position == SubtitlePosition.BOTTOM_20:
            x = f"(w-text_w)/2"
            y = f"h*0.8-text_h"
        elif self.position == SubtitlePosition.BOTTOM_30:
            x = f"(w-text_w)/2"
            y = f"h*0.7-text_h"
        elif self.position == SubtitlePosition.TOP_CENTER:
            x = f"(w-text_w)/2"
            y = str(self.margin_y)
        elif self.position == SubtitlePosition.TOP_LEFT:
            x = str(self.margin_x)
            y = str(self.margin_y)
        elif self.position == SubtitlePosition.TOP_RIGHT:
            x = f"w-text_w-{self.margin_x}"
            y = str(self.margin_y)
        elif self.position == SubtitlePosition.TOP_10:
            x = f"(w-text_w)/2"
            y = f"h*0.1"
        elif self.position == SubtitlePosition.TOP_20:
            x = f"(w-text_w)/2"
            y = f"h*0.2"
        elif self.position == SubtitlePosition.CENTER:
            x = f"(w-text_w)/2"
            y = f"(h-text_h)/2"
        elif self.position == SubtitlePosition.CENTER_70:
            x = f"(w-text_w)/2"
            y = f"h*0.7-text_h"
        elif self.position == SubtitlePosition.CENTER_30:
            x = f"(w-text_w)/2"
            y = f"h*0.3"
        elif self.position == SubtitlePosition.CUSTOM:
            x = str(self.custom_x or 0)
            y = str(self.custom_y or 0)
        else:
            # 默认底部居中
            x = f"(w-text_w)/2"
            y = f"h-text_h-{self.margin_y}"
            
        return f"x={x}:y={y}"
    
    def get_style_params(self) -> str:
        """
        生成FFmpeg字幕样式参数
        
        Returns:
            样式参数字符串
        """
        params = []
        
        # 字体配置
        params.append(f"FontName={self.font_family}")
        params.append(f"FontSize={self.font_size}")
        
        # 颜色配置
        font_color_hex = f"&H{self.font_color[2]:02x}{self.font_color[1]:02x}{self.font_color[0]:02x}"
        params.append(f"PrimaryColour={font_color_hex}")
        
        # 描边配置
        outline_color_hex = f"&H{self.outline_color[2]:02x}{self.outline_color[1]:02x}{self.outline_color[0]:02x}"
        params.append(f"OutlineColour={outline_color_hex}")
        params.append(f"Outline={self.outline_width}")
        
        # 阴影配置
        if self.shadow_enabled:
            shadow_color_hex = f"&H{self.shadow_color[2]:02x}{self.shadow_color[1]:02x}{self.shadow_color[0]:02x}"
            params.append(f"BackColour={shadow_color_hex}")
            params.append(f"Shadow={max(abs(self.shadow_offset_x), abs(self.shadow_offset_y))}")
        else:
            params.append("Shadow=0")
        
        # 字体粗细
        if self.font_weight == FontWeight.BOLD:
            params.append("Bold=1")
        else:
            params.append("Bold=0")
        
        return ":".join(params)
    
    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            'position': self.position.value,
            'margin_x': self.margin_x,
            'margin_y': self.margin_y,
            'custom_x': self.custom_x,
            'custom_y': self.custom_y,
            'font_family': self.font_family,
            'font_size': self.font_size,
            'font_weight': self.font_weight.value,
            'font_color': self.font_color,
            'outline_color': self.outline_color,
            'outline_width': self.outline_width,
            'shadow_enabled': self.shadow_enabled,
            'shadow_color': self.shadow_color,
            'shadow_offset_x': self.shadow_offset_x,
            'shadow_offset_y': self.shadow_offset_y,
            'shadow_blur': self.shadow_blur,
            'background_enabled': self.background_enabled,
            'background_color': self.background_color,
            'background_padding': self.background_padding,
            'line_spacing': self.line_spacing,
            'max_width_percent': self.max_width_percent
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'SubtitleStyle':
        """从字典创建样式对象"""
        style = cls()
        
        if 'position' in data:
            style.position = SubtitlePosition(data['position'])
        if 'margin_x' in data:
            style.margin_x = data['margin_x']
        if 'margin_y' in data:
            style.margin_y = data['margin_y']
        if 'custom_x' in data:
            style.custom_x = data['custom_x']
        if 'custom_y' in data:
            style.custom_y = data['custom_y']
        if 'font_family' in data:
            style.font_family = data['font_family']
        if 'font_size' in data:
            style.font_size = data['font_size']
        if 'font_weight' in data:
            style.font_weight = FontWeight(data['font_weight'])
        if 'font_color' in data:
            style.font_color = tuple(data['font_color'])
        if 'outline_color' in data:
            style.outline_color = tuple(data['outline_color'])
        if 'outline_width' in data:
            style.outline_width = data['outline_width']
        if 'shadow_enabled' in data:
            style.shadow_enabled = data['shadow_enabled']
        if 'shadow_color' in data:
            style.shadow_color = tuple(data['shadow_color'])
        if 'shadow_offset_x' in data:
            style.shadow_offset_x = data['shadow_offset_x']
        if 'shadow_offset_y' in data:
            style.shadow_offset_y = data['shadow_offset_y']
        if 'shadow_blur' in data:
            style.shadow_blur = data['shadow_blur']
        if 'background_enabled' in data:
            style.background_enabled = data['background_enabled']
        if 'background_color' in data:
            style.background_color = tuple(data['background_color'])
        if 'background_padding' in data:
            style.background_padding = data['background_padding']
        if 'line_spacing' in data:
            style.line_spacing = data['line_spacing']
        if 'max_width_percent' in data:
            style.max_width_percent = data['max_width_percent']
            
        return style


# 预设颜色定义
class PresetColors:
    """预设颜色系统"""
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    YELLOW = (255, 255, 0)
    CYAN = (0, 255, 255)
    MAGENTA = (255, 0, 255)
    ORANGE = (255, 165, 0)
    PURPLE = (128, 0, 128)
    PINK = (255, 192, 203)
    GRAY = (128, 128, 128)
    LIGHT_GRAY = (192, 192, 192)
    DARK_GRAY = (64, 64, 64)
    GOLD = (255, 215, 0)
    SILVER = (192, 192, 192)
    BROWN = (139, 69, 19)
    LIGHT_BLUE = (173, 216, 230)
    DARK_BLUE = (0, 0, 139)
    LIGHT_GREEN = (144, 238, 144)
    DARK_GREEN = (0, 100, 0)
    BEIGE = (245, 245, 220)
    CORAL = (255, 127, 80)
    SKY_BLUE = (135, 206, 235)


# 预定义样式
class PresetStyles:
    """预定义字幕样式"""
    
    @staticmethod
    def default() -> SubtitleStyle:
        """默认样式：底部居中，白字黑边，带阴影"""
        return SubtitleStyle()
    
    @staticmethod
    def cinema() -> SubtitleStyle:
        """电影院样式：底部居中，大字体，强阴影"""
        return SubtitleStyle(
            font_size=28,
            margin_y=60,
            shadow_enabled=True,
            shadow_offset_x=4,
            shadow_offset_y=4,
            shadow_blur=6,
            outline_width=2,
            font_weight=FontWeight.BOLD
        )
    
    @staticmethod
    def youtube() -> SubtitleStyle:
        """YouTube样式:底部居中,黄色背景"""
        return SubtitleStyle(
            font_size=20,
            background_enabled=True,
            background_color=(255, 255, 0, 180),  # 半透明黄色
            background_padding=8,
            outline_width=1
        )
    
    @staticmethod
    def minimal() -> SubtitleStyle:
        """极简样式：底部居中，无阴影，细描边"""
        return SubtitleStyle(
            font_size=22,
            shadow_enabled=False,
            outline_width=1,
            font_weight=FontWeight.NORMAL
        )
    
    @staticmethod
    def top_news() -> SubtitleStyle:
        """新闻样式：顶部居中，带背景"""
        return SubtitleStyle(
            position=SubtitlePosition.TOP_CENTER,
            font_size=20,
            background_enabled=True,
            background_color=(0, 0, 0, 200),  # 半透明黑色
            background_padding=12,
            margin_y=30
        )
    
    @staticmethod
    def strong_shadow() -> SubtitleStyle:
        """强阴影样式：类似图片效果，文字后面有明显阴影"""
        return SubtitleStyle(
            font_size=32,
            font_weight=FontWeight.BOLD,
            margin_y=50,
            # 强阴影配置
            shadow_enabled=True,
            shadow_color=(0, 0, 0),  # 纯黑色阴影
            shadow_offset_x=6,       # 更大的X偏移
            shadow_offset_y=6,       # 更大的Y偏移
            shadow_blur=8,           # 更强的模糊
            # 描边配置
            outline_width=3,
            outline_color=(0, 0, 0), # 黑色描边
            # 字体颜色保持白色以形成对比
            font_color=(255, 255, 255)
        )
    
    @staticmethod
    def dramatic_shadow() -> SubtitleStyle:
        """戏剧化阴影样式：超强阴影效果"""
        return SubtitleStyle(
            font_size=36,
            font_weight=FontWeight.BOLD,
            margin_y=60,
            # 超强阴影配置
            shadow_enabled=True,
            shadow_color=(0, 0, 0),  # 纯黑色阴影
            shadow_offset_x=8,       # 超大X偏移
            shadow_offset_y=8,       # 超大Y偏移
            shadow_blur=12,          # 超强模糊
            # 粗描边
            outline_width=4,
            outline_color=(0, 0, 0),
            # 白色字体
            font_color=(255, 255, 255)
        )
    
    @staticmethod
    def background_black() -> SubtitleStyle:
        """黑色背景样式：类似原始节点的黑底白字效果"""
        return SubtitleStyle(
            position=SubtitlePosition.BOTTOM_10,
            font_size=28,
            font_weight=FontWeight.BOLD,
            font_color=PresetColors.WHITE,
            background_enabled=True,
            background_color=(0, 0, 0, 200),  # 半透明黑色背景
            background_padding=15,
            outline_width=0,  # 有背景时不需要描边
            shadow_enabled=False,  # 有背景时不需要阴影
            margin_y=50
        )
    
    @staticmethod
    def background_blur() -> SubtitleStyle:
        """模糊背景样式：带半透明模糊背景的字幕"""
        return SubtitleStyle(
            position=SubtitlePosition.BOTTOM_CENTER,
            font_size=26,
            font_color=PresetColors.WHITE,
            background_enabled=True,
            background_color=(20, 20, 20, 180),  # 深灰半透明背景
            background_padding=20,
            background_margin_h=10,
            outline_width=1,
            outline_color=PresetColors.DARK_GRAY,
            shadow_enabled=False
        )
    
    @staticmethod
    def colorful_background() -> SubtitleStyle:
        """彩色背景样式：适合综艺节目"""
        return SubtitleStyle(
            position=SubtitlePosition.BOTTOM_20,
            font_size=32,
            font_weight=FontWeight.BOLD,
            font_color=PresetColors.WHITE,
            background_enabled=True,
            background_color=(255, 69, 0, 200),  # 橙红色背景
            background_padding=18,
            outline_width=2,
            outline_color=PresetColors.DARK_GRAY,
            shadow_enabled=True,
            shadow_offset_x=3,
            shadow_offset_y=3
        )
    
    @staticmethod
    def elegant() -> SubtitleStyle:
        """优雅样式：适合纪录片或正式内容"""
        return SubtitleStyle(
            position=SubtitlePosition.BOTTOM_CENTER,
            font_size=24,
            font_weight=FontWeight.NORMAL,
            font_color=PresetColors.BEIGE,
            outline_width=1,
            outline_color=PresetColors.DARK_GRAY,
            shadow_enabled=True,
            shadow_color=PresetColors.BLACK,
            shadow_offset_x=2,
            shadow_offset_y=2,
            margin_y=45
        )
    
    @staticmethod
    def gaming() -> SubtitleStyle:
        """游戏风格：醒目的游戏字幕效果"""
        return SubtitleStyle(
            position=SubtitlePosition.BOTTOM_10,
            font_size=30,
            font_weight=FontWeight.BOLD,
            font_color=PresetColors.YELLOW,
            outline_width=3,
            outline_color=PresetColors.BLACK,
            shadow_enabled=True,
            shadow_color=PresetColors.DARK_GRAY,
            shadow_offset_x=4,
            shadow_offset_y=4,
            shadow_blur=5
        )