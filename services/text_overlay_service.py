"""
文本覆盖服务
为视频添加自定义文本覆盖功能
"""

import os
import logging
import subprocess
from typing import Optional, Tuple, Dict, Any
from pathlib import Path

try:
    from .font_manager import get_font_manager
except ImportError:
    from font_manager import get_font_manager

logger = logging.getLogger(__name__)


class TextAlignment:
    """文本对齐方式"""
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"


class TextEffectType:
    """文本特效类型"""
    NONE = "none"
    GLOW = "glow"               # 发光效果
    DOUBLE_OUTLINE = "double_outline"  # 双重描边
    NEON = "neon"               # 霓虹效果
    SHADOW_3D = "shadow_3d"     # 3D立体阴影
    GLITCH = "glitch"           # 故障效果


class TextOverlayStyle:
    """文本覆盖样式配置"""
    
    def __init__(self):
        # 位置配置
        self.position_preset = "bottom_center"  # 预设位置
        self.margin_x = 50                      # 边距X
        
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
        
        # 文本排版配置
        self.line_spacing = 4                   # 行间距（像素）
        
        # 时间配置 - 默认覆盖整个视频
        self.start_time = 0.0                   # 开始时间(秒) 
        self.end_time = None                    # 结束时间(秒), None表示到视频结束
        
        # ===== 新增高级特效配置 =====
        self.text_effect = TextEffectType.NONE  # 文本特效类型
        
        # 发光效果配置
        self.glow_enabled = False               # 是否启用发光
        self.glow_color = (255, 255, 255)      # 发光颜色
        self.glow_intensity = 8                 # 发光强度 (模糊半径)
        self.glow_spread = 2                    # 发光扩散距离
        
        # 双重描边配置
        self.double_outline_enabled = False     # 是否启用双重描边
        self.outline_inner_width = 2            # 内描边宽度
        self.outline_inner_color = (255, 255, 255)  # 内描边颜色
        self.outline_outer_width = 4            # 外描边宽度  
        self.outline_outer_color = (0, 0, 0)    # 外描边颜色
        
        # 霓虹效果配置
        self.neon_enabled = False               # 是否启用霓虹效果
        self.neon_base_color = (255, 20, 147)  # 霓虹基础颜色
        self.neon_glow_layers = 3               # 发光层数
        self.neon_intensity = 10                # 霓虹强度
        
        # 3D阴影配置
        self.shadow_3d_enabled = False          # 是否启用3D阴影
        self.shadow_3d_layers = 5               # 阴影层数
        self.shadow_3d_depth = 3                # 阴影深度
        self.shadow_3d_angle = 225              # 阴影角度(度)
        
        # 故障效果配置
        self.glitch_enabled = False             # 是否启用故障效果
        self.glitch_displacement = 3            # 故障位移
        self.glitch_color_shift = True          # 颜色偏移
    
    def get_position_expression(self, video_width: int, video_height: int) -> Tuple[str, str]:
        """
        根据位置配置生成FFmpeg位置表达式
        
        Args:
            video_width: 视频宽度
            video_height: 视频高度
            
        Returns:
            (x_expression, y_expression)
        """
        # 水平方向位置计算，考虑水平边距和文本对齐
        if hasattr(self, 'text_alignment'):
            if self.text_alignment == TextAlignment.LEFT:
                # 左对齐
                x = str(self.margin_x) if self.margin_x > 0 else "0"
            elif self.text_alignment == TextAlignment.RIGHT:
                # 右对齐
                x = f"w-text_w-{self.margin_x}" if self.margin_x > 0 else "w-text_w"
            else:
                # 居中对齐 (默认)
                if self.margin_x > 0:
                    x = f"(w-text_w-{self.margin_x*2})/2+{self.margin_x}"
                else:
                    x = f"(w-text_w)/2"
        else:
            # 默认居中对齐
            if self.margin_x > 0:
                x = f"(w-text_w-{self.margin_x*2})/2+{self.margin_x}"
            else:
                x = f"(w-text_w)/2"
        
        # 根据垂直位置计算Y坐标，使用视频高度比例
        if self.position_preset == "bottom":
            y = f"h-text_h-h*0.05"  # 距底部5%高度
        elif self.position_preset == "bottom_low":
            y = f"h-text_h-h*0.03"  # 距底部3%高度（更靠近底部）
        elif self.position_preset == "bottom_high":
            y = f"h-text_h-h*0.08"  # 距底部8%高度（距底部更远）
        elif self.position_preset == "center":
            y = f"(h-text_h)/2"  # 正中央
        elif self.position_preset == "center_low":
            y = f"(h-text_h)/2+h*0.05"  # 中央向下偏移5%高度
        elif self.position_preset == "center_high":
            y = f"(h-text_h)/2-h*0.05"  # 中央向上偏移5%高度
        elif self.position_preset == "top":
            y = f"h*0.08"  # 距顶部8%高度（合适的顶部位置）
        elif self.position_preset == "top_low":
            y = f"h*0.15"  # 距顶部15%高度（顶部偏下）
        elif self.position_preset == "top_high":
            y = f"h*0.03"  # 距顶部3%高度（顶部偏上）
        else:
            # 默认底部居中
            y = f"h-text_h-h*0.05"
        
        return x, y


