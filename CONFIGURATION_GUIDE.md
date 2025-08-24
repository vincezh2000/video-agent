# Configuration Guide

## Quick Start

### 1. Copy Environment Template
```bash
cp .env.example .env
```

### 2. Add Your API Keys

Edit `.env` and add your API keys:

```bash
# Required for episode generation
OPENAI_API_KEY=your-openai-api-key

# Optional for voice synthesis
ELEVENLABS_API_KEY=your-elevenlabs-api-key

# Optional for video generation (use FAL_KEY)
FAL_KEY=your-fal-key
```

### 3. Check Configuration
```bash
python check_config.py
```

## API Keys

### OpenAI (Required)
- **Purpose**: Episode script generation
- **Get Key**: https://platform.openai.com/api-keys
- **Environment Variable**: `OPENAI_API_KEY`
- **Cost**: ~$0.01-0.10 per episode

### ElevenLabs (Optional)
- **Purpose**: Celebrity voice synthesis
- **Get Key**: https://elevenlabs.io
- **Environment Variable**: `ELEVENLABS_API_KEY`
- **Cost**: ~$0.05-0.20 per episode

### fal.ai (Optional)
- **Purpose**: AI video generation
- **Get Key**: https://fal.ai/dashboard
- **Environment Variables**: 
  - `FAL_KEY` (recommended, official)
  - `FAL_API_KEY` (alternative, also supported)
- **Cost**: ~$0.50-2.00 per episode

## Environment Variables

### Primary Configuration (.env)

```bash
# Core API Keys
OPENAI_API_KEY=sk-proj-...
ELEVENLABS_API_KEY=sk_...
FAL_KEY=fal_...

# Model Configuration
DEFAULT_MODEL=gpt-4.1
FALLBACK_MODEL=gpt-3.5-turbo

# Simulation Settings
DEFAULT_SIMULATION_HOURS=3
DEFAULT_TIME_STEP_MINUTES=15

# Output Configuration
OUTPUT_DIRECTORY=output
SAVE_INTERMEDIATE_FILES=true

# Logging
LOG_LEVEL=INFO
LOG_FILE=showrunner.log
```

### fal.ai Specific Configuration

The system supports both environment variable names for fal.ai:

1. **FAL_KEY** (Recommended)
   - Official environment variable name used by fal.ai
   - Takes priority if both are set
   
2. **FAL_API_KEY** (Alternative)
   - Alternative name for compatibility
   - Used as fallback if FAL_KEY is not set

The code automatically tries both:
```python
fal_key = os.getenv("FAL_KEY") or os.getenv("FAL_API_KEY")
```

## Installation

### 1. Python Dependencies

```bash
# Core dependencies
pip install openai loguru pydantic python-dotenv

# Audio generation
pip install elevenlabs pydub

# Video generation
pip install fal-client pillow aiohttp

# Full installation
pip install -r requirements.txt
```

### 2. System Dependencies

#### FFmpeg (Required for video assembly)

**macOS:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

**Windows:**
Download from https://ffmpeg.org/download.html

## Testing Your Setup

### 1. Check All Configurations
```bash
python check_config.py
```

### 2. Test Individual Components

#### Test Episode Generation (OpenAI only)
```bash
python example_generate_episode.py --mode minimal
```

#### Test Voice Synthesis (ElevenLabs)
```bash
python test_celebrity_voices.py
```

#### Test Video Generation (fal.ai)
```bash
python test_fal_api.py --test all
```

## Feature Availability

| Feature | Required APIs | Status |
|---------|--------------|--------|
| Script Generation | OpenAI | Required |
| Voice Synthesis | ElevenLabs | Optional |
| Video Generation | fal.ai | Optional |
| Full Multimedia | All three | Optional |

## Troubleshooting

### API Key Not Working

1. **Check Format**:
   - OpenAI: Should start with `sk-proj-` or `sk-`
   - ElevenLabs: Should start with `sk_`
   - fal.ai: Various formats, check dashboard

2. **Check Environment**:
   ```bash
   # Verify environment variables are loaded
   python -c "import os; print('FAL_KEY:', os.getenv('FAL_KEY', 'Not set'))"
   ```

3. **Check .env Location**:
   - Must be in project root directory
   - File must be named `.env` (not `.env.txt`)

### fal.ai Specific Issues

1. **API Key Not Found**:
   ```bash
   # Try setting both variables
   export FAL_KEY="your-key"
   export FAL_API_KEY="your-key"
   ```

2. **Rate Limiting**:
   - Free tier has limits
   - Implement delays between requests
   - Cache generated content

3. **Model Availability**:
   - Some models require paid plans
   - Check https://fal.ai/pricing

### Missing Dependencies

```bash
# Check what's missing
python check_config.py

# Install all at once
pip install -r requirements.txt

# Or install individually
pip install fal-client
pip install elevenlabs
```

## Cost Optimization

### Minimize API Calls
- Use caching for repeated content
- Generate in batches when possible
- Use lower quality settings for testing

### Quality Settings
- **Testing**: Use TURBO/draft modes
- **Preview**: Use BALANCED/standard modes  
- **Production**: Use QUALITY/high modes

### Free Alternatives
- **Voice**: Use pyttsx3 or gTTS instead of ElevenLabs
- **Images**: Use local Stable Diffusion instead of fal.ai
- **Video**: Use static images with audio overlay

## Security Best Practices

1. **Never commit API keys**:
   - Add `.env` to `.gitignore`
   - Use `.env.example` as template

2. **Rotate keys regularly**:
   - Change API keys monthly
   - Revoke unused keys

3. **Use environment-specific keys**:
   - Development keys for testing
   - Production keys for deployment

4. **Monitor usage**:
   - Check API dashboards regularly
   - Set up billing alerts

## Support

- **OpenAI**: https://platform.openai.com/docs
- **ElevenLabs**: https://docs.elevenlabs.io
- **fal.ai**: https://docs.fal.ai
- **Project Issues**: Create issue on GitHub