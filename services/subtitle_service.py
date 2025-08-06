"""
字幕处理服务
负责生成SRT格式字幕文件
"""

import logging
from typing import List, Dict, Optional
from datetime import timedelta

logger = logging.getLogger(__name__)


class SubtitleService:
    """字幕处理服务类"""
    
    def __init__(self):
        pass
    
    def _format_timestamp(self, seconds: float) -> str:
        """
        将秒数转换为SRT时间戳格式 (HH:MM:SS,mmm)
        
        Args:
            seconds: 秒数
            
        Returns:
            SRT格式的时间戳
        """
        td = timedelta(seconds=seconds)
        hours = int(td.total_seconds() // 3600)
        minutes = int((td.total_seconds() % 3600) // 60)
        seconds = td.total_seconds() % 60
        milliseconds = int((seconds % 1) * 1000)
        seconds = int(seconds)
        
        return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"
    
    def generate_srt_from_segments(self, segments: List, output_path: str) -> bool:
        """
        从Whisper转录段落生成SRT字幕文件
        
        Args:
            segments: Whisper转录段落列表
            output_path: SRT文件输出路径
            
        Returns:
            生成是否成功
        """
        try:
            logger.info(f"开始生成SRT字幕文件: {output_path}")
            
            with open(output_path, 'w', encoding='utf-8') as f:
                for i, segment_text in enumerate(segments, 1):
                    # 解析时间戳和文本
                    # 格式: [开始时间s -> 结束时间s] 文本内容
                    if not segment_text.startswith('[') or '] ' not in segment_text:
                        logger.warning(f"跳过格式不正确的段落: {segment_text}")
                        continue
                    
                    # 提取时间戳
                    timestamp_part = segment_text.split('] ')[0][1:]  # 移除开头的'['
                    text_part = segment_text.split('] ', 1)[1]  # 获取文本部分
                    
                    # 解析开始和结束时间
                    if ' -> ' not in timestamp_part:
                        logger.warning(f"时间戳格式错误: {timestamp_part}")
                        continue
                    
                    start_str, end_str = timestamp_part.split(' -> ')
                    start_time = float(start_str.replace('s', ''))
                    end_time = float(end_str.replace('s', ''))
                    
                    # 写入SRT格式
                    f.write(f"{i}\n")
                    f.write(f"{self._format_timestamp(start_time)} --> {self._format_timestamp(end_time)}\n")
                    f.write(f"{text_part.strip()}\n\n")
            
            logger.info(f"SRT字幕文件生成完成: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"生成SRT字幕文件失败: {e}")
            return False
    
    def generate_srt_from_whisper_result(self, whisper_result: Dict, output_path: str) -> bool:
        """
        从Whisper转录结果生成SRT字幕文件
        
        Args:
            whisper_result: Whisper转录结果字典
            output_path: SRT文件输出路径
            
        Returns:
            生成是否成功
        """
        if not whisper_result or 'segments' not in whisper_result:
            logger.error("Whisper转录结果无效")
            return False
        
        segments = whisper_result['segments']
        return self.generate_srt_from_segments(segments, output_path)
    
    def validate_srt_file(self, srt_path: str) -> bool:
        """
        验证SRT文件格式是否正确
        
        Args:
            srt_path: SRT文件路径
            
        Returns:
            文件格式是否正确
        """
        try:
            with open(srt_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                
            if not content:
                return False
                
            # 简单验证：检查是否包含时间戳格式
            return '-->' in content and content.count('\n\n') > 0
            
        except Exception as e:
            logger.warning(f"SRT文件验证失败: {e}")
            return False
    
    def get_subtitle_info(self, srt_path: str) -> Optional[Dict]:
        """
        获取字幕文件信息
        
        Args:
            srt_path: SRT文件路径
            
        Returns:
            字幕信息字典，包含条目数量等
        """
        try:
            with open(srt_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            
            # 计算字幕条目数量
            entries = content.split('\n\n')
            entry_count = len([e for e in entries if e.strip()])
            
            return {
                'entry_count': entry_count,
                'file_size': len(content.encode('utf-8')),
                'is_valid': self.validate_srt_file(srt_path)
            }
            
        except Exception as e:
            logger.warning(f"获取字幕信息失败: {e}")
            return None