#!/usr/bin/env python3
"""
字幕样式测试脚本
测试字幕样式配置功能
"""

from subtitle_style import SubtitleStyle, SubtitlePosition, PresetStyles, FontWeight
import json

def test_preset_styles():
    """测试预设样式"""
    print("=== 预设样式测试 ===")
    
    styles = {
        "default": PresetStyles.default(),
        "cinema": PresetStyles.cinema(),
        "youtube": PresetStyles.youtube(),
        "minimal": PresetStyles.minimal(),
        "top_news": PresetStyles.top_news()
    }
    
    for name, style in styles.items():
        print(f"\n{name.upper()}样式:")
        print(f"  位置: {style.position.value}")
        print(f"  字体大小: {style.font_size}")
        print(f"  字体颜色: {style.font_color}")
        print(f"  阴影: {'启用' if style.shadow_enabled else '禁用'}")
        print(f"  背景: {'启用' if style.background_enabled else '禁用'}")

def test_custom_style():
    """测试自定义样式"""
    print("\n=== 自定义样式测试 ===")
    
    # 创建自定义样式
    custom_style = SubtitleStyle(
        position=SubtitlePosition.TOP_CENTER,
        font_size=32,
        font_color=(255, 255, 0),  # 黄色
        shadow_enabled=True,
        shadow_offset_x=3,
        shadow_offset_y=3,
        outline_width=2
    )
    
    print("自定义样式配置:")
    print(f"  位置: {custom_style.position.value}")
    print(f"  字体大小: {custom_style.font_size}")
    print(f"  字体颜色: {custom_style.font_color}")
    print(f"  阴影偏移: ({custom_style.shadow_offset_x}, {custom_style.shadow_offset_y})")
    print(f"  描边宽度: {custom_style.outline_width}")

def test_position_filter():
    """测试位置过滤器生成"""
    print("\n=== 位置过滤器测试 ===")
    
    video_width, video_height = 1920, 1080
    
    positions = [
        SubtitlePosition.BOTTOM_CENTER,
        SubtitlePosition.TOP_CENTER,
        SubtitlePosition.CENTER,
        SubtitlePosition.BOTTOM_LEFT,
        SubtitlePosition.TOP_RIGHT
    ]
    
    for pos in positions:
        style = SubtitleStyle(position=pos, margin_x=50, margin_y=50)
        filter_str = style.get_position_filter(video_width, video_height)
        print(f"  {pos.value}: {filter_str}")

def test_style_serialization():
    """测试样式序列化"""
    print("\n=== 样式序列化测试 ===")
    
    # 创建样式
    original_style = PresetStyles.cinema()
    
    # 转换为字典
    style_dict = original_style.to_dict()
    print("样式字典:")
    print(json.dumps(style_dict, indent=2, ensure_ascii=False))
    
    # 从字典恢复
    restored_style = SubtitleStyle.from_dict(style_dict)
    print(f"\n恢复后的样式位置: {restored_style.position.value}")
    print(f"恢复后的字体大小: {restored_style.font_size}")

def test_ffmpeg_filter():
    """测试FFmpeg过滤器生成"""
    print("\n=== FFmpeg过滤器测试 ===")
    
    # 导入video_service来测试过滤器生成
    try:
        from video_service import VideoService
        
        service = VideoService()
        style = PresetStyles.cinema()
        
        # 模拟生成过滤器（不实际调用FFmpeg）
        print("电影院样式的FFmpeg配置:")
        print(f"  字体大小: {style.font_size}")
        print(f"  位置: {style.position.value}")
        print(f"  阴影: {style.shadow_enabled}")
        print(f"  描边宽度: {style.outline_width}")
        
    except ImportError as e:
        print(f"无法导入video_service: {e}")

if __name__ == '__main__':
    print("字幕样式功能测试")
    print("=" * 50)
    
    test_preset_styles()
    test_custom_style()
    test_position_filter()
    test_style_serialization()
    test_ffmpeg_filter()
    
    print("\n测试完成！")
    print("\n使用示例:")
    print("python main.py video.mp4 --style cinema")
    print("python main.py video.mp4 --position top_center --font-size 32 --shadow")
    print("python main.py video.mp4 --font-color '255,255,0' --no-shadow")