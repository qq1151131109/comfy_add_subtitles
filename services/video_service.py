"""
视频处理服务
负责视频信息获取和下载
"""

import subprocess
import os
import json
from typing import Dict, Optional
import logging

# 导入样式配置
try:
    from ..core.subtitle_style import SubtitleStyle, PresetStyles
except ImportError:
    # 兼容性导入
    try:
        from core.subtitle_style import SubtitleStyle, PresetStyles
    except ImportError:
        from subtitle_style import SubtitleStyle, PresetStyles

logger = logging.getLogger(__name__)


class VideoService:
    """视频处理服务类"""
    
    def __init__(self):
        self._cached_fonts = None
    
    def _get_available_fonts(self) -> list:
        """
        获取系统可用字体列表
        
        Returns:
            可用字体名称列表
        """
        if self._cached_fonts is not None:
            return self._cached_fonts
        
        try:
            import subprocess
            result = subprocess.run(['fc-list', ':'], capture_output=True, text=True, encoding='utf-8', errors='ignore')
            if result.returncode == 0:
                fonts = []
                for line in result.stdout.split('\n'):
                    if ':' in line:
                        font_info = line.split(':')[1].strip()
                        if font_info:
                            fonts.append(font_info)
                self._cached_fonts = fonts
                return fonts
        except Exception as e:
            logger.warning(f"获取字体列表失败: {e}")
        
        # 回退到常用字体
        self._cached_fonts = ['Arial', 'DejaVu Sans', 'Liberation Sans']
        return self._cached_fonts
    
    def _find_best_font(self, preferred_fonts: str) -> str:
        """
        从首选字体列表中找到最合适的字体
        
        Args:
            preferred_fonts: 逗号分隔的首选字体列表
            
        Returns:
            最合适的字体名称
        """
        available_fonts = self._get_available_fonts()
        font_list = [f.strip() for f in preferred_fonts.split(',')]
        
        # 尝试找到匹配的字体
        for font in font_list:
            for available in available_fonts:
                if font.lower() in available.lower():
                    logger.info(f"使用字体: {available}")
                    return available
        
        # 如果都没找到，使用中文字体回退策略
        chinese_fonts = ['Noto Sans CJK SC', 'WenQuanYi Zen Hei', 'WenQuanYi Micro Hei']
        for font in chinese_fonts:
            for available in available_fonts:
                if font.lower() in available.lower():
                    logger.info(f"使用中文回退字体: {available}")
                    return available
        
        # 最后回退到默认字体
        logger.warning("未找到合适的中文字体，使用默认字体")
        return 'Arial'
    
    def embed_subtitles(self, video_path: str, srt_path: str, output_path: str, 
                       style: Optional[SubtitleStyle] = None) -> bool:
        """
        将SRT字幕嵌入到视频中，支持自定义样式
        
        Args:
            video_path: 原视频文件路径
            srt_path: SRT字幕文件路径
            output_path: 输出视频文件路径
            style: 字幕样式配置，默认使用标准样式
            
        Returns:
            嵌入是否成功
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(video_path):
                logger.error(f"视频文件不存在: {video_path}")
                return False
                
            if not os.path.exists(srt_path):
                logger.error(f"字幕文件不存在: {srt_path}")
                return False
            
            # 如果没有指定样式，使用默认样式
            if style is None:
                style = PresetStyles.default()
            
            # 获取视频信息以计算字幕位置
            video_info = self.get_video_info_local(video_path)
            if not video_info:
                logger.warning("无法获取视频信息，使用默认样式")
                video_width, video_height = 1920, 1080
            else:
                video_width = video_info.get('width', 1920)
                video_height = video_info.get('height', 1080)
            
            # 构建字幕过滤器
            subtitle_filter = self._build_subtitle_filter(srt_path, style, video_width, video_height)
            
            # 使用ffmpeg将字幕嵌入视频 - 添加字符编码支持
            cmd = [
                'ffmpeg', '-i', video_path,
                '-vf', subtitle_filter,
                '-c:a', 'copy',  # 复制音频流，不重新编码
                '-c:v', 'libx264',  # 指定视频编码器
                '-preset', 'medium',  # 编码速度预设
                output_path,
                '-y'  # 覆盖输出文件
            ]
            
            logger.info(f"开始嵌入字幕: {video_path} + {srt_path} -> {output_path}")
            logger.info(f"字幕样式: {style.position.value}, 字体大小: {style.font_size}")
            logger.info(f"执行命令: {' '.join(cmd)}")
            
            # 添加超时机制，避免进程卡死
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)  # 5分钟超时
            except subprocess.TimeoutExpired:
                logger.error("FFmpeg 处理超时（5分钟），可能是字幕文件或参数有问题")
                return False
            
            if result.returncode == 0:
                # 验证输出文件是否真正创建
                if os.path.exists(output_path):
                    file_size = os.path.getsize(output_path)
                    logger.info(f"字幕嵌入完成: {output_path} ({file_size} 字节)")
                    return True
                else:
                    logger.error(f"字幕嵌入失败: 输出文件未创建 {output_path}")
                    logger.error(f"FFmpeg stderr: {result.stderr}")
                    logger.error(f"FFmpeg stdout: {result.stdout}")
                    return False
            else:
                logger.error(f"字幕嵌入失败 (退出码: {result.returncode})")
                logger.error(f"FFmpeg stderr: {result.stderr}")
                logger.error(f"FFmpeg stdout: {result.stdout}")
                logger.error(f"执行的命令: {' '.join(cmd)}")
                return False
                
        except FileNotFoundError:
            logger.error("错误: 未找到ffmpeg，请先安装ffmpeg")
            return False
        except Exception as e:
            logger.error(f"字幕嵌入出错: {e}")
            return False
    
    def _build_subtitle_filter(self, srt_path: str, style: SubtitleStyle, 
                              video_width: int, video_height: int) -> str:
        """
        构建FFmpeg字幕过滤器字符串，支持高级样式配置
        
        Args:
            srt_path: SRT文件路径
            style: 字幕样式
            video_width: 视频宽度
            video_height: 视频高度
            
        Returns:
            FFmpeg过滤器字符串
        """
        # 转义文件路径中的特殊字符 - 针对中文字符进行优化
        escaped_path = srt_path.replace('\\', '/').replace(':', '\\:').replace("'", "\\'")
        
        # 使用简化但可控的字幕样式配置
        style_configs = []
        
        # 字体配置
        best_font = self._find_best_font(style.font_family)
        style_configs.append(f"FontName={best_font}")
        style_configs.append(f"FontSize={style.font_size}")
        
        # 字体颜色
        font_color = f"&H{style.font_color[2]:02x}{style.font_color[1]:02x}{style.font_color[0]:02x}"
        style_configs.append(f"PrimaryColour={font_color}")
        
        # 描边配置
        if style.outline_width > 0:
            outline_color = f"&H{style.outline_color[2]:02x}{style.outline_color[1]:02x}{style.outline_color[0]:02x}"
            style_configs.append(f"OutlineColour={outline_color}")
            style_configs.append(f"Outline={style.outline_width}")
        else:
            style_configs.append("Outline=0")
        
        # 阴影配置 - 根据参数控制
        if style.shadow_enabled:
            shadow_depth = max(abs(style.shadow_offset_x), abs(style.shadow_offset_y))
            if shadow_depth == 0:
                shadow_depth = 2  # 默认阴影深度
            style_configs.append(f"Shadow={shadow_depth}")
        else:
            style_configs.append("Shadow=0")
        
        # 字体粗细
        if style.font_weight.value == "bold":
            style_configs.append("Bold=1")
        else:
            style_configs.append("Bold=0")
        
        # 对齐方式 - 根据位置设置
        alignment = self._get_alignment_from_position(style.position)
        style_configs.append(f"Alignment={alignment}")
        
        # 边距配置 - 根据位置调整
        if style.position.value in ['bottom_center', 'bottom_left', 'bottom_right']:
            style_configs.append(f"MarginV={style.margin_y}")
        elif style.position.value in ['top_center', 'top_left', 'top_right']:
            style_configs.append(f"MarginV={style.margin_y}")
        else:  # center
            style_configs.append(f"MarginV=0")
        
        # 左右边距（简化版本，只在需要时添加）
        if style.position.value in ['bottom_left', 'top_left']:
            style_configs.append(f"MarginL={style.margin_x}")
        elif style.position.value in ['bottom_right', 'top_right']:
            style_configs.append(f"MarginR={style.margin_x}")
        
        # 组合样式配置
        force_style = ",".join(style_configs)
        
        # 构建字幕过滤器
        return f"subtitles='{escaped_path}':force_style='{force_style}'"
    
    def _get_alignment_from_position(self, position: 'SubtitlePosition') -> int:
        """
        根据字幕位置获取ASS对齐值
        
        Args:
            position: 字幕位置枚举
            
        Returns:
            ASS对齐值 (1-9)
        """
        # ASS对齐值映射:
        # 1=左下, 2=中下, 3=右下
        # 4=左中, 5=中中, 6=右中  
        # 7=左上, 8=中上, 9=右上
        alignment_map = {
            'bottom_left': 1,
            'bottom_center': 2,
            'bottom_right': 3,
            'center': 5,
            'top_left': 7,
            'top_center': 8,
            'top_right': 9,
            'custom': 2  # 默认底部居中
        }
        return alignment_map.get(position.value, 2)
    
    def embed_subtitles_with_preset(self, video_path: str, srt_path: str, output_path: str, 
                                   preset_name: str = "default") -> bool:
        """
        使用预设样式嵌入字幕
        
        Args:
            video_path: 原视频文件路径
            srt_path: SRT字幕文件路径
            output_path: 输出视频文件路径
            preset_name: 预设样式名称 (default, cinema, youtube, minimal, top_news)
            
        Returns:
            嵌入是否成功
        """
        # 获取预设样式
        style_map = {
            "default": PresetStyles.default,
            "cinema": PresetStyles.cinema,
            "youtube": PresetStyles.youtube,
            "minimal": PresetStyles.minimal,
            "top_news": PresetStyles.top_news,
            "strong_shadow": PresetStyles.strong_shadow,
            "dramatic_shadow": PresetStyles.dramatic_shadow
        }
        
        if preset_name not in style_map:
            logger.warning(f"未知的预设样式: {preset_name}，使用默认样式")
            preset_name = "default"
        
        style = style_map[preset_name]()
        logger.info(f"使用预设样式: {preset_name}")
        
        return self.embed_subtitles(video_path, srt_path, output_path, style)
    
    def get_video_info_local(self, video_path: str) -> Optional[Dict]:
        """
        获取本地视频文件信息
        
        Args:
            video_path: 视频文件路径
            
        Returns:
            视频信息字典
        """
        try:
            cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_format', '-show_streams', video_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                import json
                info = json.loads(result.stdout)
                
                # 提取视频流信息
                video_stream = None
                for stream in info.get('streams', []):
                    if stream.get('codec_type') == 'video':
                        video_stream = stream
                        break
                
                format_info = info.get('format', {})
                
                return {
                    'duration': float(format_info.get('duration', 0)),
                    'size': int(format_info.get('size', 0)),
                    'width': video_stream.get('width', 0) if video_stream else 0,
                    'height': video_stream.get('height', 0) if video_stream else 0,
                    'fps': eval(video_stream.get('r_frame_rate', '0/1')) if video_stream else 0
                }
            return None
            
        except Exception as e:
            logger.warning(f"获取视频信息失败: {e}")
            return None