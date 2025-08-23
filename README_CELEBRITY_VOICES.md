# Celebrity Voice Generation with ElevenLabs

这个组件提供了使用ElevenLabs生成名人声音的功能，特别优化了Elon Musk和Trump的声音模拟。

## 功能特性

- 🎭 **多名人支持**: Elon Musk, Trump, Biden, Obama
- 🎨 **多种风格**: default, excited, calm, confident
- 🔄 **声音轮换**: 多个Voice ID轮换使用，增加变化
- 💬 **对话生成**: 支持多名人对话生成
- 📦 **批量处理**: 一次生成多个音频文件
- 🧠 **智能文本处理**: 模拟各名人的说话习惯
- 💾 **缓存机制**: 避免重复生成相同内容

## 安装要求

```bash
pip install elevenlabs loguru
```

## 环境配置

设置ElevenLabs API密钥：

```bash
export ELEVENLABS_API_KEY="your-elevenlabs-api-key"
```

## 基础使用

### 1. 简单生成

```python
from src.rendering.celebrity_voices import CelebrityVoiceGenerator

# 初始化生成器
generator = CelebrityVoiceGenerator()

# 生成Elon Musk的声音
elon_audio = generator.generate(
    celebrity="elon_musk",
    text="Mars colonization is the key to humanity's future.",
    style="excited"
)

# 生成Trump的声音
trump_audio = generator.generate(
    celebrity="trump", 
    text="This is going to be tremendous, believe me.",
    style="confident"
)
```

### 2. 便捷函数

```python
from src.rendering.celebrity_voices import generate_elon_voice, generate_trump_voice

# 快速生成
elon_path = generate_elon_voice("AI safety is critically important.")
trump_path = generate_trump_voice("America will lead in AI technology.")
```

### 3. 生成对话

```python
conversation = [
    {"celebrity": "elon_musk", "text": "We should colonize Mars.", "style": "excited"},
    {"celebrity": "trump", "text": "Space Force will make it happen!", "style": "confident"}
]

manifest = generator.generate_conversation(conversation, "output/mars_debate")
```

## 高级功能

### 批量生成

```python
batch_configs = [
    {"celebrity": "elon_musk", "text": "Tesla is the future.", "filename": "elon_tesla.mp3"},
    {"celebrity": "trump", "text": "America first!", "filename": "trump_america.mp3"}
]

results = generator.generate_batch(batch_configs, "output/batch")
```

### 不同说话风格

支持的风格：
- `default`: 默认说话风格
- `excited`: 兴奋/激动
- `calm`: 冷静/沉稳  
- `confident`: 自信/坚定

```python
# 同样的文本，不同风格
text = "Artificial intelligence will change everything."

for style in ["default", "excited", "calm", "confident"]:
    audio = generator.generate("elon_musk", text, style)
```

### 声音ID轮换

```python
# 启用轮换，每次使用不同的Voice ID
audio = generator.generate(
    celebrity="elon_musk", 
    text="Test voice rotation",
    use_rotation=True
)
```

## 支持的名人

### Elon Musk
- **Voice IDs**: pNInz6obpgDQGcFmaJgB (主), ErXwobaYiN019PkySvjV, VR6AewLTigWG4xSOukaG
- **说话特点**: 添加"um"停顿，强调技术词汇
- **优化词汇**: AI, Mars, Tesla, SpaceX, neural, sustainable

### Donald Trump  
- **Voice IDs**: VR6AewLTigWG4xSOukaG (主), 2EiwWnXFnvU5JabPnv8n, onwK4e9ZLuTAKqWW03F9
- **说话特点**: 使用上级词汇，添加口头禅
- **优化词汇**: tremendous, fantastic, believe me, incredible

### Joe Biden
- **Voice IDs**: AZnzlk1XvdvUeBnXmlld (主), EXAVITQu4vr4xnSDxMaL  
- **说话特点**: 使用"folks", "come on", "here's the deal"

### Barack Obama
- **Voice IDs**: 29vD33N1CtxCmqQRPOHJ (主), 21m00Tcm4TlvDq8ikWAM
- **说话特点**: 使用"let me be clear", 停顿明显

## 文件结构

```
src/rendering/
├── celebrity_voices.py      # 主要生成器
├── voice_profiles.py        # 声音配置和文本处理
└── audio_renderer.py        # 基础音频渲染器

examples/
├── examples_celebrity_voices.py  # 使用示例
└── test_celebrity_voices.py      # 测试脚本
```

## 测试和示例

### 运行测试

```bash
python test_celebrity_voices.py
```

### 运行示例

```bash  
python examples_celebrity_voices.py
```

## API参考

### CelebrityVoiceGenerator

#### 主要方法

```python
def generate(celebrity, text, style="default", output_path=None, use_rotation=True)
```
生成单个名人声音

```python  
def generate_batch(texts, output_dir="output/audio/batch")
```
批量生成多个声音

```python
def generate_conversation(conversation, output_dir="output/audio/conversation")  
```
生成名人对话

```python
async def generate_async(celebrity, text, style="default", output_path=None, use_rotation=True)
```
异步生成声音

#### 辅助方法

```python
def list_available_celebrities()  # 列出可用名人
def get_celebrity_info(celebrity)  # 获取名人详细信息  
def clear_cache()  # 清空缓存
```

### 便捷函数

```python
generate_elon_voice(text, output_path=None, style="default")
generate_trump_voice(text, output_path=None, style="default") 
quick_conversation(elon_text, trump_text, output_dir="output/conversation")
```

## 输出格式

生成的音频文件为MP3格式，保存在指定目录：

```
output/
├── audio/
│   ├── celebrities/
│   │   ├── elon_musk/
│   │   └── trump/
│   ├── conversation/
│   └── batch/
```

## 注意事项

1. **API限制**: ElevenLabs有API调用限制，请根据您的套餐合理使用
2. **声音质量**: Voice ID的选择会影响最终效果，可以尝试不同的ID
3. **文本长度**: 建议单次生成的文本不超过500字符
4. **缓存**: 开启缓存可以避免重复生成相同内容
5. **文件大小**: 生成的MP3文件大小通常在100KB-1MB之间

## 错误处理

常见错误及解决方案：

- **API Key错误**: 检查ELEVENLABS_API_KEY环境变量
- **Voice ID无效**: 使用voice_profiles.py中预设的ID  
- **文本太长**: 将长文本分段处理
- **网络错误**: 检查网络连接和ElevenLabs服务状态

## 扩展新名人

在`voice_profiles.py`中添加新的CelebrityProfile：

```python
"new_celebrity": CelebrityProfile(
    name="new_celebrity",
    display_name="New Celebrity", 
    voice_ids=["voice_id_1", "voice_id_2"],
    primary_voice_id="voice_id_1",
    voice_settings=VoiceSettings(...),
    text_processor=process_new_celebrity_text
)
```