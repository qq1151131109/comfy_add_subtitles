"""
文本覆盖节点使用示例
演示如何在ComfyUI工作流中使用文本覆盖功能
"""

import os
import sys

# 添加父目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

# 由于ComfyUI依赖问题，这里只演示配置，不实际导入节点
# from comfyui_nodes.text_overlay_node import TextOverlayVideoNode
# from services.text_overlay_service import TextOverlayStyle


def create_sample_workflow():
    """
    创建示例工作流配置
    展示如何在ComfyUI中配置文本覆盖节点
    """
    
    # 工作流配置示例
    workflow_config = {
        "nodes": [
            {
                "id": 1,
                "type": "VHS_LoadVideoPath",
                "pos": [100, 100],
                "size": [300, 200],
                "inputs": {},
                "outputs": [
                    {"name": "IMAGE", "type": "IMAGE"}
                ],
                "widgets_values": {
                    "video": "/path/to/your/video.mp4"
                }
            },
            {
                "id": 2, 
                "type": "TextOverlayVideoNode",
                "pos": [500, 100],
                "size": [400, 500],
                "inputs": [
                    {"name": "images", "type": "IMAGE", "link_from": 1}
                ],
                "outputs": [
                    {"name": "images", "type": "IMAGE"},
                    {"name": "processing_log", "type": "STRING"}
                ],
                "widgets_values": {
                    "text_content": "这是覆盖在视频上的文本",
                    "position": "bottom_center",
                    "font_size": 32,
                    "font_color_r": 0,     # 黑色文字
                    "font_color_g": 0,
                    "font_color_b": 0,
                    "background_color_r": 255,  # 白色背景
                    "background_color_g": 255,
                    "background_color_b": 255,
                    "background_opacity": 0.8,
                    "enable_background": True,
                    "font_bold": True,
                    "text_alignment": "center",
                    "enable_shadow": False,
                    "enable_border": False,
                    "margin_x": 50,
                    "margin_y": 50
                }
            },
            {
                "id": 3,
                "type": "VHS_VideoCombine", 
                "pos": [1000, 100],
                "size": [300, 400],
                "inputs": [
                    {"name": "images", "type": "IMAGE", "link_from": 2}
                ],
                "outputs": [],
                "widgets_values": {
                    "frame_rate": 30,
                    "filename_prefix": "output_with_text",
                    "format": "video/h264-mp4"
                }
            }
        ],
        "links": [
            [1, 1, 0, 2, 0, "IMAGE"],  # 视频加载 -> 文本覆盖
            [2, 2, 0, 3, 0, "IMAGE"]   # 文本覆盖 -> 视频输出
        ]
    }
    
    return workflow_config


def demo_text_styles():
    """
    演示不同的文本样式配置
    """
    
    print("📝 文本覆盖样式演示")
    print("=" * 50)
    
    # 样式1: 电影字幕风格
    print("🎬 电影字幕风格:")
    style1 = {
        "text_content": "这是电影字幕样式的文本",
        "position": "bottom_center",
        "font_size": 28,
        "font_color_r": 255, "font_color_g": 255, "font_color_b": 255,  # 白色文字
        "background_color_r": 0, "background_color_g": 0, "background_color_b": 0,  # 黑色背景
        "background_opacity": 0.7,
        "enable_background": True,
        "font_bold": True,
        "enable_shadow": True,
        "margin_y": 80
    }
    print(f"  位置: {style1['position']}")
    print(f"  字体大小: {style1['font_size']}")
    print(f"  背景: 半透明黑色")
    print(f"  文字: 白色粗体")
    print()
    
    # 样式2: 新闻标题风格
    print("📺 新闻标题风格:")
    style2 = {
        "text_content": "重要新闻标题",
        "position": "top_center",
        "font_size": 24,
        "font_color_r": 0, "font_color_g": 0, "font_color_b": 0,  # 黑色文字
        "background_color_r": 255, "background_color_g": 255, "background_color_b": 0,  # 黄色背景
        "background_opacity": 0.9,
        "enable_background": True,
        "font_bold": True,
        "margin_y": 30
    }
    print(f"  位置: {style2['position']}")
    print(f"  字体大小: {style2['font_size']}")
    print(f"  背景: 黄色")
    print(f"  文字: 黑色粗体")
    print()
    
    # 样式3: 简洁风格
    print("✨ 简洁风格:")
    style3 = {
        "text_content": "简洁的文本覆盖",
        "position": "center",
        "font_size": 20,
        "font_color_r": 50, "font_color_g": 50, "font_color_b": 50,  # 深灰色文字
        "background_color_r": 255, "background_color_g": 255, "background_color_b": 255,  # 白色背景
        "background_opacity": 0.5,
        "enable_background": True,
        "font_bold": False,
        "enable_shadow": False,
        "enable_border": False
    }
    print(f"  位置: {style3['position']}")
    print(f"  字体大小: {style3['font_size']}")
    print(f"  背景: 半透明白色")
    print(f"  文字: 深灰色常规")
    print()


