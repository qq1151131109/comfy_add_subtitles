# ComfyUI Video Subtitle Generator

🎬 一个功能完整的视频自动字幕生成ComfyUI节点集合

## 🚀 快速开始

### ComfyUI节点使用
1. 将整个项目复制到ComfyUI的`custom_nodes`目录
2. 重启ComfyUI
3. 在节点菜单中找到`Video/Subtitle`分类下的节点

### 命令行工具使用
```bash
# 基础使用
python main.py video.mp4

# 使用强阴影样式
python main.py video.mp4 --style strong_shadow

# 批量处理
python main.py ./videos --batch --style cinema
```

## 📦 节点列表

- 🤖 **Whisper Model Loader**: 模型加载和缓存管理
- 🎙️ **Whisper Transcribe**: 纯音频转录功能  
- 🎬 **Video Subtitle (with Model)**: 使用预加载模型的字幕生成
- 🗂️ **Whisper Cache Manager**: 缓存管理工具
- 🎬 **Video Subtitle Generator (Legacy)**: 原始一体化节点

## 📁 项目结构

```
├── core/           # 核心配置模块
├── services/       # 业务服务层
├── comfyui_nodes/  # ComfyUI节点
├── docs/          # 详细文档
├── examples/      # 工作流示例
└── tests/         # 测试文件
```

## 📖 详细文档

- [完整使用指南](docs/README.md)
- [ComfyUI安装说明](docs/ComfyUI_Installation.md) 
- [Whisper节点指南](docs/Whisper_Model_Nodes_Guide.md)
- [项目结构说明](docs/Project_Structure.md)

## ⚡ 特色功能

- ✅ 模块化设计，支持模型复用
- ✅ 强阴影字幕样式，突出显示效果
- ✅ GPU加速，处理速度快
- ✅ 多语言支持，识别准确度高
- ✅ 批量处理，效率更高

## 🛠️ 系统要求

- Python 3.8+
- FFmpeg
- 可选: NVIDIA GPU + CUDA

---

**版本**: v1.2.0 | **许可证**: MIT