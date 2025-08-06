# 视频实时字幕添加工具

一个基于Whisper的本地视频自动字幕生成和嵌入工具，支持多种语言的语音识别和SRT字幕生成。

## 功能特性

- 🎥 **本地视频处理**: 支持多种视频格式 (MP4, AVI, MKV, MOV等)
- 🎵 **音频提取**: 自动从视频中提取音频进行处理
- 🗣️ **语音识别**: 基于OpenAI Whisper模型，支持多种语言
- 📝 **字幕生成**: 自动生成SRT格式字幕文件
- 🎬 **字幕嵌入**: 将字幕直接嵌入到视频中
- 📦 **批量处理**: 支持批量处理多个视频文件
- ⚡ **GPU加速**: 支持CUDA GPU加速处理

## 系统要求

- Python 3.8+
- FFmpeg (用于视频和音频处理)
- 可选: NVIDIA GPU + CUDA (用于加速)

## 安装

### 1. 安装FFmpeg

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**CentOS/RHEL:**
```bash
sudo yum install epel-release
sudo yum install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
下载FFmpeg并添加到系统PATH环境变量

### 2. 安装Python依赖

```bash
pip install -r requirements.txt
```

### 3. 安装GPU支持 (可选)

如果您有NVIDIA GPU，可以安装CUDA版本的PyTorch以获得更快的处理速度：

```bash
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118
```

## 使用方法

### 命令行使用

#### 处理单个视频文件

```bash
python main.py video.mp4
```

#### 指定输出目录

```bash
python main.py video.mp4 -o /path/to/output
```

#### 选择Whisper模型

```bash
python main.py video.mp4 -m large-v3
```

可选模型: `tiny`, `base`, `small`, `medium`, `large`, `large-v2`, `large-v3`

#### 指定计算设备

```bash
# 使用GPU (默认)
python main.py video.mp4 -d cuda

# 使用CPU
python main.py video.mp4 -d cpu
```

#### 字幕样式配置

##### 使用预设样式

```bash
# 默认样式
python main.py video.mp4 --style default

# 电影院样式 (大字体，强阴影)
python main.py video.mp4 --style cinema

# YouTube样式 (带背景)
python main.py video.mp4 --style youtube

# 极简样式 (无阴影)
python main.py video.mp4 --style minimal

# 新闻样式 (顶部显示)
python main.py video.mp4 --style top_news

# 强阴影样式 (类似图片效果)
python main.py video.mp4 --style strong_shadow

# 戏剧化阴影样式 (超强阴影效果)
python main.py video.mp4 --style dramatic_shadow
```

##### 自定义字幕样式

```bash
# 设置字幕位置
python main.py video.mp4 --position top_center

# 设置字体大小
python main.py video.mp4 --font-size 28

# 设置字体颜色 (RGB格式)
python main.py video.mp4 --font-color "255,255,0"  # 黄色

# 启用/禁用阴影
python main.py video.mp4 --shadow
python main.py video.mp4 --no-shadow

# 组合使用
python main.py video.mp4 --position bottom_center --font-size 24 --font-color "255,255,255" --shadow
```

##### 字幕位置选项

- `bottom_center` - 底部居中 (默认)
- `bottom_left` - 底部左对齐  
- `bottom_right` - 底部右对齐
- `top_center` - 顶部居中
- `top_left` - 顶部左对齐
- `top_right` - 顶部右对齐
- `center` - 屏幕中央

#### 批量处理

```bash
# 处理目录中的所有视频
python main.py /path/to/video/directory --batch -o /path/to/output
```

### 完整示例

```bash
# 使用large-v3模型，GPU加速，处理单个视频
python main.py test.mp4 -m large-v3 -d cuda -o ./output

# 批量处理视频目录
python main.py ./videos --batch -m medium -o ./output_with_subtitles

# 使用电影院样式处理视频
python main.py movie.mp4 --style cinema -o ./output

# 自定义字幕样式：顶部显示，大字体，黄色，带阴影
python main.py video.mp4 --position top_center --font-size 32 --font-color "255,255,0" --shadow

# 批量处理，使用YouTube样式
python main.py ./videos --batch --style youtube -o ./output

