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
    TOP_CENTER = "top_center"            # 顶部居中
    TOP_LEFT = "top_left"                # 顶部左对齐
    TOP_RIGHT = "top_right"              # 顶部右对齐
    CENTER = "center"                    # 屏幕中央
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
    margin_x: int = 120                  # 左右边距（像素）
    margin_y: int = 50                   # 上下边距（像素）- 减小数值让字幕更靠近底部
    custom_x: Optional[int] = None       # 自定义X坐标（仅当position为CUSTOM时使用）
    custom_y: Optional[int] = None       # 自定义Y坐标（仅当position为CUSTOM时使用）
    
    # 字体配置
    font_family: str = "Noto Sans CJK SC,WenQuanYi Zen Hei,Arial"  # 字体名称（支持中文）
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
        elif self.position == SubtitlePosition.TOP_CENTER:
            x = f"(w-text_w)/2"
            y = str(self.margin_y)
        elif self.position == SubtitlePosition.TOP_LEFT:
            x = str(self.margin_x)
            y = str(self.margin_y)
        elif self.position == SubtitlePosition.TOP_RIGHT:
            x = f"w-text_w-{self.margin_x}"
            y = str(self.margin_y)
        elif self.position == SubtitlePosition.CENTER:
            x = f"(w-text_w)/2"
            y = f"(h-text_h)/2"
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
            margin_x=100,
            margin_y=40,  # 减小数值让字幕更靠近底部
            shadow_enabled=True,
            shadow_offset_x=4,
            shadow_offset_y=4,
            shadow_blur=6,
            outline_width=2,
            font_weight=FontWeight.BOLD,
            max_width_percent=75  # 限制最大宽度
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
            margin_x=120,
            margin_y=30,  # 减小数值让字幕更靠近底部
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
            font_color=(255, 255, 255),
            max_width_percent=70     # 限制最大宽度
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
    
    # ======= TikTok 专用预设样式 =======
    
    @staticmethod
    def tiktok_classic() -> SubtitleStyle:
        """🔥 TikTok经典：大字体白字粗黑边，中下位置显示"""
        return SubtitleStyle(
            # 位置：中下位置，适合竖屏观看
            position=SubtitlePosition.BOTTOM_CENTER,
            margin_y=25,  # 距离底部适中距离，避开TikTok UI
            margin_x=30,  # 减少边距以适配手机屏幕
            
            # 字体：大字体粗体，突出显示
            font_size=42,
            font_weight=FontWeight.BOLD,
            font_family="Arial Black,WenQuanYi Zen Hei",
            
            # 颜色：纯白字体配黑边，经典TikTok风格
            font_color=(255, 255, 255),
            outline_width=4,  # 粗描边确保可读性
            outline_color=(0, 0, 0),
            
            # 阴影：增强立体感
            shadow_enabled=True,
            shadow_offset_x=3,
            shadow_offset_y=3,
            shadow_blur=5,
            shadow_color=(0, 0, 0),
            
            # 背景：不使用背景，保持简洁
            background_enabled=False,
            
            # 布局：适配手机屏幕
            max_width_percent=85,
            line_spacing=1.3
        )
    
    @staticmethod
    def tiktok_neon() -> SubtitleStyle:
        """✨ TikTok霓虹：发光效果，时尚炫酷"""
        return SubtitleStyle(
            # 位置：居中稍下，突出显示
            position=SubtitlePosition.CENTER,
            margin_y=40,
            margin_x=25,
            
            # 字体：中大字体，现代感
            font_size=38,
            font_weight=FontWeight.BOLD,
            font_family="Arial,Roboto,WenQuanYi Zen Hei",
            
            # 颜色：白色字体配霓虹边框
            font_color=(255, 255, 255),
            outline_width=3,
            outline_color=(255, 20, 147),  # 霓虹粉边框
            
            # 特殊效果：多层阴影模拟发光
            shadow_enabled=True,
            shadow_offset_x=0,
            shadow_offset_y=0,
            shadow_blur=10,
            shadow_color=(255, 20, 147),  # 霓虹粉发光
            
            # 背景：半透明深色背景增强发光效果
            background_enabled=True,
            background_color=(20, 20, 40, 120),
            background_padding=15,
            
            # 布局
            max_width_percent=80,
            line_spacing=1.2
        )
    
    @staticmethod 
    def tiktok_bold() -> SubtitleStyle:
        """💪 TikTok粗体：超粗字体，震撼视觉"""
        return SubtitleStyle(
            # 位置：底部，霸气显示
            position=SubtitlePosition.BOTTOM_CENTER,
            margin_y=30,
            margin_x=20,
            
            # 字体：超大粗体
            font_size=48,
            font_weight=FontWeight.BOLD,
            font_family="Impact,Arial Black,WenQuanYi Zen Hei Bold",
            
            # 颜色：纯白配超粗黑边
            font_color=(255, 255, 255),
            outline_width=6,  # 超粗描边
            outline_color=(0, 0, 0),
            
            # 阴影：强化立体感
            shadow_enabled=True,
            shadow_offset_x=4,
            shadow_offset_y=4,
            shadow_blur=8,
            shadow_color=(0, 0, 0),
            
            # 布局：紧凑显示
            max_width_percent=90,
            line_spacing=1.1
        )
    
    @staticmethod
    def tiktok_colorful() -> SubtitleStyle:
        """🌈 TikTok彩色：彩虹色彩，活力四射"""
        return SubtitleStyle(
            # 位置：中上位置
            position=SubtitlePosition.CENTER,
            margin_y=35,
            margin_x=30,
            
            # 字体：活泼字体
            font_size=40,
            font_weight=FontWeight.BOLD,
            font_family="Arial Rounded,Arial,WenQuanYi Zen Hei",
            
            # 颜色：彩虹色字体（这里用黄色代表，实际需要渐变支持）
            font_color=(255, 215, 0),  # 金黄色
            outline_width=3,
            outline_color=(255, 69, 0),  # 橙红色边框
            
            # 阴影：彩色阴影
            shadow_enabled=True,
            shadow_offset_x=2,
            shadow_offset_y=2,
            shadow_blur=6,
            shadow_color=(255, 105, 180),  # 粉色阴影
            
            # 背景：渐变背景（暂用半透明白色）
            background_enabled=True,
            background_color=(255, 255, 255, 80),
            background_padding=12,
            
            max_width_percent=82
        )
    
    @staticmethod
    def tiktok_minimal() -> SubtitleStyle:
        """🌟 TikTok简约：干净简洁，突出内容"""
        return SubtitleStyle(
            # 位置：底部简洁
            position=SubtitlePosition.BOTTOM_CENTER,
            margin_y=35,
            margin_x=40,
            
            # 字体：简洁现代
            font_size=36,
            font_weight=FontWeight.BOLD,
            font_family="Helvetica,Arial,WenQuanYi Zen Hei",
            
            # 颜色：纯白简洁
            font_color=(255, 255, 255),
            outline_width=2,  # 细描边
            outline_color=(0, 0, 0),
            
            # 阴影：轻微阴影
            shadow_enabled=True,
            shadow_offset_x=1,
            shadow_offset_y=1,
            shadow_blur=3,
            shadow_color=(0, 0, 0),
            
            # 背景：无背景，保持简洁
            background_enabled=False,
            
            max_width_percent=75,
            line_spacing=1.4
        )
    
    @staticmethod
    def tiktok_story() -> SubtitleStyle:
        """📖 TikTok故事：温馨叙述，情感传达"""
        return SubtitleStyle(
            # 位置：中央偏下
            position=SubtitlePosition.CENTER,
            margin_y=25,
            margin_x=35,
            
            # 字体：温暖字体
            font_size=34,
            font_weight=FontWeight.BOLD,
            font_family="Georgia,Times,SimSun,WenQuanYi Zen Hei",
            
            # 颜色：温暖白色
            font_color=(255, 248, 220),  # 象牙白
            outline_width=2,
            outline_color=(139, 69, 19),  # 棕色边框
            
            # 阴影：温和阴影
            shadow_enabled=True,
            shadow_offset_x=2,
            shadow_offset_y=2,
            shadow_blur=4,
            shadow_color=(101, 67, 33),  # 深棕色阴影
            
            # 背景：温馨背景
            background_enabled=True,
            background_color=(139, 69, 19, 100),  # 半透明棕色
            background_padding=14,
            
            max_width_percent=85,
            line_spacing=1.5
        )
    
    @staticmethod
    def tiktok_dance() -> SubtitleStyle:
        """💃 TikTok舞蹈：动感节拍，律动感强"""
        return SubtitleStyle(
            # 位置：顶部，避开舞蹈动作
            position=SubtitlePosition.TOP_CENTER,
            margin_y=25,
            margin_x=25,
            
            # 字体：动感字体
            font_size=44,
            font_weight=FontWeight.BOLD,
            font_family="Impact,Arial Black,WenQuanYi Zen Hei",
            
            # 颜色：活力色彩
            font_color=(255, 255, 255),
            outline_width=5,
            outline_color=(255, 0, 128),  # 亮粉色边框
            
            # 阴影：强烈阴影
            shadow_enabled=True,
            shadow_offset_x=3,
            shadow_offset_y=3,
            shadow_blur=7,
            shadow_color=(255, 0, 128),
            
            # 背景：动感背景
            background_enabled=True,
            background_color=(0, 0, 0, 150),
            background_padding=10,
            
            max_width_percent=80,
            line_spacing=1.2
        )
    
    @staticmethod
    def tiktok_luxury() -> SubtitleStyle:
        """💎 TikTok奢华：金色质感，高端大气"""
        return SubtitleStyle(
            # 位置：居中显示
            position=SubtitlePosition.CENTER,
            margin_y=30,
            margin_x=40,
            
            # 字体：优雅字体
            font_size=38,
            font_weight=FontWeight.BOLD,
            font_family="Times New Roman,Georgia,SimSun",
            
            # 颜色：金色奢华
            font_color=(255, 215, 0),  # 金色
            outline_width=3,
            outline_color=(184, 134, 11),  # 深金色边框
            
            # 阴影：奢华阴影
            shadow_enabled=True,
            shadow_offset_x=2,
            shadow_offset_y=2,
            shadow_blur=8,
            shadow_color=(139, 69, 19),  # 深棕色阴影
            
            # 背景：高端背景
            background_enabled=True,
            background_color=(0, 0, 0, 180),  # 深色背景
            background_padding=16,
            
            max_width_percent=78,
            line_spacing=1.3
        )