def integration_tips():
    """
    集成提示和最佳实践
    """
    
    print("🔧 集成提示和最佳实践")
    print("=" * 50)
    
    tips = [
        "1. 节点位置：将文本覆盖节点放在图像处理链的最后阶段",
        "2. 输入连接：确保images输入连接到视频加载或图像处理节点的输出",
        "3. 文本内容：支持多行文本，使用换行符分隔",
        "4. 字体大小：建议根据视频分辨率调整，1080p视频建议24-32像素",
        "5. 颜色搭配：确保文字和背景有足够的对比度",
        "6. 位置选择：根据视频内容选择合适的位置避免遮挡重要内容",
        "7. 性能考虑：处理大量帧时可能需要较长时间",
        "8. 依赖要求：确保系统安装了FFmpeg",
        "9. 测试建议：先用短视频测试参数配置",
        "10. 输出格式：节点输出图像序列，需要配合视频合成节点使用"
    ]
    
    for tip in tips:
        print(f"  {tip}")
    
    print()


def troubleshooting():
    """
    常见问题解决方案
    """
    
    print("🐛 常见问题解决方案")
    print("=" * 50)
    
    issues = [
        {
            "问题": "节点在ComfyUI中不显示",
            "解决方案": [
                "检查custom_nodes目录结构是否正确",
                "确认__init__.py文件中已注册节点",
                "重启ComfyUI服务",
                "查看控制台错误信息"
            ]
        },
        {
            "问题": "文本覆盖处理失败",
            "解决方案": [
                "检查FFmpeg是否正确安装",
                "确认输入图像序列格式正确",
                "验证文本内容是否包含特殊字符",
                "查看processing_log输出的错误信息"
            ]
        },
        {
            "问题": "文本显示位置不正确",
            "解决方案": [
                "检查position参数设置",
                "调整margin_x和margin_y边距",
                "确认视频分辨率与预期一致",
                "尝试不同的位置预设"
            ]
        },
        {
            "问题": "处理速度较慢",
            "解决方案": [
                "减小视频分辨率或帧数",
                "关闭不必要的效果（阴影、边框等）",
                "使用更快的存储设备",
                "考虑分段处理长视频"
            ]
        }
    ]
    
    for issue in issues:
        print(f"❓ {issue['问题']}:")
        for solution in issue['解决方案']:
            print(f"   • {solution}")
        print()


def main():
    """主函数"""
    
    print("🎨 ComfyUI文本覆盖节点使用指南")
    print("=" * 70)
    print()
    
    # 演示样式配置
    demo_text_styles()
    
    # 集成提示
    integration_tips()
    
    # 问题解决
    troubleshooting()
    
    # 工作流示例
    print("⚙️ 工作流配置示例")
    print("=" * 50)
    print("在ComfyUI中的典型工作流:")
    print("  视频加载 → [图像处理] → 文本覆盖 → 视频输出")
    print()
    print("节点连接:")
    print("  1. VHS_LoadVideoPath.IMAGE → TextOverlayVideoNode.images")
    print("  2. TextOverlayVideoNode.images → VHS_VideoCombine.images")
    print()
    
    print("✅ 文本覆盖节点已就绪！")
    print("可以在ComfyUI的'Video/Text'分类中找到'📝 Text Overlay Video'节点")


if __name__ == "__main__":
    main()
