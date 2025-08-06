# ComfyUI 视频字幕节点安装指南

## 📦 节点功能

这个自定义节点将视频字幕生成功能集成到ComfyUI中，支持：
- 🎥 自动语音识别（基于Whisper）
- 📝 SRT字幕文件生成
- 🎨 多种字幕样式（包括强阴影效果）
- ⚡ GPU加速处理
- 🎯 灵活的参数配置

## 🚀 安装步骤

### 1. 复制节点文件

将以下文件复制到ComfyUI的自定义节点目录：

```bash
# ComfyUI自定义节点目录通常为：
# ComfyUI/custom_nodes/video_subtitle/

mkdir -p /path/to/ComfyUI/custom_nodes/video_subtitle/
cp -r ./* /path/to/ComfyUI/custom_nodes/video_subtitle/
```

### 2. 安装依赖

在ComfyUI环境中安装必要的Python包：

```bash
# 激活ComfyUI的Python环境
conda activate comfyui  # 或者您的ComfyUI环境名称

# 安装依赖
pip install faster-whisper
# 确保已安装ffmpeg
```

### 3. 重启ComfyUI

重启ComfyUI服务器以加载新节点。

## 🎛️ 节点参数说明

### 必需参数

| 参数名 | 类型 | 说明 | 默认值 |
|--------|------|------|--------|
| `video_path` | STRING | 输入视频文件的完整路径 | "" |
| `output_dir` | STRING | 输出目录路径 | "./output" |
| `whisper_model` | DROPDOWN | Whisper模型大小 | "large-v3" |
| `device` | DROPDOWN | 计算设备(cuda/cpu) | "cuda" |
| `subtitle_style` | DROPDOWN | 预设字幕样式 | "default" |

### 可选参数

| 参数名 | 类型 | 说明 | 默认值 |
|--------|------|------|--------|
| `custom_font_size` | INT | 自定义字体大小(12-72) | 24 |
| `custom_position` | DROPDOWN | 自定义字幕位置 | "none" |
| `font_color_r` | INT | 字体红色分量(0-255) | 255 |
| `font_color_g` | INT | 字体绿色分量(0-255) | 255 |
| `font_color_b` | INT | 字体蓝色分量(0-255) | 255 |
| `enable_shadow` | BOOLEAN | 是否启用阴影 | True |

### 预设样式选项

- **default**: 默认样式，白字黑边带阴影
- **cinema**: 电影院样式，大字体强阴影
- **youtube**: YouTube样式，带背景
- **minimal**: 极简样式，无阴影
- **top_news**: 新闻样式，顶部显示
- **strong_shadow**: 强阴影样式（推荐）
- **dramatic_shadow**: 戏剧化超强阴影

## 📤 输出说明

节点返回三个输出：

1. **output_video_path**: 生成的带字幕视频文件路径
2. **subtitle_file_path**: 生成的SRT字幕文件路径  
3. **processing_log**: 处理过程的详细日志

## 🎯 使用示例

### 基础用法

```
输入:
- video_path: "/path/to/your/video.mp4"
- output_dir: "./output"
- whisper_model: "large-v3"
- device: "cuda"
- subtitle_style: "strong_shadow"

输出:
- output_video_path: "./output/video_with_subtitles.mp4"
- subtitle_file_path: "./output/video.srt"
- processing_log: "✅ 视频处理完成!..."
```

### 自定义样式

```
输入:
- video_path: "/path/to/your/video.mp4"
- subtitle_style: "default"
- custom_font_size: 32
- custom_position: "top_center"
- font_color_r: 255
- font_color_g: 255
- font_color_b: 0  # 黄色字体
- enable_shadow: True
```

## 🔧 工作流集成

### 典型工作流

1. **视频输入** → **字幕生成节点** → **视频输出**
2. 可以与其他视频处理节点串联
3. 支持批量处理（通过循环节点）

### 节点连接

```
[Video Input] 
    ↓ (video_path)
[🎬 Video Subtitle Generator]
    ↓ (output_video_path)
[Video Output/Preview]
```

## ⚠️ 注意事项

1. **文件路径**: 使用绝对路径以避免路径问题
2. **GPU内存**: large-v3模型需要较多GPU内存
3. **处理时间**: 视频长度影响处理时间
4. **音频质量**: 清晰的音频能提高识别准确度
5. **中文支持**: 对中文语音识别效果很好

## 🐛 故障排除

### 常见问题

1. **模块导入错误**
   ```
   解决: 确保所有依赖文件都在同一目录
   ```

2. **FFmpeg未找到**
   ```
   解决: 安装ffmpeg并添加到PATH
   ```

3. **CUDA内存不足**
   ```
   解决: 使用较小模型或切换到CPU模式
   ```

4. **字幕不显示**
   ```
   解决: 检查视频播放器是否支持内嵌字幕
   ```

## 🔄 更新日志

- **v1.0**: 初始版本，支持基础字幕生成
- **v1.1**: 添加强阴影样式支持
- **v1.2**: 集成ComfyUI节点接口

## 📞 技术支持

如有问题，请检查：
1. ComfyUI控制台日志
2. 节点输出的processing_log
3. 确保所有依赖正确安装