"""
文本覆盖服务
为视频添加自定义文本覆盖功能
"""

import os
import logging
import subprocess
from typing import Optional, Tuple, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class TextAlignment:
    """文本对齐方式"""
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"


class TextOverlayStyle:
    """文本覆盖样式配置"""
    
    def __init__(self):
        # 位置配置
        self.position_preset = "bottom_center"  # 预设位置
        self.margin_x = 50                      # 边距X
        self.margin_y = 50                      # 边距Y
        
        # 字体配置
        self.font_family = "Arial"              # 字体族
        self.font_size = 24                     # 字体大小
        self.font_color = (0, 0, 0)            # 字体颜色 RGB (默认黑色)
        self.font_bold = False                  # 是否粗体
        
        # 背景配置
        self.background_enabled = True          # 是否启用背景
        self.background_color = (255, 255, 255) # 背景颜色 RGB (默认白色)
        self.background_opacity = 0.8           # 背景透明度 (0-1)
        self.background_padding = 10            # 背景内边距
        self.background_radius = 8              # 背景圆角半径
        
        # 文本效果
        self.text_alignment = TextAlignment.CENTER  # 文字对齐
        self.enable_shadow = False              # 是否启用阴影
        self.shadow_color = (128, 128, 128)    # 阴影颜色
        self.shadow_offset_x = 2                # 阴影X偏移
        self.shadow_offset_y = 2                # 阴影Y偏移
        
        # 边框配置
        self.enable_border = False              # 是否启用边框
        self.border_color = (0, 0, 0)          # 边框颜色
        self.border_width = 1                   # 边框宽度
        
        # 时间配置 - 默认覆盖整个视频
        self.start_time = 0.0                   # 开始时间(秒) 
        self.end_time = None                    # 结束时间(秒), None表示到视频结束
    
    def get_position_expression(self, video_width: int, video_height: int) -> Tuple[str, str]:
        """
        根据位置配置生成FFmpeg位置表达式
        
        Args:
            video_width: 视频宽度
            video_height: 视频高度
            
        Returns:
            (x_expression, y_expression)
        """
        # 水平方向始终居中
        x = f"(w-text_w)/2"
        
        # 根据垂直位置计算Y坐标
        if self.position_preset == "bottom":
            y = f"h-text_h-{self.margin_y}"
        elif self.position_preset == "bottom_low":
            y = f"h-text_h-{self.margin_y//2}"  # 更靠近底部
        elif self.position_preset == "bottom_high":
            y = f"h-text_h-{self.margin_y*2}"  # 离底部更远
        elif self.position_preset == "center":
            y = f"(h-text_h)/2"
        elif self.position_preset == "center_low":
            y = f"(h-text_h)/2+{self.margin_y}"  # 中央偏下
        elif self.position_preset == "center_high":
            y = f"(h-text_h)/2-{self.margin_y}"  # 中央偏上
        elif self.position_preset == "top":
            y = str(self.margin_y)
        elif self.position_preset == "top_low":
            y = str(self.margin_y*2)  # 距离顶部更远
        elif self.position_preset == "top_high":
            y = str(self.margin_y//2)  # 更靠近顶部
        else:
            # 默认底部居中
            y = f"h-text_h-{self.margin_y}"
        
        return x, y


class TextOverlayService:
    """文本覆盖服务类"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def add_text_overlay(self, 
                        video_path: str,
                        text_content: str,
                        output_path: str,
                        style: TextOverlayStyle) -> bool:
        """
        为视频添加文本覆盖
        
        Args:
            video_path: 输入视频路径
            text_content: 要覆盖的文本内容
            output_path: 输出视频路径
            style: 文本样式配置
            
        Returns:
            处理是否成功
        """
        try:
            # 验证输入文件
            if not os.path.exists(video_path):
                self.logger.error(f"视频文件不存在: {video_path}")
                return False
            
            # 获取视频信息
            video_info = self._get_video_info(video_path)
            if not video_info:
                self.logger.error("无法获取视频信息")
                return False
            
            video_width = video_info['width']
            video_height = video_info['height']
            video_duration = video_info['duration']
            
            # 构建FFmpeg命令
            cmd = self._build_ffmpeg_command(
                video_path, text_content, output_path, 
                style, video_width, video_height, video_duration
            )
            
            self.logger.info(f"开始添加文本覆盖: {text_content}")
            self.logger.debug(f"FFmpeg命令: {' '.join(cmd)}")
            
            # 执行FFmpeg命令
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
            
            if result.returncode == 0:
                self.logger.info(f"文本覆盖添加成功: {output_path}")
                return True
            else:
                self.logger.error(f"FFmpeg执行失败: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"添加文本覆盖时发生错误: {e}")
            return False
    
    def _get_video_info(self, video_path: str) -> Optional[Dict[str, Any]]:
        """
        获取视频基本信息
        
        Args:
            video_path: 视频文件路径
            
        Returns:
            视频信息字典或None
        """
        try:
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                '-show_streams',
                video_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                self.logger.error(f"ffprobe执行失败: {result.stderr}")
                return None
            
            import json
            data = json.loads(result.stdout)
            
            # 查找视频流
            video_stream = None
            for stream in data['streams']:
                if stream['codec_type'] == 'video':
                    video_stream = stream
                    break
            
            if not video_stream:
                self.logger.error("未找到视频流")
                return None
            
            return {
                'width': int(video_stream['width']),
                'height': int(video_stream['height']),
                'duration': float(data['format']['duration'])
            }
            
        except Exception as e:
            self.logger.error(f"获取视频信息时发生错误: {e}")
            return None
    
    def _build_ffmpeg_command(self, 
                             video_path: str,
                             text_content: str,
                             output_path: str,
                             style: TextOverlayStyle,
                             video_width: int,
                             video_height: int,
                             video_duration: float) -> list:
        """
        构建FFmpeg命令
        
        Args:
            video_path: 输入视频路径
            text_content: 文本内容
            output_path: 输出路径
            style: 样式配置
            video_width: 视频宽度
            video_height: 视频高度
            video_duration: 视频时长
            
        Returns:
            FFmpeg命令列表
        """
        cmd = ['ffmpeg', '-i', video_path]
        
        # 构建drawtext过滤器
        filter_parts = []
        
        # 基本文本配置
        # 转义文本中的特殊字符
        escaped_text = text_content.replace(':', '\\:').replace("'", "\\'")
        filter_parts.append(f"text='{escaped_text}'")
        
        # 字体配置
        filter_parts.append(f"fontfile={self._get_font_path(style.font_family)}")
        filter_parts.append(f"fontsize={style.font_size}")
        
        # 字体颜色
        font_color_hex = f"0x{style.font_color[0]:02x}{style.font_color[1]:02x}{style.font_color[2]:02x}"
        filter_parts.append(f"fontcolor={font_color_hex}")
        
        # 位置配置
        x_expr, y_expr = style.get_position_expression(video_width, video_height)
        filter_parts.append(f"x={x_expr}")
        filter_parts.append(f"y={y_expr}")
        
        # 背景配置
        if style.background_enabled:
            # 计算背景颜色和透明度
            bg_alpha = int(style.background_opacity * 255)
            bg_color = f"0x{style.background_color[0]:02x}{style.background_color[1]:02x}{style.background_color[2]:02x}{bg_alpha:02x}"
            filter_parts.append(f"box=1")
            filter_parts.append(f"boxcolor={bg_color}")
            filter_parts.append(f"boxborderw={style.background_padding}")
            
            # 圆角效果（FFmpeg的drawtext过滤器本身不支持圆角）
            # 这里暂时跳过圆角处理，后续可通过复合过滤器实现
            if style.background_radius > 0:
                # 暂时不添加圆角相关的FFmpeg参数
                # 实际的圆角效果需要在后续版本中通过复合过滤器实现
                pass
        
        # 边框配置
        if style.enable_border:
            border_color_hex = f"0x{style.border_color[0]:02x}{style.border_color[1]:02x}{style.border_color[2]:02x}"
            filter_parts.append(f"borderw={style.border_width}")
            filter_parts.append(f"bordercolor={border_color_hex}")
        
        # 阴影配置
        if style.enable_shadow:
            shadow_color_hex = f"0x{style.shadow_color[0]:02x}{style.shadow_color[1]:02x}{style.shadow_color[2]:02x}"
            filter_parts.append(f"shadowcolor={shadow_color_hex}")
            filter_parts.append(f"shadowx={style.shadow_offset_x}")
            filter_parts.append(f"shadowy={style.shadow_offset_y}")
        
        # 时间配置
        end_time = style.end_time if style.end_time is not None else video_duration
        if style.start_time > 0 or end_time < video_duration:
            filter_parts.append(f"enable='between(t,{style.start_time},{end_time})'")
        
        # 组合过滤器
        drawtext_filter = "drawtext=" + ":".join(filter_parts)
        
        cmd.extend(['-vf', drawtext_filter])
        cmd.extend(['-c:a', 'copy'])  # 音频直接复制
        cmd.extend(['-y', output_path])  # 覆盖输出文件
        
        return cmd
    
    def _get_font_path(self, font_family: str) -> str:
        """
        获取字体文件路径
        
        Args:
            font_family: 字体族名称
            
        Returns:
            字体文件路径
        """
        # 常见系统字体路径
        font_paths = {
            "Arial": "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "Times": "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
            "Courier": "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
        }
        
        # 首先尝试系统字体
        if font_family in font_paths and os.path.exists(font_paths[font_family]):
            return font_paths[font_family]
        
        # 尝试查找中文字体
        chinese_fonts = [
            "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
            "/usr/share/fonts/truetype/arphic/uming.ttc",
            "/System/Library/Fonts/PingFang.ttc",  # macOS
            "/Windows/Fonts/simhei.ttf",  # Windows
        ]
        
        for font_path in chinese_fonts:
            if os.path.exists(font_path):
                return font_path
        
        # 默认使用Arial
        return font_paths.get("Arial", "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf")
    
    def validate_style(self, style: TextOverlayStyle) -> Tuple[bool, str]:
        """
        验证样式配置
        
        Args:
            style: 样式配置
            
        Returns:
            (是否有效, 错误信息)
        """
        # 验证时间配置
        if style.start_time < 0:
            return False, "开始时间不能为负数"
        
        if style.end_time is not None and style.end_time <= style.start_time:
            return False, "结束时间必须大于开始时间"
        
        # 验证颜色配置
        for color_name, color in [
            ("字体颜色", style.font_color),
            ("背景颜色", style.background_color),
            ("阴影颜色", style.shadow_color),
            ("边框颜色", style.border_color)
        ]:
            if not isinstance(color, tuple) or len(color) != 3:
                return False, f"{color_name}必须是包含3个元素的元组"
            
            for i, c in enumerate(color):
                if not isinstance(c, int) or c < 0 or c > 255:
                    return False, f"{color_name}的第{i+1}个分量必须是0-255之间的整数"
        
        # 验证透明度
        if not 0 <= style.background_opacity <= 1:
            return False, "背景透明度必须在0-1之间"
        
        # 验证字体大小
        if style.font_size <= 0:
            return False, "字体大小必须大于0"
        
        return True, ""
