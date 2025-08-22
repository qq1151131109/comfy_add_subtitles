# 🎬 ComfyUI视频字幕和文本覆盖工具

一个功能完整的ComfyUI自定义节点包，提供视频自动字幕生成和文本覆盖功能。

## ✨ 主要功能

### 🎙️ 自动字幕生成
- **Whisper集成**：基于OpenAI Whisper的高精度语音识别
- **多语言支持**：支持100+种语言的自动识别和转录
- **模块化设计**：独立的模型加载、转录和缓存管理节点
- **智能缓存**：避免重复处理，提高工作效率
- **多种样式**：内置电影、YouTube、新闻等多种字幕样式

### 📝 文本覆盖功能
- **灵活位置**：9种预设位置选择
- **丰富样式**：自定义字体大小、颜色、背景、透明度
- **实时处理**：直接在ComfyUI工作流中处理
- **高质量输出**：基于FFmpeg的专业视频处理

## 🚀 快速开始

### 安装要求

```bash
# Python依赖
pip install -r requirements.txt

# 系统依赖
# Ubuntu/Debian:
sudo apt install ffmpeg

# macOS:
brew install ffmpeg

# Windows: 下载FFmpeg并添加到PATH
```

### ComfyUI安装

1. 将此项目克隆到ComfyUI的custom_nodes目录：
```bash
cd ComfyUI/custom_nodes/
git clone https://github.com/your-username/comfy_add_subtitles.git
```

2. 安装依赖：
```bash
cd comfy_add_subtitles
pip install -r requirements.txt
```

3. 重启ComfyUI

## 📋 节点列表

### 🎙️ 字幕生成节点

| 节点名称 | 显示名称 | 功能描述 |
|----------|----------|----------|
| `WhisperModelNode` | 🤖 Whisper Model Loader | 加载和管理Whisper模型 |
| `WhisperTranscribeNode` | 🎙️ Whisper Transcribe | 音频转录为文本 |
| `WhisperCacheManagerNode` | 🗂️ Whisper Cache Manager | 管理转录缓存 |
| `VideoSubtitleWithModelNode` | 🎬 Video Subtitle (with Model) | 完整的视频字幕生成 |
| `VideoSubtitleNode` | 🎬 Video Subtitle Generator (Legacy) | 传统字幕生成节点 |

### 📝 文本覆盖节点

| 节点名称 | 显示名称 | 功能描述 |
|----------|----------|----------|
| `TextOverlayVideoNode` | 📝 Text Overlay Video | 为视频添加自定义文本覆盖 |

## 📝 Text Overlay Video 节点详细说明

### 主要功能
- 为视频添加自定义文本覆盖
- 9种垂直位置选择（水平居中）
- 12种字体颜色预设 + 13种背景颜色预设
- 支持背景透明度调节
- 自动文本换行功能
- 实时进度显示

### 核心参数

#### 必需参数
- **`images`**: 输入图像序列（来自视频节点）
- **`text_content`**: 文本内容（支持多行）
- **`position`**: 垂直位置选择（按视频高度比例，间距更大便于区分）
  - `底部居中` - 标准底部（距底边8%，默认）
  - `底部偏下` - 最靠近底部（距底边3%）
  - `底部偏上` - 底部区域上方（距底边15%）  
  - `屏幕中央` - 屏幕正中央
  - `中央偏下` - 中央偏下（中央+12%）
  - `中央偏上` - 中央偏上（中央-12%）
  - `顶部居中` - 标准顶部（距顶边8%）
  - `顶部偏下` - 顶部区域下方（距顶边15%）
  - `顶部偏上` - 最靠近顶部（距顶边3%）
- **`font_size`**: 字体大小（12-72px，默认24）
- **`font_color`**: 字体颜色预设
  - `黑色`, `白色`, `红色`, `绿色`, `蓝色`, `黄色`
  - `青色`, `洋红`, `橙色`, `紫色`, `灰色`, `深灰`
- **`background_color`**: 背景颜色预设
  - `白色` - 白色背景（默认）
  - `黑色` - 黑色背景
  - `透明` - 无背景（透明）
  - `红色`, `绿色`, `蓝色`, `黄色`, `青色`, `洋红`
  - `橙色`, `紫色`, `灰色`, `浅灰`
- **`background_opacity`**: 背景透明度（0.0=完全透明，1.0=完全不透明，默认0.8）
- **`max_chars_per_line`**: 每行最大字符数（10-100，默认30）

#### 可选参数
- **`enable_background`**: 是否启用背景（默认True）
- **`font_bold`**: 是否粗体（默认False）
- **`text_alignment`**: 文本对齐（居中/左对齐/右对齐）
- **`enable_shadow`**: 是否启用阴影（默认False）
- **`enable_border`**: 是否启用边框（默认False）
- **`margin_x`**: 水平边距（0-200px，默认50）
- **`margin_y`**: 垂直边距（0-200px，默认50）

### 使用示例

#### 经典字幕风格
```
文本内容: "这是视频字幕"
位置: bottom
字体颜色: white
背景颜色: black
背景透明度: 0.8
```

#### 新闻标题风格
```
文本内容: "重要新闻标题"
位置: top
字体颜色: black  
背景颜色: yellow
背景透明度: 0.9
```

#### 无背景风格
```
文本内容: "简洁文本"
位置: center
字体颜色: white
背景颜色: transparent
启用阴影: True
```

## 🔧 使用方法

### 方法1：自动字幕生成

