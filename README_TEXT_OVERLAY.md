# 📝 Text Overlay Video 节点

## 概述

Text Overlay Video 节点是一个专门为ComfyUI设计的文本覆盖功能节点，可以为视频添加自定义文本覆盖。该节点支持多种文本样式和位置配置，满足不同场景的需求。

## 功能特点

- ✅ **丰富的位置选项**：9种预设位置（上、中、下 × 左、中、右）
- ✅ **完全自定义样式**：字体大小、颜色、背景、透明度等
- ✅ **多种文本效果**：阴影、边框、粗体等
- ✅ **覆盖整个视频**：文本默认从开始到结束显示
- ✅ **实时预览**：处理日志显示详细信息
- ✅ **高性能处理**：基于FFmpeg的高效视频处理

## 输入参数

### 必需参数

| 参数名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `images` | IMAGE | - | 输入图像序列（来自视频加载或处理节点） |
| `text_content` | STRING | "在这里输入文本内容" | 要显示的文本内容，支持多行 |
| `position` | 选择 | "bottom_center" | 文本位置（9个预设选项） |
| `font_size` | INT | 24 | 字体大小（12-72像素） |
| `font_color_r/g/b` | INT | 0,0,0 | 字体颜色RGB值（默认黑色） |
| `background_color_r/g/b` | INT | 255,255,255 | 背景颜色RGB值（默认白色） |
| `background_opacity` | FLOAT | 0.8 | 背景透明度（0-1） |

### 可选参数

| 参数名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `enable_background` | BOOLEAN | True | 是否启用文字背景 |
| `font_bold` | BOOLEAN | False | 是否使用粗体字 |
| `text_alignment` | 选择 | "center" | 文本对齐方式 |
| `enable_shadow` | BOOLEAN | False | 是否启用文字阴影 |
| `enable_border` | BOOLEAN | False | 是否启用文字边框 |
| `margin_x` | INT | 50 | 水平边距（0-200像素） |
| `margin_y` | INT | 50 | 垂直边距（0-200像素） |

## 位置选项

| 位置名称 | 说明 |
|----------|------|
| `bottom_center` | 底部居中（默认） |
| `bottom_left` | 底部左对齐 |
| `bottom_right` | 底部右对齐 |
| `top_center` | 顶部居中 |
| `top_left` | 顶部左对齐 |
| `top_right` | 顶部右对齐 |
| `center` | 屏幕中央 |
| `center_left` | 中央左对齐 |
| `center_right` | 中央右对齐 |

## 使用方法

### 1. 基本工作流

```
视频加载节点 → Text Overlay Video → 视频输出节点
```

### 2. 典型连接

1. 将 `VHS_LoadVideoPath` 或其他图像处理节点的 `IMAGE` 输出连接到本节点的 `images` 输入
2. 配置文本内容和样式参数
3. 将本节点的 `images` 输出连接到 `VHS_VideoCombine` 等视频输出节点

### 3. 配置示例

#### 电影字幕风格
```
text_content: "这是电影字幕"
position: "bottom_center"
font_size: 28
font_color: 白色 (255,255,255)
background_color: 黑色 (0,0,0)
background_opacity: 0.7
font_bold: True
```

#### 新闻标题风格
```
text_content: "重要新闻标题"
position: "top_center"
font_size: 24
font_color: 黑色 (0,0,0)
background_color: 黄色 (255,255,0)
background_opacity: 0.9
font_bold: True
```

## 注意事项

### 系统要求
- 需要安装FFmpeg（用于视频处理）
- Python 3.7+
- ComfyUI环境

### 性能优化
- 大视频文件处理可能需要较长时间
- 建议先用短视频测试参数配置
- 关闭不需要的效果可以提高处理速度

### 常见问题

**Q: 节点在ComfyUI中不显示？**
A: 检查custom_nodes目录结构，确认节点已注册，重启ComfyUI。

**Q: 文本位置不正确？**
A: 调整position参数和margin_x/y边距值。

**Q: 处理失败？**
A: 检查FFmpeg安装，查看processing_log输出的错误信息。

**Q: 文字看不清楚？**
A: 增加文字和背景的对比度，启用阴影或边框效果。

## 技术实现

- **核心服务**：`TextOverlayService` 处理视频文本覆盖逻辑
- **FFmpeg集成**：使用drawtext过滤器实现文本渲染
- **图像处理**：支持ComfyUI的图像张量格式
- **临时文件管理**：自动处理临时文件的创建和清理

## 更新日志

### v1.0.0
- ✅ 初始版本发布
- ✅ 支持9种预设位置
- ✅ 完整的样式配置选项
- ✅ ComfyUI节点集成
- ✅ FFmpeg后端处理

## 许可证

MIT License - 详见项目根目录LICENSE文件

## 支持与反馈

如果您在使用过程中遇到问题或有改进建议，请通过以下方式联系：

- 项目Issues
- 技术文档
- 示例代码：`examples/text_overlay_example.py`

---

**感谢使用Text Overlay Video节点！**
