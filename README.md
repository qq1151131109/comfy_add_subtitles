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

```mermaid
graph LR
    A[🎥 视频/图像序列] --> B[📝 Text Overlay Video]
    B --> C[📹 输出视频]
```

**典型工作流：**
1. 视频加载或图像处理节点
2. 连接到`TextOverlayVideoNode`
3. 配置文本内容和样式
4. 输出到视频合成节点

## ⚙️ 配置选项

### 文本覆盖样式

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| 文本内容 | STRING | - | 要显示的文本 |
| 位置 | 选择 | bottom_center | 9种预设位置 |
| 字体大小 | INT | 24 | 12-72像素 |
| 字体颜色 | RGB | (0,0,0) | 黑色 |
| 背景颜色 | RGB | (255,255,255) | 白色 |
| 背景透明度 | FLOAT | 0.8 | 0-1 |

### 位置选项

- `bottom_center` - 底部居中
- `bottom_left` - 底部左对齐  
- `bottom_right` - 底部右对齐
- `top_center` - 顶部居中
- `top_left` - 顶部左对齐
- `top_right` - 顶部右对齐
- `center` - 屏幕中央
- `center_left` - 中央左对齐
- `center_right` - 中央右对齐

## 🎨 样式预设

### 电影字幕风格
```
位置: bottom_center
字体大小: 28
字体颜色: 白色 (255,255,255)
背景颜色: 黑色 (0,0,0)
背景透明度: 0.7
粗体: 是
```

### 新闻标题风格
```
位置: top_center
字体大小: 24
字体颜色: 黑色 (0,0,0)
背景颜色: 黄色 (255,255,0)
背景透明度: 0.9
粗体: 是
```

### 简洁风格
```
位置: center
字体大小: 20
字体颜色: 深灰色 (50,50,50)
背景颜色: 白色 (255,255,255)
背景透明度: 0.5
粗体: 否
```

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