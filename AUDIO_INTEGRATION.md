# Audio Integration Guide

## Overview

The Showrunner Agents system now supports full audio generation for episodes, including celebrity voice synthesis using ElevenLabs API. This allows generated TV episodes to have fully voiced dialogue with character-specific voices, including celebrity impersonations.

## Features

### 1. Celebrity Voice Support
- **Pre-configured celebrities**: Elon Musk, Donald Trump, Joe Biden, Barack Obama
- **Custom voice profiles**: Create unique voices for any character
- **Text processing**: Automatic adjustment of speech patterns to match celebrity styles

### 2. Episode Audio Generation
- **Full episode rendering**: Generate audio for entire episodes automatically
- **Scene-by-scene processing**: Each scene rendered with appropriate voices
- **Emotion-based delivery**: Dialogue adjusted based on emotional context
- **Sound effects**: Automatic detection and insertion of sound effect markers

### 3. Character Voice Mapping
- **Automatic mapping**: Characters automatically assigned appropriate voices based on traits
- **Manual override**: Explicitly map characters to specific celebrity voices
- **Voice profiles**: Custom voice settings for non-celebrity characters

## Setup

### Prerequisites

1. Install required packages:
```bash
pip install elevenlabs>=0.2.0
pip install pydub>=0.25.0
```

2. Set up API keys in `.env`:
```bash
OPENAI_API_KEY=your-openai-api-key
ELEVENLABS_API_KEY=your-elevenlabs-api-key
```

## Usage

### Basic Episode Generation with Audio

```python
from src.main import ShowrunnerSystem

# Initialize system
system = ShowrunnerSystem()

# Generate episode with audio
episode = await system.generate_episode(
    title="Tech Titans Clash",
    synopsis="A heated debate about AI ethics",
    themes=["technology", "ethics"],
    genre="drama",
    tone="tense",
    characters=characters,
    generate_audio=True,  # Enable audio
    character_voice_mapping={
        "Alex Chen": "elon_musk",
        "Sam Rodriguez": "trump"
    }
)
```

### Direct Audio Rendering

```python
from src.rendering.episode_audio_renderer import EpisodeAudioRenderer

# Initialize renderer
renderer = EpisodeAudioRenderer()

# Map characters to voices
renderer.map_character_to_celebrity("Tech CEO", "elon_musk")
renderer.map_character_to_celebrity("Politician", "trump")

# Render episode audio
manifest = await renderer.render_full_episode(
    episode_data=episode,
    output_dir="output/audio/episodes"
)
```

### Celebrity Voice Generation

```python
from src.rendering.celebrity_voices import CelebrityVoiceGenerator

# Initialize generator
generator = CelebrityVoiceGenerator()

# Generate single voice
audio_path = generator.generate(
    celebrity="elon_musk",
    text="We need to make life multiplanetary",
    style="default"
)

# Generate conversation
conversation = [
    {"celebrity": "elon_musk", "text": "AI is crucial for humanity"},
    {"celebrity": "trump", "text": "We'll have the best AI, believe me"}
]
manifest = generator.generate_conversation(conversation)
```

## Demo Scripts

### 1. Full Episode with Audio
```bash
python demo_episode_with_audio.py --mode full
```
Generates a complete episode with celebrity voices for main characters.

### 2. Test Audio Only
```bash
python demo_episode_with_audio.py --mode audio-test
```
Tests audio generation with a sample scene.

### 3. Celebrity Conversation
```bash
python test_trump_elon_conversation.py
```
Generates a conversation between Trump and Elon Musk voices.

## Architecture

### Components

1. **EpisodeAudioRenderer** (`src/rendering/episode_audio_renderer.py`)
   - Main integration point for episode audio
   - Handles character-to-voice mapping
   - Manages full episode audio generation

2. **CelebrityVoiceGenerator** (`src/rendering/celebrity_voices.py`)
   - Celebrity voice synthesis
   - Text processing for speech patterns
   - Conversation generation

3. **AudioRenderer** (`src/rendering/audio_renderer.py`)
   - Base audio rendering functionality
   - Voice profile management
   - Sound effect integration

4. **VoiceProfiles** (`src/rendering/voice_profiles.py`)
   - Celebrity voice configurations
   - Text processors for speech patterns
   - Voice settings optimization

### Data Flow

```
Episode Generation
    ↓
Scene Extraction
    ↓
Character Voice Mapping
    ↓
Dialogue Processing
    ↓
Voice Synthesis (ElevenLabs API)
    ↓
Audio File Generation
    ↓
Timeline Creation
    ↓
Audio Manifest
```

## Configuration

### Voice Mapping Strategies

1. **Automatic Mapping**: Based on character occupation and personality
   - Tech leaders → Elon Musk voice
   - Politicians → Trump/Biden voice
   - Default characters → Generic voices

2. **Manual Mapping**: Explicit character-to-celebrity assignment
   ```python
   character_voice_mapping = {
       "Alex Chen": "elon_musk",
       "Sam Rodriguez": "trump",
       "Jordan Kim": "obama"
   }
   ```

3. **Custom Profiles**: Create unique voice characteristics
   ```python
   voice_profile = VoiceProfile(
       character_name="Sarah",
       voice_id="custom_voice_id",
       stability=0.7,
       style=0.3
   )
   ```

### Voice Settings

Each voice can be adjusted with:
- **Stability** (0-1): Voice consistency
- **Similarity Boost** (0-1): Match to original voice
- **Style** (0-1): Expression variation
- **Speaking Style**: default, excited, calm, confident

## Output Structure

```
output/
├── audio/
│   ├── episodes/
│   │   ├── [episode_id]/
│   │   │   ├── scene_001/
│   │   │   │   ├── dialogue_001_character.mp3
│   │   │   │   └── dialogue_002_character.mp3
│   │   │   ├── audio_manifest.json
│   │   │   └── timeline.json
│   │   └── ...
│   ├── celebrities/
│   │   └── [celebrity_name]/
│   │       └── cached_audio.mp3
│   └── conversation/
│       └── conv_[id]_001_celebrity.mp3
```

## Best Practices

1. **API Rate Limits**: Be mindful of ElevenLabs API limits
   - Use caching to avoid regenerating same dialogue
   - Batch process scenes when possible

2. **Voice Selection**: Match voices to character personalities
   - Authoritative characters → Lower stability, higher similarity
   - Emotional characters → Higher style variation

3. **Text Processing**: Enhance celebrity authenticity
   - Add speech patterns (um, uh for Elon)
   - Include catchphrases ("believe me" for Trump)
   - Adjust punctuation for emotion

4. **Performance**: Optimize for large episodes
   - Use async rendering for concurrent processing
   - Cache generated audio files
   - Implement progress callbacks for long episodes

## Troubleshooting

### Common Issues

1. **No Audio Generated**
   - Check ELEVENLABS_API_KEY is set
   - Verify API key has sufficient credits
   - Check network connectivity

2. **Voice Doesn't Match Character**
   - Review character_voice_mapping
   - Check voice profile settings
   - Verify celebrity name spelling

3. **Poor Audio Quality**
   - Adjust stability/similarity settings
   - Improve text preprocessing
   - Check input text for special characters

### Debug Mode

Enable detailed logging:
```python
from loguru import logger
logger.add("audio_debug.log", level="DEBUG")
```

## Future Enhancements

- [ ] Background music generation
- [ ] Advanced sound effects library
- [ ] Voice cloning from samples
- [ ] Real-time audio streaming
- [ ] Multi-language support
- [ ] Lip-sync data generation
- [ ] Audio post-processing effects