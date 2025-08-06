# Whisper模型节点使用指南

## 🎯 节点架构概述

新的模块化设计将Whisper功能拆分为独立的节点，提供更灵活的工作流配置：

```
🤖 Whisper Model Loader → 🎙️ Whisper Transcribe
                      ↘
                        🎬 Video Subtitle (with Model)
```

## 📦 节点列表

### 1. 🤖 Whisper Model Loader (WhisperModelNode)
**功能**: 加载和缓存Whisper模型
- **输入**: 模型配置参数
- **输出**: 预加载的模型实例 + 模型信息
- **特点**: 全局缓存，避免重复加载

### 2. 🎙️ Whisper Transcribe (WhisperTranscribeNode)  
**功能**: 使用预加载模型进行音频转录
- **输入**: 预加载模型 + 音频文件路径
- **输出**: 转录文本 + 语言 + 置信度 + 段落信息
- **特点**: 纯转录功能，可复用模型

### 3. 🎬 Video Subtitle (with Model) (VideoSubtitleWithModelNode)
**功能**: 使用预加载模型生成视频字幕
- **输入**: 预加载模型 + 视频文件路径 + 样式配置
- **输出**: 带字幕视频 + 字幕文件 + 转录文本 + 处理日志
- **特点**: 完整的视频字幕生成流程

### 4. 🗂️ Whisper Cache Manager (WhisperCacheManagerNode)
**功能**: 管理模型缓存
- **输入**: 操作类型 (get_info/clear_cache)
- **输出**: 缓存信息
- **特点**: 监控和清理模型缓存

### 5. 🎬 Video Subtitle Generator (Legacy) (VideoSubtitleNode)
**功能**: 原始的一体化字幕生成节点
- **特点**: 保持向后兼容，内部管理模型加载

## 🔄 推荐工作流

### 基础工作流
```
[🤖 Whisper Model Loader] 
    ↓ (whisper_model)
[🎬 Video Subtitle (with Model)]
    ↓ (output_video_path, processing_log)
[ShowText] (显示结果)
```

### 高级工作流
```
[🤖 Whisper Model Loader] 
    ├─ (whisper_model) → [🎙️ Whisper Transcribe] → [ShowText]
    └─ (whisper_model) → [🎬 Video Subtitle (with Model)] → [ShowText]
```

### 批量处理工作流
```
[🤖 Whisper Model Loader] (一次加载)
    ├─ → [🎬 Video Subtitle 1] → [Video Output 1]
    ├─ → [🎬 Video Subtitle 2] → [Video Output 2]
    └─ → [🎬 Video Subtitle N] → [Video Output N]
```

## ⚙️ 详细参数说明

### Whisper Model Loader 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `model_size` | DROPDOWN | large-v3 | 模型大小，影响准确度和速度 |
| `device` | DROPDOWN | cuda | 计算设备，GPU加速需要CUDA |
| `compute_type` | DROPDOWN | float16 | 计算精度，影响内存使用 |
| `force_reload` | BOOLEAN | false | 强制重新加载，即使已缓存 |

**模型大小建议**:
- `tiny`: 最快，准确度较低，~39MB
- `small`: 平衡选择，~244MB  
- `medium`: 高准确度，~769MB
- `large-v3`: 最高准确度，~1550MB (推荐)

**计算类型说明**:
- `float16`: GPU推荐，节省内存
- `float32`: 最高精度，占用更多内存
- `int8`: CPU推荐，速度快但精度稍低

### Video Subtitle (with Model) 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `whisper_model` | WHISPER_MODEL | - | 来自模型加载节点 |
| `video_path` | STRING | "" | 输入视频文件路径 |
| `output_dir` | STRING | ./output | 输出目录 |
| `subtitle_style` | DROPDOWN | strong_shadow | 预设字幕样式 |
| `custom_font_size` | INT | 24 | 自定义字体大小 |
| `custom_position` | DROPDOWN | none | 自定义位置 |
| `font_color_r/g/b` | INT | 255 | RGB颜色值 |
| `enable_shadow` | BOOLEAN | true | 阴影开关 |
| `language_hint` | STRING | "" | 语言提示 |

## 🎨 字幕样式选项

| 样式名 | 特点 | 适用场景 |
|--------|------|----------|
| `default` | 标准白字黑边 | 通用场景 |
| `cinema` | 大字体强阴影 | 电影字幕 |
| `youtube` | 带背景色 | 在线视频 |
| `minimal` | 极简无阴影 | 简洁风格 |
| `top_news` | 顶部显示带背景 | 新闻字幕 |
| `strong_shadow` | 强阴影效果 | 突出显示 ⭐ |
| `dramatic_shadow` | 超强立体阴影 | 戏剧效果 ⭐ |

## 💡 最佳实践

### 1. 模型选择策略
```
测试阶段: small 模型 (快速验证)
    ↓
生产环境: large-v3 模型 (最佳质量)
```

### 2. 缓存管理
- 使用 `🗂️ Whisper Cache Manager` 监控缓存状态
- 处理大量视频时，保持模型缓存避免重复加载
- 内存不足时及时清理缓存

### 3. 批量处理优化
```python
# 推荐工作流
1. 加载一次模型 (🤖 Whisper Model Loader)
2. 并行处理多个视频 (多个 🎬 Video Subtitle 节点)
3. 统一输出管理
```

### 4. 错误处理
- 检查模型加载状态 (查看 model_info 输出)
- 验证视频文件路径存在
- 监控 GPU 内存使用情况
- 查看 processing_log 了解详细错误

## 🔧 故障排除

### 常见问题

**1. 模型加载失败**
```
原因: CUDA内存不足
解决: 使用较小模型或切换到CPU
```

**2. 转录质量差**
```
原因: 音频质量低或语言检测错误
解决: 使用language_hint指定语言
```

**3. 字幕位置不正确**
```
原因: 视频分辨率与预期不符
解决: 使用custom_position精确控制
```

**4. 处理速度慢**
```
原因: CPU模式或大模型
解决: 使用GPU加速 + 适当模型大小
```

## 🚀 性能对比

| 配置 | 模型加载时间 | 处理速度 | 内存占用 | 准确度 |
|------|------------|----------|----------|--------|
| tiny + CPU | ~2s | 很快 | ~1GB | 一般 |
| small + CUDA | ~3s | 快 | ~2GB | 良好 |
| medium + CUDA | ~5s | 中等 | ~5GB | 很好 |
| large-v3 + CUDA | ~8s | 较慢 | ~10GB | 最佳 |

## 📝 工作流示例

### 示例1: 单视频处理
```json
{
  "1": {"type": "WhisperModelNode", "widgets_values": ["large-v3", "cuda", "float16"]},
  "2": {"type": "VideoSubtitleWithModelNode", "inputs": [["1", 0]]}
}
```

### 示例2: 音频转录 + 视频字幕
```json
{
  "1": {"type": "WhisperModelNode"},
  "2": {"type": "WhisperTranscribeNode", "inputs": [["1", 0]]},
  "3": {"type": "VideoSubtitleWithModelNode", "inputs": [["1", 0]]}
}
```

## 🔄 版本更新

- **v1.0**: 基础功能
- **v1.1**: 添加模型缓存
- **v1.2**: 模块化设计 ⭐
- **v1.3**: 强阴影样式支持

## 📞 技术支持

遇到问题时请检查：
1. ComfyUI控制台日志
2. 节点输出的详细信息
3. GPU内存使用情况
4. 模型缓存状态