```mermaid
graph LR
    A[🎥 视频文件] --> B[🤖 Whisper Model Loader]
    B --> C[🎙️ Whisper Transcribe]
    C --> D[🎬 Video Subtitle Generator]
    D --> E[📹 输出带字幕视频]
```

**典型工作流：**
1. 使用`VHS_LoadVideoPath`加载视频
2. 连接到`WhisperModelNode`加载语音识别模型
3. 使用`WhisperTranscribeNode`进行语音转录
4. 通过`VideoSubtitleWithModelNode`生成带字幕的视频

### 方法2：自定义文本覆盖

**典型工作流：**
```
视频加载 → [图像处理] → 文本覆盖 → 视频输出
```

**节点连接：**
1. `VHS_LoadVideoPath` → `TextOverlayVideoNode`
2. `TextOverlayVideoNode` → `VHS_VideoCombine`

**配置要点：**
- 在`Video/Text`分类找到`📝 Text Overlay Video`节点
- 输入要显示的文本内容
- 选择合适的位置和颜色
- 根据需要调整字体大小和背景样式

## 🎨 快速配置指南

### 常用样式组合

**🎬 电影字幕**
- 位置: `bottom` | 字体: `white` | 背景: `black` | 透明度: 0.8

**📺 新闻标题** 
- 位置: `top` | 字体: `black` | 背景: `yellow` | 透明度: 0.9

**💭 对话气泡**
- 位置: `center` | 字体: `black` | 背景: `white` | 透明度: 0.9

**🔥 警告提示**
- 位置: `center` | 字体: `white` | 背景: `red` | 粗体: 是

**🌟 无背景效果**
- 位置: `bottom` | 字体: `white` | 背景: `transparent`（透明） | 阴影: 是

## 📁 项目结构

```
comfy_add_subtitles/
├── README.md                    # 项目说明文档
├── README_TEXT_OVERLAY.md       # 文本覆盖详细文档
├── requirements.txt             # Python依赖
├── config.py                    # 配置文件
├── main.py                      # 主程序
├── __init__.py                  # ComfyUI节点注册
├── core/                        # 核心模块
│   └── subtitle_style.py       # 字幕样式定义
├── services/                    # 服务层
│   ├── audio_service.py         # 音频处理服务
│   ├── whisper_service.py       # Whisper语音识别服务
│   ├── subtitle_service.py      # 字幕处理服务
│   ├── video_service.py         # 视频处理服务
│   └── text_overlay_service.py  # 文本覆盖服务
├── comfyui_nodes/              # ComfyUI节点
│   ├── __init__.py             # 节点注册
│   ├── comfyui_subtitle_node.py
│   ├── whisper_model_node.py
│   ├── video_subtitle_with_model_node.py
│   └── text_overlay_node.py    # 文本覆盖节点
├── tests/                       # 测试文件
│   └── test_text_overlay.py
├── examples/                    # 使用示例
│   └── text_overlay_example.py
└── docs/                        # 文档目录
```

## 🛠️ 技术特性

- **高性能处理**：基于FFmpeg的专业视频处理引擎
- **智能缓存**：避免重复计算，提高处理效率
- **模块化设计**：每个功能独立封装，便于维护和扩展
- **错误处理**：完善的错误处理和日志记录
- **内存优化**：有效管理临时文件和内存使用

## 🐛 故障排除

### 常见问题

**Q: 节点在ComfyUI中不显示？**
```bash
# 检查安装
ls ComfyUI/custom_nodes/comfy_add_subtitles/
# 检查依赖
pip install -r requirements.txt
# 重启ComfyUI
```

**Q: FFmpeg相关错误？**
```bash
# 检查FFmpeg安装
ffmpeg -version
# Ubuntu安装
sudo apt install ffmpeg
# macOS安装  
brew install ffmpeg
```

**Q: Whisper模型下载慢？**
```bash
# 使用国内镜像
export HF_ENDPOINT=https://hf-mirror.com
# 或预先下载模型文件
```

**Q: 处理大视频文件很慢？**
- 使用更小的Whisper模型（tiny、base、small）
- 降低视频分辨率
- 关闭不必要的视觉效果

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🤝 贡献

欢迎提交Issue和Pull Request！

### 开发环境设置

```bash
git clone https://github.com/your-username/comfy_add_subtitles.git
cd comfy_add_subtitles
pip install -r requirements.txt
```

### 运行测试

```bash
python -m pytest tests/
```

## 📞 支持

- 📝 **文档**：详见各README文件
- 🐛 **问题报告**：[GitHub Issues](https://github.com/your-username/comfy_add_subtitles/issues)
- 💡 **功能建议**：[GitHub Discussions](https://github.com/your-username/comfy_add_subtitles/discussions)

## 🎯 路线图

### v1.1.0 (计划中)
- [ ] 支持更多字体选择
- [ ] 批量文本处理
- [ ] 动画文字效果
- [ ] SRT文件导入/导出

### v1.2.0 (计划中)
- [ ] GPU加速处理
- [ ] 实时预览功能
- [ ] 模板系统
- [ ] 更多语言支持

## 🌟 致谢

- [OpenAI Whisper](https://github.com/openai/whisper) - 强大的语音识别模型
- [ComfyUI](https://github.com/comfyanonymous/ComfyUI) - 优秀的节点式AI工具平台
- [FFmpeg](https://ffmpeg.org/) - 专业的多媒体处理工具

---

**🎉 开始创作您的视频内容吧！**