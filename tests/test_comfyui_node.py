#!/usr/bin/env python3
"""
ComfyUI节点快速测试脚本
"""

import os
import sys

# 添加父目录到路径以支持导入
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from comfyui_nodes.comfyui_subtitle_node import VideoSubtitleNode

def test_node_functionality():
    """测试节点的各种功能"""
    
    print("🧪 ComfyUI视频字幕节点测试")
    print("=" * 50)
    
    # 检查测试视频
    test_video = "test.mp4"
    if not os.path.exists(test_video):
        print("❌ 未找到测试视频文件 test.mp4")
        return False
    
    # 创建节点实例
    node = VideoSubtitleNode()
    
    # 测试1: 基础功能测试
    print("\n📋 测试1: 基础功能 (default样式)")
    output_video, subtitle_file, log = node.process_video(
        video_path=test_video,
        output_dir="./test_output_basic",
        whisper_model="small",  # 使用小模型加快测试
        device="cuda",
        subtitle_style="default"
    )
    
    if output_video:
        print("✅ 基础功能测试通过")
        print(f"输出视频: {output_video}")
        print(f"字幕文件: {subtitle_file}")
    else:
        print("❌ 基础功能测试失败")
        print(log)
        return False
    
    # 测试2: 强阴影样式测试
    print("\n📋 测试2: 强阴影样式")
    output_video, subtitle_file, log = node.process_video(
        video_path=test_video,
        output_dir="./test_output_shadow",
        whisper_model="small",
        device="cuda",
        subtitle_style="strong_shadow"
    )
    
    if output_video:
        print("✅ 强阴影样式测试通过")
    else:
        print("❌ 强阴影样式测试失败")
        return False
    
    # 测试3: 自定义样式测试
    print("\n📋 测试3: 自定义样式 (黄色字体，顶部居中)")
    output_video, subtitle_file, log = node.process_video(
        video_path=test_video,
        output_dir="./test_output_custom",
        whisper_model="small",
        device="cuda",
        subtitle_style="default",
        custom_font_size=28,
        custom_position="top_center",
        font_color_r=255,
        font_color_g=255,
        font_color_b=0,  # 黄色
        enable_shadow=True
    )
    
    if output_video:
        print("✅ 自定义样式测试通过")
    else:
        print("❌ 自定义样式测试失败")
        return False
    
    # 测试4: 输入类型验证
    print("\n📋 测试4: 输入类型验证")
    input_types = node.INPUT_TYPES()
    
    required_params = input_types["required"]
    optional_params = input_types["optional"]
    
    print(f"✅ 必需参数数量: {len(required_params)}")
    print(f"✅ 可选参数数量: {len(optional_params)}")
    
    # 验证返回类型
    return_types = node.RETURN_TYPES
    return_names = node.RETURN_NAMES
    
    print(f"✅ 返回类型: {return_types}")
    print(f"✅ 返回名称: {return_names}")
    
    print("\n🎉 所有测试通过！")
    print("\n📁 生成的测试文件:")
    
    # 列出所有测试输出目录
    for test_dir in ["test_output_basic", "test_output_shadow", "test_output_custom"]:
        if os.path.exists(test_dir):
            files = os.listdir(test_dir)
            print(f"  {test_dir}/:")
            for file in files:
                size = os.path.getsize(os.path.join(test_dir, file))
                print(f"    - {file} ({size/1024/1024:.2f}MB)")
    
    return True

def test_node_categories():
    """测试节点分类和显示名称"""
    print("\n📋 节点信息测试")
    
    from comfyui_nodes.comfyui_subtitle_node import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS
    
    print(f"节点类映射: {list(NODE_CLASS_MAPPINGS.keys())}")
    print(f"节点显示名称: {list(NODE_DISPLAY_NAME_MAPPINGS.values())}")
    
    node = VideoSubtitleNode()
    print(f"节点分类: {node.CATEGORY}")
    print(f"节点函数: {node.FUNCTION}")

if __name__ == "__main__":
    print("🚀 开始ComfyUI节点完整测试")
    
    try:
        # 测试节点分类信息
        test_node_categories()
        
        # 测试节点功能
        success = test_node_functionality()
        
        if success:
            print("\n🎯 ComfyUI节点已就绪，可以部署到ComfyUI中使用！")
            print("\n📝 部署步骤:")
            print("1. 将整个项目文件夹复制到 ComfyUI/custom_nodes/ 目录")
            print("2. 重启ComfyUI")
            print("3. 在节点菜单中找到 'Video/Subtitle' → '🎬 Video Subtitle Generator'")
        else:
            print("\n❌ 测试失败，请检查错误信息")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n💥 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)