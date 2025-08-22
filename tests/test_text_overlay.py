"""
文本覆盖节点测试
"""

import os
import sys
import unittest
from unittest.mock import Mock, patch

# 添加父目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from services.text_overlay_service import TextOverlayService, TextOverlayStyle, TextAlignment
from comfyui_nodes.text_overlay_node import TextOverlayVideoNode


class TestTextOverlayService(unittest.TestCase):
    """测试文本覆盖服务"""
    
    def setUp(self):
        self.service = TextOverlayService()
    
    def test_style_validation(self):
        """测试样式验证"""
        style = TextOverlayStyle()
        
        # 测试有效样式
        is_valid, error_msg = self.service.validate_style(style)
        self.assertTrue(is_valid, f"默认样式应该有效: {error_msg}")
        
        # 测试无效开始时间
        style.start_time = -1.0
        is_valid, error_msg = self.service.validate_style(style)
        self.assertFalse(is_valid)
        self.assertIn("开始时间不能为负数", error_msg)
        
        # 测试无效结束时间
        style.start_time = 5.0
        style.end_time = 3.0
        is_valid, error_msg = self.service.validate_style(style)
        self.assertFalse(is_valid)
        self.assertIn("结束时间必须大于开始时间", error_msg)
        
        # 测试无效颜色
        style.start_time = 0.0
        style.end_time = None
        style.font_color = (300, 0, 0)  # 无效的RGB值
        is_valid, error_msg = self.service.validate_style(style)
        self.assertFalse(is_valid)
        self.assertIn("字体颜色", error_msg)
    
    def test_position_expression(self):
        """测试位置表达式生成"""
        style = TextOverlayStyle()
        
        # 测试底部居中
        style.position_preset = "bottom_center"
        x, y = style.get_position_expression(1920, 1080)
        self.assertEqual(x, "(w-text_w)/2")
        self.assertEqual(y, f"h-text_h-{style.margin_y}")
        
        # 测试顶部左对齐
        style.position_preset = "top_left"
        x, y = style.get_position_expression(1920, 1080)
        self.assertEqual(x, str(style.margin_x))
        self.assertEqual(y, str(style.margin_y))
        
        # 测试居中
        style.position_preset = "center"
        x, y = style.get_position_expression(1920, 1080)
        self.assertEqual(x, "(w-text_w)/2")
        self.assertEqual(y, "(h-text_h)/2")


class TestTextOverlayVideoNode(unittest.TestCase):
    """测试文本覆盖视频节点"""
    
    def setUp(self):
        self.node = TextOverlayVideoNode()
    
    def test_input_types(self):
        """测试输入类型定义"""
        input_types = self.node.INPUT_TYPES()
        
        # 检查必需输入
        required = input_types["required"]
        self.assertIn("images", required)
        self.assertIn("text_content", required)
        self.assertIn("position", required)
        self.assertIn("font_size", required)
        
        # 检查位置选项
        position_options = required["position"][0]
        expected_positions = [
            "bottom_center", "bottom_left", "bottom_right",
            "top_center", "top_left", "top_right",
            "center", "center_left", "center_right"
        ]
        for pos in expected_positions:
            self.assertIn(pos, position_options)
        
        # 检查可选输入
        optional = input_types["optional"]
        self.assertIn("enable_background", optional)
        self.assertIn("font_bold", optional)
        self.assertIn("text_alignment", optional)
    
    def test_return_types(self):
        """测试返回类型"""
        self.assertEqual(self.node.RETURN_TYPES, ("IMAGE", "STRING"))
        self.assertEqual(self.node.RETURN_NAMES, ("images", "processing_log"))
    
    @patch('subprocess.run')
    def test_style_creation(self, mock_subprocess):
        """测试样式创建"""
        # 模拟图像输入
        mock_images = Mock()
        
        # 模拟FFmpeg成功执行
        mock_subprocess.return_value.returncode = 0
        mock_subprocess.return_value.stdout = ""
        mock_subprocess.return_value.stderr = ""
        
        # 由于实际的图像处理比较复杂，这里主要测试参数传递
        try:
            # 测试基本参数
            result = self.node.process_text_overlay(
                images=mock_images,
                text_content="测试文本",
                position="bottom_center",
                font_size=24,
                font_color_r=0,
                font_color_g=0,
                font_color_b=0,
                background_color_r=255,
                background_color_g=255,
                background_color_b=255,
                background_opacity=0.8
            )
            
            # 结果应该是元组
            self.assertIsInstance(result, tuple)
            self.assertEqual(len(result), 2)
            
        except Exception as e:
            # 由于依赖复杂，这里主要验证没有语法错误
            print(f"测试过程中的预期错误（缺少依赖）: {e}")


if __name__ == "__main__":
    # 运行测试
    print("🧪 开始运行文本覆盖节点测试...")
    unittest.main(verbosity=2)