# 使用强阴影效果，类似图片中的效果
python main.py video.mp4 --style strong_shadow -o ./output_shadow

# 使用戏剧化阴影效果，超强立体感
python main.py video.mp4 --style dramatic_shadow -o ./output_dramatic
```

## 输出文件

处理完成后，将生成以下文件：

- `原文件名.srt` - SRT格式字幕文件
- `原文件名_with_subtitles.mp4` - 嵌入字幕的视频文件

## 支持的语言

工具支持Whisper模型识别的100+种语言，包括但不限于：

- 中文 (zh)
- 英语 (en) 
- 日语 (ja)
- 韩语 (ko)
- 西班牙语 (es)
- 法语 (fr)
- 德语 (de)
- 俄语 (ru)
- 阿拉伯语 (ar)
- 更多...

## 模型选择建议

| 模型 | 大小 | 内存需求 | 处理速度 | 准确度 |
|------|------|----------|----------|--------|
| tiny | 39MB | ~1GB | 最快 | 较低 |
| base | 74MB | ~1GB | 快 | 一般 |
| small | 244MB | ~2GB | 中等 | 良好 |
| medium | 769MB | ~5GB | 较慢 | 很好 |
| large | 1550MB | ~10GB | 慢 | 最佳 |
| large-v2 | 1550MB | ~10GB | 慢 | 最佳 |
| large-v3 | 1550MB | ~10GB | 慢 | 最佳 |

建议：
- 快速测试: `base` 或 `small`
- 生产使用: `large-v3` (最新且最准确)
- 资源受限: `tiny` 或 `base`

## 性能优化

1. **使用GPU**: 如果有NVIDIA GPU，使用 `-d cuda` 可以显著提升处理速度
2. **选择合适模型**: 根据准确度和速度需求选择模型大小
3. **批量处理**: 使用 `--batch` 模式处理多个文件更高效

## 故障排除

### 常见问题

1. **FFmpeg未找到**
   - 确保FFmpeg已正确安装并在PATH中
   - 运行 `ffmpeg -version` 验证安装

2. **CUDA内存不足**
   - 使用较小的模型 (如 `medium` 或 `small`)
   - 或切换到CPU模式 `-d cpu`

3. **音频提取失败**
   - 检查视频文件是否损坏
   - 确保视频格式受支持

4. **字幕识别不准确**
   - 尝试使用更大的模型 (`large-v3`)
   - 确保音频质量良好

### 日志文件

程序运行时会生成 `subtitle_generator.log` 日志文件，包含详细的处理信息和错误信息。

## 代码结构

```
add_subtitles/
├── __init__.py              # 模块初始化
├── main.py                  # 主程序入口
├── audio_service.py         # 音频处理服务
├── video_service.py         # 视频处理服务
├── whisper_service.py       # Whisper语音识别服务
├── subtitle_service.py      # 字幕生成服务
├── config.py               # 配置文件
├── requirements.txt        # Python依赖
└── README.md              # 说明文档
```

## 🎛️ ComfyUI节点使用

本项目已封装为ComfyUI自定义节点，支持在ComfyUI工作流中使用。

### 安装ComfyUI节点

1. 将整个项目文件夹复制到ComfyUI的`custom_nodes`目录
2. 重启ComfyUI
3. 在节点菜单中找到`Video/Subtitle` → `🎬 Video Subtitle Generator`

### 节点参数

**必需参数**：
- `video_path`: 输入视频文件路径
- `output_dir`: 输出目录
- `whisper_model`: 模型大小 (推荐large-v3)
- `device`: cuda/cpu
- `subtitle_style`: 预设样式

**可选参数**：
- `custom_font_size`: 自定义字体大小
- `custom_position`: 自定义位置
- `font_color_r/g/b`: RGB颜色值
- `enable_shadow`: 是否启用阴影

### 节点输出

- `output_video_path`: 生成的带字幕视频路径
- `subtitle_file_path`: SRT字幕文件路径  
- `processing_log`: 处理日志

### 工作流示例

参考`workflow_example.json`文件，展示了如何在ComfyUI中使用字幕生成节点。

## 许可证

本项目基于MIT许可证开源。

## 贡献

欢迎提交Issue和Pull Request来改进这个工具！