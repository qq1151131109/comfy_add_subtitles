"""
音频处理服务
负责从视频中提取音频
"""

import subprocess
import logging
from typing import Optional

# 导入配置
try:
    from ..config import AUDIO_BITRATE, AUDIO_FORMAT
except ImportError:
    # 默认配置（独立运行时使用）
    AUDIO_FORMAT = "pcm_s16le"  # 音频格式
    AUDIO_BITRATE = "192k"      # 音频比特率

logger = logging.getLogger(__name__)


class AudioService:
    """音频处理服务类"""
    
    def extract_audio_from_video(self, video_path: str, audio_path: str) -> bool:
        """
        使用ffmpeg从视频中提取音频
        
        Args:
            video_path: 视频文件路径
            audio_path: 音频输出路径
            
        Returns:
            提取是否成功
        """
        try:
            cmd = [
                'ffmpeg', '-i', video_path,
                '-vn',  # 不处理视频流
                '-acodec', AUDIO_FORMAT,
                '-ab', AUDIO_BITRATE,
                audio_path,
                '-y'  # 覆盖输出文件
            ]
            
            logger.info(f"开始提取音频: {video_path} -> {audio_path}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"音频提取完成: {audio_path}")
                return True
            else:
                logger.error(f"音频提取失败: {result.stderr}")
                return False
                
        except FileNotFoundError:
            logger.error("错误: 未找到ffmpeg，请先安装ffmpeg")
            return False
        except Exception as e:
            logger.error(f"音频提取出错: {e}")
            return False
    
    def validate_audio_file(self, audio_path: str) -> bool:
        """
        验证音频文件是否有效
        
        Args:
            audio_path: 音频文件路径
            
        Returns:
            文件是否有效
        """
        try:
            cmd = ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', audio_path]
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0
        except Exception as e:
            logger.warning(f"音频文件验证失败: {e}")
            return False
    
    def get_audio_duration(self, audio_path: str) -> Optional[float]:
        """
        获取音频时长
        
        Args:
            audio_path: 音频文件路径
            
        Returns:
            音频时长（秒），获取失败返回None
        """
        try:
            cmd = [
                'ffprobe', '-v', 'quiet', '-print_format', 'compact=print_section=0:nokey=1:escape=csv',
                '-show_entries', 'format=duration', audio_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                duration_str = result.stdout.strip()
                return float(duration_str) if duration_str else None
            return None
            
        except Exception as e:
            logger.warning(f"获取音频时长失败: {e}")
            return None