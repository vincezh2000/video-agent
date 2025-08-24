# Video Generation Pipeline Documentation

## 概述

这是一个完整的端到端视频生成管道，将剧本JSON转换为带有AI生成角色、场景和语音的完整视频。系统使用fal.ai的多个模型实现高质量的视频生成。

## 系统架构

```
Episode JSON
    ↓
Script Extraction → 提取场景、角色、对话
    ↓
Visual Style Setting → 设置统一视觉风格
    ↓
Character Generation → 生成角色肖像 (Ideogram)
    ↓
Scene Generation → 生成场景背景 (Ideogram)
    ↓
Audio Generation → 生成对话语音 (ElevenLabs)
    ↓
Scene Composition → 角色场景合成 (Flux Kontekt Pro)
    ↓
Video Generation → 生成说话视频 (Stable Avatar)
    ↓
Video Assembly → 组装最终视频 (FFmpeg)
    ↓
Final Episode Video
```

## 核心组件

### 1. Script Extractor (`src/video/script_extractor.py`)

**功能**：从剧本JSON提取结构化数据

**主要类**：
- `SceneData`: 场景数据结构
- `CharacterProfile`: 角色档案
- `DialogueLine`: 对话行数据
- `ScriptExtractor`: 提取器主类

**提取内容**：
- 场景环境描述
- 角色信息和视觉描述
- 对话序列（包含情感、动作）
- 戏剧元素

### 2. Video Generator (`src/video/video_generator.py`)

**功能**：调用fal.ai模型生成视觉内容

**主要功能**：
- `generate_character_image()`: 生成角色肖像
- `generate_scene_background()`: 生成场景背景
- `composite_character_in_scene()`: 角色场景合成
- `generate_talking_video()`: 生成说话视频

**使用的AI模型**：
- **Ideogram V2**: 文本到图像生成
- **Flux Kontekt Pro**: 图像合成
- **Stable Avatar**: 说话头像视频生成

### 3. Episode Video Pipeline (`src/video/episode_video_pipeline.py`)

**功能**：协调整个视频生成流程

**主要步骤**：
1. 提取脚本数据
2. 设置视觉风格
3. 生成所有角色图像
4. 生成所有场景背景
5. 生成所有对话音频
6. 创建场景合成图
7. 生成说话视频片段
8. 组装最终视频

## 使用方法

### 环境设置

1. **安装依赖**：
```bash
pip install fal-client
pip install elevenlabs
pip install pillow
pip install aiohttp
pip install loguru
```

2. **设置API密钥**：
```bash
# 在.env文件中设置
FAL_API_KEY=your-fal-api-key
ELEVENLABS_API_KEY=your-elevenlabs-api-key
```

### 基本使用

```python
from src.video.episode_video_pipeline import generate_episode_video_from_json

# 生成视频
video_path = await generate_episode_video_from_json(
    json_path="output/latest_episode_mock.json",
    visual_style="tech_noir",  # 可选: cinematic, realistic, dramatic
    character_voices={
        "Alex Chen": "elon_musk",
        "Sam Rodriguez": "trump"
    }
)
```

### 命令行使用

```bash
# 完整视频生成
python generate_episode_video.py --mode full --style tech_noir

# 仅提取脚本
python generate_episode_video.py --mode extract

# 测试角色生成
python generate_episode_video.py --mode character
```

## 视觉风格预设

### 1. Cinematic（电影感）
- 电影级光照
- 景深效果
- 专业摄影构图

### 2. Realistic（写实）
- 照片级真实感
- 自然光照
- 高细节8K分辨率

### 3. Dramatic（戏剧性）
- 戏剧性光照
- 高对比度
- 情绪化氛围

### 4. Tech Noir（科技黑色）
- 赛博朋克美学
- 霓虹灯光
- 未来主义风格

## 生成流程详解

### Step 1: 脚本提取
```python
extractor = ScriptExtractor()
extracted_data = extractor.extract_from_json(episode_json)
```
- 解析JSON结构
- 提取场景、角色、对话
- 生成环境描述
- 估算时长

### Step 2: 角色生成
```python
# 为每个角色生成肖像
for character in characters:
    image = await generator.generate_character_image(
        character_name=character.name,
        character_prompt=character.visual_prompt
    )
```
- 使用Ideogram生成一致风格的角色
- 基于性格特征调整视觉呈现
- 保存为高质量PNG

