#!/usr/bin/env python3
"""
视频实时字幕添加主程序
整合视频处理、音频提取、语音识别和字幕嵌入功能
"""

import os
import sys
import logging
import argparse
import tempfile
from pathlib import Path

from services.audio_service import AudioService
from services.whisper_service import WhisperService
from services.subtitle_service import SubtitleService
from services.video_service import VideoService
from core.subtitle_style import SubtitleStyle, SubtitlePosition, PresetStyles, FontWeight

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('subtitle_generator.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)


class SubtitleGenerator:
    """视频字幕生成器主类"""
    
    def __init__(self):
        self.audio_service = AudioService()
        self.whisper_service = WhisperService()
        self.subtitle_service = SubtitleService()
        self.video_service = VideoService()
    
    def generate_subtitles_for_video(self, video_path: str, output_dir: str = None, 
                                   model_size: str = "large-v3", device: str = "cuda",
                                   subtitle_style: SubtitleStyle = None, preset_style: str = None) -> bool:
        """
        为视频生成字幕并嵌入
        
        Args:
            video_path: 视频文件路径
            output_dir: 输出目录，默认为视频文件所在目录
            model_size: Whisper模型大小
            device: 计算设备
            subtitle_style: 自定义字幕样式
            preset_style: 预设字幕样式名称
            
        Returns:
            处理是否成功
        """
        try:
            # 验证输入文件
            if not os.path.exists(video_path):
                logger.error(f"视频文件不存在: {video_path}")
                return False
            
            # 设置输出目录
            if output_dir is None:
                output_dir = os.path.dirname(os.path.abspath(video_path))
            
            os.makedirs(output_dir, exist_ok=True)
            
            # 生成文件名
            video_name = Path(video_path).stem
            audio_path = os.path.join(output_dir, f"{video_name}.wav")
            srt_path = os.path.join(output_dir, f"{video_name}.srt")
            output_video_path = os.path.join(output_dir, f"{video_name}_with_subtitles.mp4")
            
            logger.info(f"开始处理视频: {video_path}")
            
            # 步骤1: 从视频中提取音频
            logger.info("步骤1: 提取音频...")
            if not self.audio_service.extract_audio_from_video(video_path, audio_path):
                logger.error("音频提取失败")
                return False
            
            # 验证音频文件
            if not self.audio_service.validate_audio_file(audio_path):
                logger.error("音频文件验证失败")
                return False
            
            # 步骤2: 使用Whisper进行语音识别
            logger.info("步骤2: 语音识别...")
            whisper_result = self.whisper_service.transcribe_audio(
                audio_path, model_size=model_size, device=device
            )
            
            if not whisper_result:
                logger.error("语音识别失败")
                return False
            
            # 输出识别信息
            language = whisper_result.get('language', 'unknown')
            language_name = self.whisper_service.get_language_name(language)
            confidence = whisper_result.get('language_probability', 0)
            
            logger.info(f"识别语言: {language_name} (置信度: {confidence:.2f})")
            logger.info(f"识别到 {len(whisper_result['segments'])} 个语音段落")
            
            # 步骤3: 生成SRT字幕文件
            logger.info("步骤3: 生成字幕文件...")
            if not self.subtitle_service.generate_srt_from_whisper_result(whisper_result, srt_path):
                logger.error("字幕文件生成失败")
                return False
            
            # 验证字幕文件
            if not self.subtitle_service.validate_srt_file(srt_path):
                logger.error("字幕文件验证失败")
                return False
            
            # 输出字幕信息
            subtitle_info = self.subtitle_service.get_subtitle_info(srt_path)
            if subtitle_info:
                logger.info(f"字幕条目数: {subtitle_info['entry_count']}")
                logger.info(f"字幕文件大小: {subtitle_info['file_size']} 字节")
            
            # 步骤4: 将字幕嵌入视频
            logger.info("步骤4: 嵌入字幕...")
            
            # 确定使用的字幕样式
            if preset_style:
                # 使用预设样式
                if not self.video_service.embed_subtitles_with_preset(video_path, srt_path, output_video_path, preset_style):
                    logger.error("字幕嵌入失败")
                    return False
            else:
                # 使用自定义样式或默认样式
                if not self.video_service.embed_subtitles(video_path, srt_path, output_video_path, subtitle_style):
                    logger.error("字幕嵌入失败")
                    return False
            
            # 获取输出视频信息
            video_info = self.video_service.get_video_info_local(output_video_path)
            if video_info:
                duration = video_info.get('duration', 0)
                size_mb = video_info.get('size', 0) / (1024 * 1024)
                logger.info(f"输出视频时长: {duration:.2f}秒")
                logger.info(f"输出视频大小: {size_mb:.2f}MB")
            
            logger.info(f"处理完成！输出文件:")
            logger.info(f"  字幕文件: {srt_path}")
            logger.info(f"  带字幕视频: {output_video_path}")
            
            # 清理临时音频文件
            try:
                os.remove(audio_path)
                logger.info("临时音频文件已清理")
            except:
                pass
            
            return True
            
        except Exception as e:
            logger.error(f"处理过程中发生错误: {e}")
            return False
    
    def batch_process_videos(self, video_dir: str, output_dir: str = None, 
                           model_size: str = "large-v3", device: str = "cuda",
                           subtitle_style: SubtitleStyle = None, preset_style: str = None) -> int:
        """
        批量处理视频目录中的所有视频文件
        
        Args:
            video_dir: 视频目录路径
            output_dir: 输出目录
            model_size: Whisper模型大小
            device: 计算设备
            subtitle_style: 自定义字幕样式
            preset_style: 预设字幕样式名称
            
        Returns:
            成功处理的视频数量
        """
        if not os.path.exists(video_dir):
            logger.error(f"视频目录不存在: {video_dir}")
            return 0
        
        # 支持的视频格式
        video_extensions = ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm']
        
        # 查找所有视频文件
        video_files = []
        for ext in video_extensions:
            video_files.extend(Path(video_dir).glob(f"*{ext}"))
            video_files.extend(Path(video_dir).glob(f"*{ext.upper()}"))
        
        if not video_files:
            logger.warning(f"在目录 {video_dir} 中未找到支持的视频文件")
            return 0
        
        logger.info(f"找到 {len(video_files)} 个视频文件")
        
        success_count = 0
        for i, video_file in enumerate(video_files, 1):
            logger.info(f"处理第 {i}/{len(video_files)} 个视频: {video_file.name}")
            
            if self.generate_subtitles_for_video(
                str(video_file), output_dir, model_size, device, subtitle_style, preset_style
            ):
                success_count += 1
                logger.info(f"✓ {video_file.name} 处理成功")
            else:
                logger.error(f"✗ {video_file.name} 处理失败")
        
        logger.info(f"批量处理完成: {success_count}/{len(video_files)} 个视频处理成功")
        return success_count


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='视频实时字幕生成工具')
    parser.add_argument('input', help='输入视频文件或目录路径')
    parser.add_argument('-o', '--output', help='输出目录路径')
    parser.add_argument('-m', '--model', default='large-v3', 
                       choices=['tiny', 'base', 'small', 'medium', 'large', 'large-v2', 'large-v3'],
                       help='Whisper模型大小 (默认: large-v3)')
    parser.add_argument('-d', '--device', default='cuda', choices=['cuda', 'cpu'],
                       help='计算设备 (默认: cuda)')
    parser.add_argument('--batch', action='store_true', help='批量处理模式')
    
    # 字幕样式选项
    parser.add_argument('--style', default='default',
                       choices=['default', 'cinema', 'youtube', 'minimal', 'top_news', 'strong_shadow', 'dramatic_shadow'],
                       help='字幕预设样式 (默认: default)')
    parser.add_argument('--position', choices=['bottom_center', 'bottom_left', 'bottom_right', 
                                              'top_center', 'top_left', 'top_right', 'center'],
                       help='字幕位置')
    parser.add_argument('--font-size', type=int, help='字体大小')
    parser.add_argument('--font-color', help='字体颜色 (RGB格式, 如: 255,255,255)')
    parser.add_argument('--shadow', action='store_true', help='启用字幕阴影')
    parser.add_argument('--no-shadow', action='store_true', help='禁用字幕阴影')
    
    args = parser.parse_args()
    
    # 处理字幕样式配置
    subtitle_style = None
    if any([args.position, args.font_size, args.font_color, args.shadow, args.no_shadow]):
        # 创建自定义样式
        subtitle_style = PresetStyles.default()  # 从默认样式开始
        
        if args.position:
            subtitle_style.position = SubtitlePosition(args.position)
        
        if args.font_size:
            subtitle_style.font_size = args.font_size
        
        if args.font_color:
            try:
                color_parts = args.font_color.split(',')
                if len(color_parts) == 3:
                    subtitle_style.font_color = tuple(int(c.strip()) for c in color_parts)
                else:
                    logger.warning("字体颜色格式错误，使用默认颜色")
            except ValueError:
                logger.warning("字体颜色格式错误，使用默认颜色")
        
        if args.shadow:
            subtitle_style.shadow_enabled = True
        elif args.no_shadow:
            subtitle_style.shadow_enabled = False
    
    # 创建字幕生成器
    generator = SubtitleGenerator()
    
    try:
        if args.batch or os.path.isdir(args.input):
            # 批量处理模式
            success_count = generator.batch_process_videos(
                args.input, args.output, args.model, args.device, subtitle_style, args.style
            )
            if success_count > 0:
                logger.info(f"批量处理成功完成，共处理 {success_count} 个视频")
                sys.exit(0)
            else:
                logger.error("批量处理失败")
                sys.exit(1)
        else:
            # 单文件处理模式
            if generator.generate_subtitles_for_video(
                args.input, args.output, args.model, args.device, subtitle_style, args.style
            ):
                logger.info("视频字幕生成成功完成")
                sys.exit(0)
            else:
                logger.error("视频字幕生成失败")
                sys.exit(1)
                
    except KeyboardInterrupt:
        logger.info("用户中断操作")
        sys.exit(1)
    except Exception as e:
        logger.error(f"程序执行出错: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()