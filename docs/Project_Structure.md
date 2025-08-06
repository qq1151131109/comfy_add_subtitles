# 项目结构说明

## 📁 目录结构

```
comfyui-video-subtitle/
├── 📁 core/                          # 核心模块
│   ├── __init__.py
│   └── subtitle_style.py             # 字幕样式配置
│
├── 📁 services/                      # 服务层
│   ├── __init__.py
│   ├── audio_service.py              # 音频处理服务
│   ├── video_service.py              # 视频处理服务
│   ├── whisper_service.py            # Whisper语音识别服务
│   └── subtitle_service.py           # 字幕生成服务
│
├── 📁 comfyui_nodes/                 # ComfyUI节点
│   ├── __init__.py                   # 节点注册和导出
│   ├── comfyui_subtitle_node.py      # 原始一体化节点（兼容性）
│   ├── whisper_model_node.py         # Whisper模型管理节点
│   └── video_subtitle_with_model_node.py  # 使用预加载模型的字幕节点
│
├── 📁 docs/                          # 文档
│   ├── README.md                     # 项目主文档
│   ├── ComfyUI_Installation.md       # ComfyUI安装指南
│   ├── Whisper_Model_Nodes_Guide.md  # Whisper节点使用指南
│   └── Project_Structure.md          # 项目结构说明（本文件）
│
├── 📁 examples/                      # 示例和模板
│   ├── __init__.py
│   └── workflow_with_model_example.json  # 工作流示例
│
├── 📁 tests/                         # 测试文件（预留）
│   └── __init__.py
│
├── 📄 __init__.py                    # 包初始化和ComfyUI节点导出
├── 📄 main.py                        # 命令行工具主程序
├── 📄 config.py                      # 全局配置
└── 📄 requirements.txt               # 项目依赖
```

## 🏗️ 架构设计

### 分层架构

```
┌─────────────────────────────────────┐
│           ComfyUI Nodes             │  ← UI层：ComfyUI节点接口
├─────────────────────────────────────┤
│          Main Application           │  ← 应用层：命令行工具
├─────────────────────────────────────┤
│            Services                 │  ← 服务层：业务逻辑
├─────────────────────────────────────┤
│             Core                    │  ← 核心层：基础配置和数据结构
└─────────────────────────────────────┘
```

### 模块职责

#### 🎯 Core 核心模块
- **subtitle_style.py**: 字幕样式配置、预设样式、位置枚举等

#### 🔧 Services 服务层
- **audio_service.py**: 音频提取、验证、信息获取
- **video_service.py**: 视频处理、字幕嵌入、信息获取
- **whisper_service.py**: Whisper模型管理、语音识别
- **subtitle_service.py**: SRT字幕生成、验证、信息获取

#### 🎛️ ComfyUI Nodes 节点层
- **whisper_model_node.py**: 
  - WhisperModelNode: 模型加载和缓存
  - WhisperTranscribeNode: 音频转录
  - WhisperCacheManagerNode: 缓存管理
- **video_subtitle_with_model_node.py**: 
  - VideoSubtitleWithModelNode: 使用预加载模型的字幕生成
- **comfyui_subtitle_node.py**: 
  - VideoSubtitleNode: 原始一体化节点（向下兼容）

## 🔄 数据流

### 模块化工作流
```
[🤖 Whisper Model Loader] 
    ↓ (WhisperService实例)
[🎬 Video Subtitle (with Model)]
    ↓ (处理结果)
[输出节点]
```

### 服务层调用关系
```
VideoService ←→ SubtitleService
     ↓              ↓
AudioService → WhisperService
     ↓              ↓
   FFmpeg      Whisper Model
```

## 📦 包导入策略

### 相对导入（包内使用）
```python
# 在services/video_service.py中
from ..core.subtitle_style import SubtitleStyle

# 在comfyui_nodes/__init__.py中  
from .whisper_model_node import WhisperModelNode
```

### 兼容性导入（独立运行）
```python
# 支持多种导入方式
try:
    from ..services.audio_service import AudioService
except ImportError:
    try:
        from services.audio_service import AudioService
    except ImportError:
        from audio_service import AudioService
```

## 🚀 部署方式

### 1. ComfyUI自定义节点部署
```bash
# 复制整个项目到ComfyUI的custom_nodes目录
cp -r comfyui-video-subtitle /path/to/ComfyUI/custom_nodes/
```

### 2. 独立命令行工具使用
```bash
# 直接运行main.py
python main.py video.mp4 --style strong_shadow
```

### 3. Python包导入使用
```python
# 作为包导入使用
from comfyui_video_subtitle import VideoService, SubtitleStyle
```

## 🔧 扩展指南

### 添加新的字幕样式
1. 在 `core/subtitle_style.py` 中的 `PresetStyles` 类添加新方法
2. 在相关节点的样式选择列表中添加新选项

### 添加新的服务
1. 在 `services/` 目录创建新的服务文件
2. 在 `services/__init__.py` 中导出新服务
3. 在需要的地方导入和使用

### 添加新的ComfyUI节点
1. 在 `comfyui_nodes/` 目录创建新节点文件
2. 在 `comfyui_nodes/__init__.py` 中注册新节点
3. 更新文档和示例

## 📝 开发规范

### 文件命名
- 使用小写字母和下划线：`audio_service.py`
- 类名使用大驼峰：`AudioService`
- 常量使用大写字母：`AUDIO_FORMAT`

### 导入顺序
1. 标准库导入
2. 第三方库导入  
3. 项目内部导入

### 文档字符串
- 所有公共类和方法都需要文档字符串
- 使用Google风格的文档字符串

## 🧪 测试策略

### 单元测试
- 每个服务类都应有对应的测试文件
- 测试文件放在 `tests/` 目录下

### 集成测试
- ComfyUI节点的端到端测试
- 工作流测试

### 性能测试
- 大文件处理性能测试
- 内存使用监控

## 📈 版本管理

### 语义化版本
- 主版本号：不兼容的API修改
- 次版本号：向下兼容的功能性新增
- 修订号：向下兼容的问题修正

### 更新日志
- 在项目根目录维护 `CHANGELOG.md`
- 记录每个版本的重要变更