### Step 3: 场景背景
```python
# 生成无人物的场景背景
background = await generator.generate_scene_background(
    scene_number=1,
    environment_prompt="modern tech lab, blue lighting"
)
```
- 生成环境背景
- 匹配剧本描述
- 保持风格一致性

### Step 4: 语音生成
```python
# 使用ElevenLabs生成角色语音
audio_manifest = await audio_renderer.render_full_episode(
    episode_data=episode_data,
    character_mapping=voice_mapping
)
```
- 名人语音合成
- 情感表达调整
- 时间轴同步

### Step 5: 场景合成
```python
# 将角色放入场景
composite = await generator.composite_character_in_scene(
    scene_number=1,
    character_name="Alex Chen"
)
```
- 使用Flux Kontekt Pro
- 自然光照融合
- 保持透视正确

### Step 6: 视频生成
```python
# 生成说话视频
video = await generator.generate_talking_video(
    character_name="Alex Chen",
    audio_path=audio_file,
    emotion="anxious"
)
```
- Stable Avatar驱动
- 口型同步
- 表情匹配情绪

### Step 7: 视频组装
```python
# FFmpeg组装最终视频
final_video = await pipeline._assemble_final_video(output_path)
```
- 按对话顺序拼接
- 生成字幕文件
- 导出MP4格式

## 输出结构

```
output/episode_videos/
├── [timestamp]/
│   ├── extraction.json          # 提取的脚本数据
│   ├── characters/              # 角色图像
│   │   ├── Alex_Chen.png
│   │   └── Sam_Rodriguez.png
│   ├── scenes/                  # 场景背景
│   │   ├── scene_001_bg.png
│   │   └── scene_002_bg.png
│   ├── composites/              # 合成图像
│   │   └── scene_001_Alex_Chen.png
│   ├── audio/                   # 音频文件
│   │   └── scene_001/
│   │       └── dialogue_001.mp3
│   ├── videos/                  # 视频片段
│   │   └── scene_001_Alex_Chen.mp4
│   ├── concat.txt               # FFmpeg拼接列表
│   ├── final_episode.mp4       # 最终视频
│   └── final_episode.srt       # 字幕文件
```

## 性能优化

### 并行处理
- 角色图像并行生成
- 场景背景并行生成
- 异步API调用

### 缓存机制
- 图像缓存避免重复生成
- 音频缓存复用
- 中间结果保存

### 资源管理
- 批量API调用
- 内存优化
- 临时文件清理

## 质量控制

### 视觉一致性
- 统一风格提示词
- 风格参考图像
- 色彩校正

### 音视频同步
- 精确时间戳
- 口型同步校准
- 字幕对齐

### 错误处理
- API失败重试
- 降级处理
- 部分失败恢复

## 常见问题

### 1. API限制
**问题**：fal.ai API调用限制
**解决**：实现速率限制和重试机制

### 2. 视频质量
**问题**：生成的视频质量不佳
**解决**：调整模型参数，使用更高质量设置

### 3. 角色一致性
**问题**：同一角色在不同场景中外观不一致
**解决**：使用固定的角色参考图像

### 4. 音频同步
**问题**：口型与音频不同步
**解决**：调整Stable Avatar参数，确保音频格式正确

## 扩展功能

### 计划中的功能
- [ ] 多角色同框支持
- [ ] 动态摄像机运动
- [ ] 背景音乐和音效
- [ ] 转场效果
- [ ] 实时预览
- [ ] 批量处理模式

### API替代方案
- **Replicate**: 替代fal.ai
- **Runway ML**: 高级视频编辑
- **D-ID**: 说话头像生成
- **Synthesia**: 虚拟演员

## 最佳实践

1. **预生成资产**：先生成所有静态资产（角色、背景），再生成动态内容
2. **质量vs速度**：根据需求平衡质量设置和生成时间
3. **错误恢复**：保存中间结果，支持断点续传
4. **资源管理**：及时清理临时文件，避免磁盘空间不足
5. **版本控制**：保存生成配置，便于重现结果

## 总结

这个视频生成管道实现了从剧本到视频的完全自动化，通过整合多个AI模型，生成具有一致视觉风格和高质量语音的对话视频。系统模块化设计便于扩展和维护，适合生成各种类型的剧集内容。