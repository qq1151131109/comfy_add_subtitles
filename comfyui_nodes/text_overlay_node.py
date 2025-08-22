"""
ComfyUI自定义节点：文本覆盖视频节点
为视频添加自定义文本覆盖功能
"""

import os
import sys
import logging
import tempfile
from typing import Dict, Any, Tuple

# 添加父目录到Python路径以支持导入
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

try:
    from ..services.text_overlay_service import TextOverlayService, TextOverlayStyle, TextAlignment
except ImportError:
    from services.text_overlay_service import TextOverlayService, TextOverlayStyle, TextAlignment


class TextOverlayVideoNode:
    """ComfyUI文本覆盖视频节点"""
    
    def __init__(self):
        self.service = TextOverlayService()
        
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
                    "bottom_center",    # 底部居中
                    "bottom_left",      # 底部左对齐
                    "bottom_right",     # 底部右对齐
                    "top_center",       # 顶部居中
                    "top_left",         # 顶部左对齐
                    "top_right",        # 顶部右对齐
                    "center",           # 屏幕中央
                    "center_left",      # 中央左对齐
                    "center_right"      # 中央右对齐
                ], {
                    "default": "bottom_center",
                    "tooltip": "文本在视频中的位置"
                }),
                "font_size": ("INT", {
                    "default": 24,
                    "min": 12,
                    "max": 72,
                    "step": 1,
                    "tooltip": "字体大小（像素）"
                }),
                "font_color_r": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 255,
                    "step": 1,
                    "tooltip": "字体颜色红色分量"
                }),
                "font_color_g": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 255,
                    "step": 1,
                    "tooltip": "字体颜色绿色分量"
                }),
                "font_color_b": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 255,
                    "step": 1,
                    "tooltip": "字体颜色蓝色分量"
                }),
                "background_color_r": ("INT", {
                    "default": 255,
                    "min": 0,
                    "max": 255,
                    "step": 1,
                    "tooltip": "背景颜色红色分量"
                }),
                "background_color_g": ("INT", {
                    "default": 255,
                    "min": 0,
                    "max": 255,
                    "step": 1,
                    "tooltip": "背景颜色绿色分量"
                }),
                "background_color_b": ("INT", {
                    "default": 255,
                    "min": 0,
                    "max": 255,
                    "step": 1,
                    "tooltip": "背景颜色蓝色分量"
                }),
                "background_opacity": ("FLOAT", {
                    "default": 0.8,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.1,
                    "tooltip": "背景透明度（0=完全透明，1=完全不透明）"
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
                    "center",
                    "left", 
                    "right"
                ], {
                    "default": "center",
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
                           font_size: int, font_color_r: int, font_color_g: int, font_color_b: int,
                           background_color_r: int, background_color_g: int, background_color_b: int,
                           background_opacity: float, **kwargs) -> Tuple[Any, str]:
        """
        处理文本覆盖
        
        Args:
            images: 输入图像序列
            text_content: 文本内容
            position: 位置
            font_size: 字体大小
            font_color_r, font_color_g, font_color_b: 字体颜色RGB
            background_color_r, background_color_g, background_color_b: 背景颜色RGB
            background_opacity: 背景透明度
            **kwargs: 其他可选参数
            
        Returns:
            (处理后的图像序列, 处理日志)
        """
        try:
            # 获取可选参数
            enable_background = kwargs.get("enable_background", True)
            font_bold = kwargs.get("font_bold", False)
            text_alignment = kwargs.get("text_alignment", "center")
            enable_shadow = kwargs.get("enable_shadow", False)
            enable_border = kwargs.get("enable_border", False)
            margin_x = kwargs.get("margin_x", 50)
            margin_y = kwargs.get("margin_y", 50)
            
            log_messages = []
            log_messages.append(f"开始处理文本覆盖: '{text_content}'")
            log_messages.append(f"位置: {position}, 字体大小: {font_size}")
            log_messages.append(f"字体颜色: RGB({font_color_r}, {font_color_g}, {font_color_b})")
            log_messages.append(f"背景颜色: RGB({background_color_r}, {background_color_g}, {background_color_b})")
            
            # 创建样式配置
            style = TextOverlayStyle()
            style.position_preset = position
            style.font_size = font_size
            style.font_color = (font_color_r, font_color_g, font_color_b)
            style.background_color = (background_color_r, background_color_g, background_color_b)
            style.background_opacity = background_opacity
            style.background_enabled = enable_background
            style.font_bold = font_bold
            style.text_alignment = text_alignment
            style.enable_shadow = enable_shadow
            style.enable_border = enable_border
            style.margin_x = margin_x
            style.margin_y = margin_y
            
            # 验证样式配置
            is_valid, error_msg = self.service.validate_style(style)
            if not is_valid:
                error_message = f"❌ 样式配置错误: {error_msg}"
                log_messages.append(error_message)
                return images, "\n".join(log_messages)
            
            # 由于ComfyUI中图像处理通常在内存中进行，
            # 这里我们需要将图像序列转换为临时视频文件进行处理
            log_messages.append("正在转换图像序列为临时视频...")
            
            # 创建临时文件
            with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_input:
                temp_input_path = temp_input.name
            
            with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_output:
                temp_output_path = temp_output.name
            
            try:
                # 将图像序列保存为临时视频
                success = self._images_to_video(images, temp_input_path)
                if not success:
                    error_message = "❌ 图像序列转换为视频失败"
                    log_messages.append(error_message)
                    return images, "\n".join(log_messages)
                
                log_messages.append("✅ 图像序列转换完成")
                
                # 添加文本覆盖
                log_messages.append("正在添加文本覆盖...")
                success = self.service.add_text_overlay(
                    temp_input_path, text_content, temp_output_path, style
                )
                
                if not success:
                    error_message = "❌ 文本覆盖添加失败"
                    log_messages.append(error_message)
                    return images, "\n".join(log_messages)
                
                log_messages.append("✅ 文本覆盖添加完成")
                
                # 将处理后的视频转换回图像序列
                log_messages.append("正在转换回图像序列...")
                processed_images = self._video_to_images(temp_output_path)
                
                if processed_images is None:
                    error_message = "❌ 视频转换为图像序列失败"
                    log_messages.append(error_message)
                    return images, "\n".join(log_messages)
                
                log_messages.append("✅ 处理完成！")
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