class TextOverlayService:
    """文本覆盖服务类"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.font_manager = get_font_manager()
    
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
        # 检查是否需要高级特效
        use_advanced_effects = (
            getattr(style, 'glow_enabled', False) or
            getattr(style, 'double_outline_enabled', False) or
            getattr(style, 'neon_enabled', False) or
            getattr(style, 'shadow_3d_enabled', False) or
            getattr(style, 'glitch_enabled', False)
        )
        
        if use_advanced_effects:
            return self._build_advanced_effect_command(
                video_path, text_content, output_path, style, 
                video_width, video_height, video_duration
            )
        else:
            return self._build_basic_command(
                video_path, text_content, output_path, style, 
                video_width, video_height, video_duration
            )
    
    def _build_basic_command(self, 
                            video_path: str,
                            text_content: str,
                            output_path: str,
                            style: TextOverlayStyle,
                            video_width: int,
                            video_height: int,
                            video_duration: float) -> list:
        """构建基础FFmpeg命令"""
        cmd = ['ffmpeg', '-i', video_path]
        
        # 构建drawtext过滤器
        filter_parts = []
        
        # 基本文本配置
        # 转义文本中的特殊字符，但保留换行符供FFmpeg识别
        escaped_text = text_content.replace(':', '\\:').replace("'", "\\'")
        filter_parts.append(f"text='{escaped_text}'")
        
        # 字体配置 - 使用新的字体管理器
        # 如果字体名称包含语种标签，先提取原始字体名称
        font_name = style.font_family
        if font_name.startswith('[') and '] ' in font_name:
            font_name = self.font_manager.extract_font_name_from_label(font_name)
            
        # 根据粗体设置选择字体路径
        if style.font_bold:
            font_path = self.font_manager.get_font_path(font_name, weight='bold')
        else:
            font_path = self.font_manager.get_font_path(font_name, weight='regular')
            
        self.logger.info(f"使用字体: {style.font_family} -> {font_name} -> {font_path} (bold={style.font_bold})")
        filter_parts.append(f"fontfile={font_path}")
        filter_parts.append(f"fontsize={style.font_size}")
        
        # 字体颜色
        font_color_hex = f"0x{style.font_color[0]:02x}{style.font_color[1]:02x}{style.font_color[2]:02x}"
        filter_parts.append(f"fontcolor={font_color_hex}")
        
        # 位置配置
        x_expr, y_expr = style.get_position_expression(video_width, video_height)
        filter_parts.append(f"x={x_expr}")
        filter_parts.append(f"y={y_expr}")
        
        # 文本对齐配置
        # 注意：FFmpeg 5.1.6的drawtext滤镜不支持alignment参数
        # 对齐效果通过调整x位置表达式来实现
        if hasattr(style, 'text_alignment') and style.text_alignment:
            # 文本对齐会在位置计算中处理，这里不添加alignment参数
            pass
        
        # 行间距配置
        if hasattr(style, 'line_spacing') and style.line_spacing >= 0:
            filter_parts.append(f"line_spacing={style.line_spacing}")  # 用户可调行间距
        
        # 背景配置
        if style.background_enabled:
            # 计算背景颜色和透明度
            bg_alpha = int(style.background_opacity * 255)
            bg_color = f"0x{style.background_color[0]:02x}{style.background_color[1]:02x}{style.background_color[2]:02x}{bg_alpha:02x}"
            filter_parts.append(f"box=1")
            filter_parts.append(f"boxcolor={bg_color}")
            filter_parts.append(f"boxborderw={style.background_padding}")
        
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
    
    def _build_advanced_effect_command(self, 
                                     video_path: str,
                                     text_content: str,
                                     output_path: str,
                                     style: TextOverlayStyle,
                                     video_width: int,
                                     video_height: int,
                                     video_duration: float) -> list:
        """构建高级特效FFmpeg命令"""
        cmd = ['ffmpeg', '-i', video_path]
        
        # 构建复杂过滤器图
        filter_complex = []
        
        # 输入视频标记
        current_input = "0:v"
        
        # 获取基础文本配置
        base_filter_parts = self._get_base_text_config(style, text_content, video_width, video_height, video_duration)
        
        # 根据特效类型构建多层文本效果
        if getattr(style, 'glow_enabled', False):
            current_input = self._add_glow_effect(filter_complex, current_input, base_filter_parts, style)
        
        elif getattr(style, 'double_outline_enabled', False):
            current_input = self._add_double_outline_effect(filter_complex, current_input, base_filter_parts, style)
        
        elif getattr(style, 'neon_enabled', False):
            current_input = self._add_neon_effect(filter_complex, current_input, base_filter_parts, style)
            
        elif getattr(style, 'shadow_3d_enabled', False):
            current_input = self._add_3d_shadow_effect(filter_complex, current_input, base_filter_parts, style)
            
        elif getattr(style, 'glitch_enabled', False):
            current_input = self._add_glitch_effect(filter_complex, current_input, base_filter_parts, style)
        
        else:
            # 回退到基础效果
            basic_drawtext = "drawtext=" + ":".join(base_filter_parts)
            filter_complex.append(f"[{current_input}]{basic_drawtext}[out]")
            current_input = "out"
        
        # 组合过滤器命令
        filter_graph = ";".join(filter_complex)
        cmd.extend(['-filter_complex', filter_graph])
        cmd.extend(['-map', f'[{current_input}]'])  # 映射最终输出
        cmd.extend(['-c:a', 'copy'])  # 音频直接复制
        cmd.extend(['-y', output_path])  # 覆盖输出文件
        
        return cmd
    
    def get_available_fonts(self) -> list:
        """
        获取系统可用字体列表
        
        Returns:
            可用字体列表
        """
        return self.font_manager.get_available_fonts()
    
    def validate_font(self, font_family: str) -> bool:
        """
        验证字体是否可用
        
        Args:
            font_family: 字体族名称
            
        Returns:
            字体是否可用
        """
        return self.font_manager.validate_font(font_family)
    
    def get_font_info(self, font_family: str) -> dict:
        """
        获取字体信息
        
        Args:
            font_family: 字体族名称
            
        Returns:
            字体信息字典
        """
        return self.font_manager.get_font_info(font_family)
    
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
    
    # ======= 高级特效辅助方法 =======
    
    def _get_base_text_config(self, style: TextOverlayStyle, text_content: str, 
                             video_width: int, video_height: int, video_duration: float) -> list:
        """获取基础文本配置参数"""
        filter_parts = []
        
        # 转义文本
        escaped_text = text_content.replace(':', '\\:').replace("'", "\\'")
        filter_parts.append(f"text='{escaped_text}'")
        
        # 字体配置
        font_name = style.font_family
        if font_name.startswith('[') and '] ' in font_name:
            font_name = self.font_manager.extract_font_name_from_label(font_name)
        
        if style.font_bold:
            font_path = self.font_manager.get_font_path(font_name, weight='bold')
        else:
            font_path = self.font_manager.get_font_path(font_name, weight='regular')
        
        filter_parts.append(f"fontfile={font_path}")
        filter_parts.append(f"fontsize={style.font_size}")
        
        # 位置配置
        x_expr, y_expr = style.get_position_expression(video_width, video_height)
        filter_parts.append(f"x={x_expr}")
        filter_parts.append(f"y={y_expr}")
        
        # 行间距配置
        if hasattr(style, 'line_spacing') and style.line_spacing >= 0:
            filter_parts.append(f"line_spacing={style.line_spacing}")
        
        # 时间配置
        end_time = style.end_time if style.end_time is not None else video_duration
        if style.start_time > 0 or end_time < video_duration:
            filter_parts.append(f"enable='between(t,{style.start_time},{end_time})'")
        
        return filter_parts
    
    def _add_glow_effect(self, filter_complex: list, input_label: str, 
                        base_parts: list, style: TextOverlayStyle) -> str:
        """添加发光效果"""
        # 发光效果通过多层阴影模拟
        glow_color = style.glow_color
        glow_intensity = getattr(style, 'glow_intensity', 8)
        
        # 创建发光层（多个模糊阴影）
        layers = []
        for i in range(3):  # 3层发光
            blur_radius = glow_intensity + i * 2
            offset = i * 1
            
            glow_parts = base_parts.copy()
            glow_color_hex = f"0x{glow_color[0]:02x}{glow_color[1]:02x}{glow_color[2]:02x}"
            glow_parts.append(f"fontcolor={glow_color_hex}")
            glow_parts.append(f"shadowcolor={glow_color_hex}")
            glow_parts.append(f"shadowx={offset}")
            glow_parts.append(f"shadowy={offset}")
            glow_parts.append(f"shadowblur={blur_radius}")  # 注意：这个参数可能需要验证FFmpeg版本支持
            
            glow_filter = "drawtext=" + ":".join(glow_parts)
            filter_complex.append(f"[{input_label}]{glow_filter}[glow{i}]")
            input_label = f"glow{i}"
            layers.append(input_label)
        
        # 最后添加主文本
        main_parts = base_parts.copy()
        main_color_hex = f"0x{style.font_color[0]:02x}{style.font_color[1]:02x}{style.font_color[2]:02x}"
        main_parts.append(f"fontcolor={main_color_hex}")
        
        # 添加描边
        if style.enable_border:
            border_color_hex = f"0x{style.border_color[0]:02x}{style.border_color[1]:02x}{style.border_color[2]:02x}"
            main_parts.append(f"borderw={style.border_width}")
            main_parts.append(f"bordercolor={border_color_hex}")
        
        main_filter = "drawtext=" + ":".join(main_parts)
        filter_complex.append(f"[{input_label}]{main_filter}[glow_final]")
        
        return "glow_final"
    
    def _add_double_outline_effect(self, filter_complex: list, input_label: str,
                                  base_parts: list, style: TextOverlayStyle) -> str:
        """添加双重描边效果"""
        # 外描边层
        outer_parts = base_parts.copy()
        outer_color = getattr(style, 'outline_outer_color', (0, 0, 0))
        outer_width = getattr(style, 'outline_outer_width', 4)
        outer_color_hex = f"0x{outer_color[0]:02x}{outer_color[1]:02x}{outer_color[2]:02x}"
        
        # 外描边使用透明字体，只显示描边
        outer_parts.append(f"fontcolor=0x00000000")  # 透明字体
        outer_parts.append(f"borderw={outer_width}")
        outer_parts.append(f"bordercolor={outer_color_hex}")
        
        outer_filter = "drawtext=" + ":".join(outer_parts)
        filter_complex.append(f"[{input_label}]{outer_filter}[outer_outline]")
        
        # 内描边层
        inner_parts = base_parts.copy()
        inner_color = getattr(style, 'outline_inner_color', (255, 255, 255))
        inner_width = getattr(style, 'outline_inner_width', 2)
        inner_color_hex = f"0x{inner_color[0]:02x}{inner_color[1]:02x}{inner_color[2]:02x}"
        
        # 内描边也使用透明字体，只显示描边
        inner_parts.append(f"fontcolor=0x00000000")  # 透明字体
        inner_parts.append(f"borderw={inner_width}")
        inner_parts.append(f"bordercolor={inner_color_hex}")
        
        inner_filter = "drawtext=" + ":".join(inner_parts)
        filter_complex.append(f"[outer_outline]{inner_filter}[double_outline]")
        
        # 最后添加主文本
        main_parts = base_parts.copy()
        main_color_hex = f"0x{style.font_color[0]:02x}{style.font_color[1]:02x}{style.font_color[2]:02x}"
        main_parts.append(f"fontcolor={main_color_hex}")
        
        main_filter = "drawtext=" + ":".join(main_parts)
        filter_complex.append(f"[double_outline]{main_filter}[double_final]")
        
        return "double_final"
    
    def _add_neon_effect(self, filter_complex: list, input_label: str,
                        base_parts: list, style: TextOverlayStyle) -> str:
        """添加霓虹灯效果"""
        neon_color = getattr(style, 'neon_base_color', (255, 20, 147))
        neon_layers = getattr(style, 'neon_glow_layers', 3)
        neon_intensity = getattr(style, 'neon_intensity', 10)
        
        # 创建多层霓虹发光
        for i in range(neon_layers):
            blur_size = neon_intensity + i * 3
            alpha_value = max(80 - i * 20, 20)  # 逐层降低透明度
            
            neon_parts = base_parts.copy()
            # 霓虹色带透明度
            neon_color_hex = f"0x{neon_color[0]:02x}{neon_color[1]:02x}{neon_color[2]:02x}{alpha_value:02x}"
            neon_parts.append(f"fontcolor=0x00000000")  # 透明字体
            neon_parts.append(f"shadowcolor={neon_color_hex}")
            neon_parts.append(f"shadowx=0")
            neon_parts.append(f"shadowy=0")
            
            neon_filter = "drawtext=" + ":".join(neon_parts)
            filter_complex.append(f"[{input_label}]{neon_filter}[neon{i}]")
            input_label = f"neon{i}"
        
        # 主文本（霓虹颜色）
        main_parts = base_parts.copy()
        main_color_hex = f"0x{neon_color[0]:02x}{neon_color[1]:02x}{neon_color[2]:02x}"
        main_parts.append(f"fontcolor={main_color_hex}")
        
        # 霓虹边框
        main_parts.append(f"borderw=2")
        main_parts.append(f"bordercolor=0xFFFFFFFF")  # 白色边框
        
        main_filter = "drawtext=" + ":".join(main_parts)
        filter_complex.append(f"[{input_label}]{main_filter}[neon_final]")
        
        return "neon_final"
    
    def _add_3d_shadow_effect(self, filter_complex: list, input_label: str,
                             base_parts: list, style: TextOverlayStyle) -> str:
        """添加3D立体阴影效果"""
        shadow_layers = getattr(style, 'shadow_3d_layers', 5)
        shadow_depth = getattr(style, 'shadow_3d_depth', 3)
        shadow_angle = getattr(style, 'shadow_3d_angle', 225)  # 度
        
        # 计算阴影偏移
        import math
        angle_rad = math.radians(shadow_angle)
        base_offset_x = math.cos(angle_rad) * shadow_depth
        base_offset_y = math.sin(angle_rad) * shadow_depth
        
        # 创建多层3D阴影
        for i in range(shadow_layers):
            layer_offset_x = base_offset_x * (i + 1)
            layer_offset_y = base_offset_y * (i + 1)
            alpha_value = max(150 - i * 25, 30)  # 逐层降低透明度
            
            shadow_parts = base_parts.copy()
            shadow_color_hex = f"0x000000{alpha_value:02x}"  # 黑色阴影带透明度
            shadow_parts.append(f"fontcolor={shadow_color_hex}")
            shadow_parts.append(f"shadowcolor={shadow_color_hex}")
            shadow_parts.append(f"shadowx={int(layer_offset_x)}")
            shadow_parts.append(f"shadowy={int(layer_offset_y)}")
            
            shadow_filter = "drawtext=" + ":".join(shadow_parts)
            filter_complex.append(f"[{input_label}]{shadow_filter}[shadow3d{i}]")
            input_label = f"shadow3d{i}"
        
        # 主文本
        main_parts = base_parts.copy()
        main_color_hex = f"0x{style.font_color[0]:02x}{style.font_color[1]:02x}{style.font_color[2]:02x}"
        main_parts.append(f"fontcolor={main_color_hex}")
        
        # 添加描边增强立体感
        if style.enable_border:
            border_color_hex = f"0x{style.border_color[0]:02x}{style.border_color[1]:02x}{style.border_color[2]:02x}"
            main_parts.append(f"borderw={style.border_width}")
            main_parts.append(f"bordercolor={border_color_hex}")
        
        main_filter = "drawtext=" + ":".join(main_parts)
        filter_complex.append(f"[{input_label}]{main_filter}[shadow3d_final]")
        
        return "shadow3d_final"
    
    def _add_glitch_effect(self, filter_complex: list, input_label: str,
                          base_parts: list, style: TextOverlayStyle) -> str:
        """添加故障效果"""
        displacement = getattr(style, 'glitch_displacement', 3)
        
        # RGB偏移效果（红、绿、蓝通道分离）
        if getattr(style, 'glitch_color_shift', True):
            # 红色通道偏移
            red_parts = base_parts.copy()
            red_parts.append(f"fontcolor=0xFF0000FF")  # 纯红色
            red_parts.append(f"x={base_parts[3].split('=')[1]}+{displacement}")  # X偏移
            red_filter = "drawtext=" + ":".join(red_parts)
            filter_complex.append(f"[{input_label}]{red_filter}[glitch_red]")
            
            # 青色通道偏移
            cyan_parts = base_parts.copy()
            cyan_parts.append(f"fontcolor=0x00FFFFFF")  # 青色
            cyan_parts.append(f"x={base_parts[3].split('=')[1]}-{displacement}")  # X偏移
            cyan_filter = "drawtext=" + ":".join(cyan_parts)
            filter_complex.append(f"[glitch_red]{cyan_filter}[glitch_color]")
            
            input_label = "glitch_color"
        
        # 主文本
        main_parts = base_parts.copy()
        main_color_hex = f"0x{style.font_color[0]:02x}{style.font_color[1]:02x}{style.font_color[2]:02x}"
        main_parts.append(f"fontcolor={main_color_hex}")
        
        if style.enable_border:
            border_color_hex = f"0x{style.border_color[0]:02x}{style.border_color[1]:02x}{style.border_color[2]:02x}"
            main_parts.append(f"borderw={style.border_width}")
            main_parts.append(f"bordercolor={border_color_hex}")
        
        main_filter = "drawtext=" + ":".join(main_parts)
        filter_complex.append(f"[{input_label}]{main_filter}[glitch_final]")
        
        return "glitch_final"
