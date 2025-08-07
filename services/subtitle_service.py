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
    
    def _process_long_text(self, text: str, max_chars_per_line: int = 30) -> str:
        """
        处理长文本，自动换行
        
        Args:
            text: 原始文本
            max_chars_per_line: 每行最大字符数
            
        Returns:
            处理后的文本
        """
        if len(text) <= max_chars_per_line:
            return text
        
        import re
        
        # 检测是否主要为中文文本
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        is_chinese_dominant = chinese_chars > len(text) * 0.3
        
        if is_chinese_dominant:
            # 中文文本处理
            return self._process_chinese_text(text, max_chars_per_line)
        else:
            # 英文文本处理
            return self._process_english_text(text, max_chars_per_line)
    
    def _process_chinese_text(self, text: str, max_chars_per_line: int) -> str:
        """处理中文文本"""
        import re
        
        lines = []
        current_line = ""
        
        # 按标点符号分割
        parts = re.split(r'([，。！？；：、])', text)
        
        for part in parts:
            if not part:
                continue
                
            if len(current_line + part) <= max_chars_per_line:
                current_line += part
            else:
                if current_line:
                    lines.append(current_line)
                    current_line = part
                else:
                    # 单个部分太长，强制分割
                    while len(part) > max_chars_per_line:
                        lines.append(part[:max_chars_per_line])
                        part = part[max_chars_per_line:]
                    current_line = part
        
        if current_line:
            lines.append(current_line)
        
        # 限制为最多2行
        if len(lines) > 2:
            # 合并到2行
            all_text = ''.join(lines)
            mid = len(all_text) // 2
            
            # 找合适的分割点
            split_point = mid
            for i in range(max(0, mid - 5), min(len(all_text), mid + 5)):
                if all_text[i] in '，。！？；：、':
                    split_point = i + 1
                    break
            
            lines = [all_text[:split_point], all_text[split_point:]]
        
        return '\n'.join(lines)
    
    def _process_english_text(self, text: str, max_chars_per_line: int) -> str:
        """处理英文文本"""
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            
            if len(test_line) <= max_chars_per_line:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        # 限制为最多2行
        if len(lines) > 2:
            # 重新分配
            all_words = text.split()
            mid = len(all_words) // 2
            
            line1 = ' '.join(all_words[:mid])
            line2 = ' '.join(all_words[mid:])
            
            lines = [line1, line2]
        
        return '\n'.join(lines)
    
    def _smart_wrap_text(self, text: str) -> str:
        """
        智能文本换行，适配不同语言
        
        Args:
            text: 原始文本
            
        Returns:
            处理后的文本
        """
        # 检测文本长度，短文本不处理
        if len(text) <= 50:
            return text
        
        import re
        
        # 检测是否主要为中文文本
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        is_chinese_dominant = chinese_chars > len(text) * 0.3
        
        if is_chinese_dominant:
            # 中文文本：每行约25个字符
            return self._wrap_chinese_text(text, 25)
        else:
            # 英文文本：每行约60个字符或按单词换行
            return self._wrap_english_text(text, 60)
    
    def _wrap_chinese_text(self, text: str, max_chars: int) -> str:
        """中文文本换行"""
        import re
        
        # 按标点符号分割
        parts = re.split(r'([，。！？；：、])', text)
        
        lines = []
        current_line = ""
        
        for part in parts:
            if not part:
                continue
                
            if len(current_line + part) <= max_chars:
                current_line += part
            else:
                if current_line:
                    lines.append(current_line.strip())
                current_line = part
        
        if current_line:
            lines.append(current_line.strip())
        
        # 最多2行
        if len(lines) > 2:
            mid = len(''.join(lines)) // 2
            all_text = ''.join(lines)
            lines = [all_text[:mid], all_text[mid:]]
        
        return '\n'.join(lines)
    
    def _wrap_english_text(self, text: str, max_chars: int) -> str:
        """英文文本换行"""
        words = text.split()
        
        # 如果单词数少，直接按长度分割
        if len(words) <= 3:
            if len(text) > max_chars:
                mid = len(text) // 2
                # 找最近的空格
                for i in range(mid - 10, mid + 10):
                    if i < len(text) and text[i] == ' ':
                        return text[:i] + '\n' + text[i+1:]
                # 没找到空格就强制分割
                return text[:mid] + '\n' + text[mid:]
            return text
        
        # 按单词分行
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            
            if len(test_line) <= max_chars:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        # 最多2行，如果超过就重新分配
        if len(lines) > 2:
            all_words = words
            mid = len(all_words) // 2
            line1 = ' '.join(all_words[:mid])
            line2 = ' '.join(all_words[mid:])
            lines = [line1, line2]
        
        return '\n'.join(lines)
    
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
            
            # 确保输出目录存在
            import os
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # 使用UTF-8 BOM编码以确保兼容性
            with open(output_path, 'w', encoding='utf-8-sig') as f:
                valid_segments = 0
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
                    
                    # 对长文本进行换行处理
                    processed_text = self._smart_wrap_text(text_part.strip())
                    
                    # 写入SRT格式
                    f.write(f"{valid_segments + 1}\n")
                    f.write(f"{self._format_timestamp(start_time)} --> {self._format_timestamp(end_time)}\n")
                    f.write(f"{processed_text}\n\n")
                    valid_segments += 1
                
                # 如果没有识别到语音，创建一个默认字幕
                if valid_segments == 0:
                    logger.warning("未检测到语音内容，创建默认字幕")
                    f.write("1\n")
                    f.write("00:00:00,000 --> 00:00:05,000\n")
                    f.write("未检测到语音内容\n\n")
                    valid_segments = 1
            
            logger.info(f"SRT字幕文件生成完成: {output_path} (包含 {valid_segments} 条字幕)")
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
        
        # 处理 Whisper 格式化的 segments 字符串列表
        segments = whisper_result['segments']
        
        # 直接调用现有的 generate_srt_from_segments 方法
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
            # 尝试多种编码格式
            for encoding in ['utf-8-sig', 'utf-8', 'gbk', 'gb2312']:
                try:
                    with open(srt_path, 'r', encoding=encoding) as f:
                        content = f.read().strip()
                    break
                except UnicodeDecodeError:
                    continue
            else:
                logger.error(f"无法识别字幕文件编码: {srt_path}")
                return False
                
            if not content:
                return False
                
            # 简单验证：检查是否包含时间戳格式
            return '-->' in content and len(content.strip()) > 0
            
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
            # 尝试多种编码格式
            content = None
            for encoding in ['utf-8-sig', 'utf-8', 'gbk', 'gb2312']:
                try:
                    with open(srt_path, 'r', encoding=encoding) as f:
                        content = f.read().strip()
                    break
                except UnicodeDecodeError:
                    continue
            
            if content is None:
                logger.error(f"无法读取字幕文件: {srt_path}")
                return None
            
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