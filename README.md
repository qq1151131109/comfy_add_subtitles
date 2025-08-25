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
- **智能字体系统**：多语种字体自动检测和分类标注
- **比例定位系统**：基于视频尺寸的响应式位置计算
- **9种预设位置**：适配所有分辨率的一致视觉效果  
- **丰富样式选项**：字体粗细、颜色、背景、透明度、行间距
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

### 主要功能 ✨
- **比例定位系统**：基于视频高度百分比的响应式位置
- **智能字体管理**：自动检测系统字体并按语种分类标注
- **9种预设位置**：在所有分辨率下保持一致的视觉效果
- **字体粗细控制**：支持正常和粗体字重选择  
- **多语种字体**：[EN] [CN] [JP] [KR] [SYM]标签分类显示
- **可调行间距**：多行文本的精确行距控制
- **12种字体颜色** + **13种背景颜色**预设
- **自动文本换行**和**实时进度显示**

### 核心参数

#### 必需参数
- **`images`**: 输入图像序列（来自视频节点）
- **`文本内容`**: 文本内容（支持多行）
- **`字体类型`**: 带语种标注的字体选择
  - `[EN] Liberation Sans`, `[EN] DejaVu Sans` - 英文无衬线字体
  - `[CN] WenQuanYi Zen Hei` - 中文字体
  - `[EN] Times New Roman` - 英文衬线字体
  - 更多字体自动检测显示...
- **`文本位置`**: 基于视频高度比例的响应式定位
  - `顶部偏上` - 距顶部3%高度（最靠近顶部）
  - `顶部居中` - 距顶部8%高度（合适的顶部位置）
  - `顶部偏下` - 距顶部15%高度（顶部区域下方）
  - `中央偏上` - 屏幕中央向上偏移5%
  - `屏幕中央` - 屏幕绝对中央
  - `中央偏下` - 屏幕中央向下偏移5%  
  - `底部偏上` - 距底部8%高度（底部区域上方）
  - `底部居中` - 距底部5%高度（标准底部，默认）
  - `底部偏下` - 距底部3%高度（最靠近底部）
- **`字体大小`**: 字体大小（12-72px，默认24）
- **`字体颜色`**: 字体颜色预设
  - `黑色`, `白色`, `红色`, `绿色`, `蓝色`, `黄色`
  - `青色`, `洋红`, `橙色`, `紫色`, `灰色`, `深灰`
- **`背景颜色`**: 背景颜色预设
  - `白色` - 白色背景（默认）
  - `黑色` - 黑色背景
  - `透明` - 无背景（透明）
  - `红色`, `绿色`, `蓝色`, `黄色`, `青色`, `洋红`
  - `橙色`, `紫色`, `灰色`, `浅灰`
- **`背景透明度`**: 背景透明度（0.0=完全透明，1.0=完全不透明，默认0.8）
- **`每行字符数`**: 每行最大字符数（10-100，默认30）

#### 可选参数
- **`启用背景`**: 是否启用文字背景（默认True）
- **`粗体字`**: 是否使用粗体字重（默认False）
- **`文本对齐`**: 文本水平对齐方式（居中/左对齐/右对齐，默认居中）
- **`启用阴影`**: 是否启用文字阴影效果（默认False）
- **`启用边框`**: 是否启用文字边框（默认False）
- **`水平边距`**: 文本左右边距（0-200px，默认50）
- **`行间距`**: 多行文本的行间距（0-20px，默认4）

### 🎯 比例定位系统优势

**响应式设计**: 
- 所有位置基于视频高度百分比计算
- 720p、1080p、4K下保持相同视觉效果
- 解决了固定像素在高分辨率下"文字太靠边"的问题

**示例对比**:
```
传统固定像素模式：
- 720p顶部居中: 60px (8.3%高度) ❌ 不一致
- 1080p顶部居中: 60px (5.6%高度) ❌ 不一致  
- 4K顶部居中: 60px (2.8%高度) ❌ 太靠顶部

新比例定位模式：  
- 720p顶部居中: 57.6px (8%高度) ✅ 视觉一致
- 1080p顶部居中: 86.4px (8%高度) ✅ 视觉一致
- 4K顶部居中: 172.8px (8%高度) ✅ 视觉一致
```

### 📋 使用示例

#### 🎬 经典字幕风格
```
文本内容: "这是视频字幕"
文本位置: 底部居中
字体类型: [EN] Liberation Sans  
字体颜色: 白色
背景颜色: 黑色
背景透明度: 0.8
```

#### 📺 新闻标题风格
```
文本内容: "重要新闻标题"
文本位置: 顶部居中
字体类型: [EN] DejaVu Sans
字体颜色: 黑色
背景颜色: 黄色
背景透明度: 0.9
粗体字: True
```

#### 🌟 无背景风格
```
文本内容: "简洁文本"
文本位置: 屏幕中央
字体类型: [EN] Liberation Sans
字体颜色: 白色
背景颜色: 透明
启用阴影: True
```

#### 💬 多行对话风格
```
文本内容: "这是第一行\n这是第二行\n这是第三行"
文本位置: 中央偏下
字体类型: [CN] WenQuanYi Zen Hei
行间距: 8
背景颜色: 白色
背景透明度: 0.9
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

### 🎨 快速样式模板

**🎬 电影字幕**
- 位置: `底部居中` | 字体: `[EN] Liberation Sans` | 颜色: `白色` | 背景: `黑色` | 透明度: 0.8

**📺 新闻标题** 
- 位置: `顶部居中` | 字体: `[EN] DejaVu Sans` | 颜色: `黑色` | 背景: `黄色` | 粗体: 是

**💭 对话气泡**
- 位置: `屏幕中央` | 字体: `[CN] WenQuanYi Zen Hei` | 颜色: `黑色` | 背景: `白色` | 行间距: 6

**🔥 警告提示**
- 位置: `中央偏上` | 字体: `[EN] Liberation Sans` | 颜色: `白色` | 背景: `红色` | 粗体: 是

**🌟 简约风格**
- 位置: `底部偏上` | 字体: `[EN] DejaVu Sans` | 颜色: `白色` | 背景: `透明` | 阴影: 是

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