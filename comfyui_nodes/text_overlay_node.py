"""
ComfyUI自定义节点：文本覆盖视频节点
为视频添加自定义文本覆盖功能
"""

import os
import sys
import logging
import tempfile
import time
from typing import Dict, Any, Tuple
from datetime import datetime

# 添加父目录到Python路径以支持导入
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

try:
    from ..services.text_overlay_service import TextOverlayService, TextOverlayStyle, TextAlignment
except ImportError:
    from services.text_overlay_service import TextOverlayService, TextOverlayStyle, TextAlignment


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
        self.service = TextOverlayService()
        self.setup_logging()
    
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
                "text_content": ("STRING", {
                    "default": "在这里输入文本内容",
                    "multiline": True,
                    "placeholder": "要显示在视频上的文本"
                }),
                "position": ([
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
                "font_size": ("INT", {
                    "default": 24,
                    "min": 12,
                    "max": 72,
                    "step": 1,
                    "tooltip": "字体大小（像素）"
                }),
                "font_color": ([
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
                "background_color": ([
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
                "background_opacity": ("FLOAT", {
                    "default": 0.8,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.1,
                    "tooltip": "背景透明度（0=完全透明，1=完全不透明）"
                }),
                "max_chars_per_line": ("INT", {
                    "default": 30,
                    "min": 10,
                    "max": 100,
                    "step": 1,
                    "tooltip": "每行最大字符数（超过自动换行）"
                })
            },
            "optional": {
                "enable_background": ("BOOLEAN", {
                    "default": True,
                    "tooltip": "是否启用文字背景"
                }),
                "font_bold": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "是否使用粗体字"
                }),
                "text_alignment": ([
                    "居中",        # center
                    "左对齐",      # left
                    "右对齐"       # right
                ], {
                    "default": "居中",
                    "tooltip": "文本对齐方式"
                }),
                "enable_shadow": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "是否启用文字阴影"
                }),
                "enable_border": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "是否启用文字边框"
                }),
                "margin_x": ("INT", {
                    "default": 50,
                    "min": 0,
                    "max": 200,
                    "step": 5,
                    "tooltip": "水平边距（像素）"
                }),
                "margin_y": ("INT", {
                    "default": 50,
                    "min": 0,
                    "max": 200,
                    "step": 5,
                    "tooltip": "垂直边距（像素）"
                })
            }
        }
    
    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("images", "processing_log")
    FUNCTION = "process_text_overlay"
    CATEGORY = "Video/Text"
    OUTPUT_NODE = False
    
    def process_text_overlay(self, images, text_content: str, position: str, 
                           font_size: int, font_color: str, background_color: str,
                           background_opacity: float, max_chars_per_line: int, **kwargs) -> Tuple[Any, str]:
        """
        处理文本覆盖
        
        Args:
            images: 输入图像序列
            text_content: 文本内容
            position: 位置
            font_size: 字体大小
            font_color: 字体颜色预设
            background_color: 背景颜色预设
            background_opacity: 背景透明度
            max_chars_per_line: 每行最大字符数
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
            enable_background = kwargs.get("enable_background", True)
            font_bold = kwargs.get("font_bold", False)
            text_alignment_cn = kwargs.get("text_alignment", "居中")
            enable_shadow = kwargs.get("enable_shadow", False)
            enable_border = kwargs.get("enable_border", False)
            margin_x = kwargs.get("margin_x", 50)
            margin_y = kwargs.get("margin_y", 50)
            
            log_messages = []
            
            # 转换中文选项为内部使用的英文值
            position_en = self.get_position_preset(position)
            font_rgb = self.get_color_rgb(font_color)
            background_rgb = self.get_color_rgb(background_color)
            text_alignment = self.get_text_alignment(text_alignment_cn)
            
            # 处理文本换行
            wrapped_text = self.wrap_text(text_content, max_chars_per_line)
            text_stats = self.get_text_stats(wrapped_text)
            
            # 步骤1: 显示配置信息
            progress.log_progress("初始化配置", f"文本: '{text_content[:20]}{'...' if len(text_content) > 20 else ''}'", 10.0)
            log_messages.append(f"开始处理文本覆盖: '{text_content}'")
            log_messages.append(f"换行后文本: {text_stats['total_lines']}行, 最长{text_stats['max_line_length']}字符")
            log_messages.append(f"位置: {position}, 字体大小: {font_size}")
            log_messages.append(f"位置计算: 按视频高度比例自适应")
            log_messages.append(f"字体颜色: {font_color} {font_rgb}")
            log_messages.append(f"背景颜色: {background_color} {background_rgb}")
            log_messages.append(f"背景透明度: {background_opacity}")
            
            # 创建样式配置
            style = TextOverlayStyle()
            style.position_preset = position_en
            style.font_size = font_size
            style.font_color = font_rgb
            style.background_color = background_rgb
            style.background_opacity = background_opacity if background_color != "透明" else 0.0
            style.background_enabled = enable_background and background_color != "透明"
            style.font_bold = font_bold
            style.text_alignment = text_alignment
            style.enable_shadow = enable_shadow
            style.enable_border = enable_border
            style.margin_x = margin_x
            style.margin_y = margin_y
            
            # 显示位置计算详情（用于调试）
            x_expr, y_expr = style.get_position_expression(1920, 1080)  # 使用标准分辨率计算示例
            log_messages.append(f"位置表达式: x={x_expr}, y={y_expr}")
            
            # 步骤2: 验证样式配置
            progress.log_progress("验证样式配置", f"位置: {position}, 大小: {font_size}px", 20.0)
            is_valid, error_msg = self.service.validate_style(style)
            if not is_valid:
                error_message = f"❌ 样式配置错误: {error_msg}"
                progress.log_error(error_message)
                log_messages.append(error_message)
                return images, "\n".join(log_messages)
            
            # 步骤3: 准备临时文件
            progress.log_progress("准备临时文件", "创建输入输出文件", 30.0)
            
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
                progress.log_progress("转换图像序列", f"临时文件: {os.path.basename(temp_input_path)}", 40.0)
                success = self._images_to_video(images, temp_input_path)
                if not success:
                    error_message = "❌ 图像序列转换为视频失败"
                    progress.log_error(error_message)
                    log_messages.append(error_message)
                    return images, "\n".join(log_messages)
                
                progress.log_progress("图像序列转换完成", "准备添加文本覆盖", 60.0)
                log_messages.append("✅ 图像序列转换完成")
                
                # 步骤5: 添加文本覆盖
                progress.log_progress("添加文本覆盖", f"使用FFmpeg处理", 70.0)
                log_messages.append("正在添加文本覆盖...")
                success = self.service.add_text_overlay(
                    temp_input_path, wrapped_text, temp_output_path, style
                )
                
                if not success:
                    error_message = "❌ 文本覆盖添加失败"
                    progress.log_error(error_message)
                    log_messages.append(error_message)
                    return images, "\n".join(log_messages)
                
                progress.log_progress("文本覆盖完成", "开始转换回图像序列", 85.0)
                log_messages.append("✅ 文本覆盖添加完成")
                
                # 步骤6: 将处理后的视频转换回图像序列
                progress.log_progress("转换回图像序列", f"输出文件: {os.path.basename(temp_output_path)}", 90.0)
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
            error_msg = f"❌ 处理过程中发生错误: {str(e)}"
            log_messages.append(error_msg)
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
