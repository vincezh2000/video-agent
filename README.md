# Showrunner Agents System

An implementation of Fable Studio's Showrunner Agents for AI-driven TV episode generation through multi-agent simulation.

## Overview

This system generates complete 22-minute TV episodes by combining:
- Multi-agent simulation for creative content generation
- Advanced prompt-chaining for story development
- Dramatic operators for narrative enhancement
- Multi-modal output capabilities (text, voice synthesis ready)

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd video-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

1. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

2. Optional: Configure settings:
```bash
# Edit config/default_config.yaml for custom settings
```

### Basic Usage

```bash
# Generate a complete episode (recommended)
python example_generate_episode.py

# Generate episode with custom parameters
python src/main.py \
  --title "The Algorithm's Edge" \
  --synopsis "An AI becomes sentient" \
  --themes "consciousness" "ethics" \
  --genre sci-fi \
  --tone tense

# Run agent simulation only
python src/simulation/run_simulation.py --agents 5 --hours 3

# Test prompt chain
python src/llm/test_prompt_chain.py --test scene
```

## 🏗️ Architecture

The system follows a sophisticated pipeline architecture:

```
User Input → Agent Simulation → LLM Processing → Drama Enhancement → Scene Compilation → Multi-modal Output
```

### Core Components

| Component | Description | Status |
|-----------|-------------|--------|
| **Agent System** | Autonomous agents with Big Five personalities, memory, and goals | ✅ Complete |
| **Simulation Engine** | Multi-agent interactions generating creative context | ✅ Complete |
| **Prompt Chain** | 5-stage LLM processing with quality scoring | ✅ Complete |
| **Drama Engine** | 10+ dramatic operators (reversal, foreshadowing, etc.) | ✅ Complete |
| **Scene Compiler** | Formats scenes into screenplay and structured data | ✅ Complete |
| **Audio Renderer** | Voice synthesis integration (ElevenLabs ready) | 🔧 Basic |
| **Visual Renderer** | Camera and visual generation | 🚧 Planned |

## 📁 Project Structure

```
src/
├── agents/         # Character agents with personality models
├── simulation/     # Multi-agent simulation engine
├── llm/           # LLM client and prompt chains
├── drama/         # Dramatic operators and plot patterns
├── generation/    # Scene compilation and formatting
├── models/        # Data models (Pydantic)
├── rendering/     # Audio/visual output systems
├── utils/         # Helper functions
└── main.py        # Main orchestrator

config/
├── default_config.yaml    # System configuration
└── characters_template.json  # Character definitions

output/            # Generated episodes and artifacts
logs/             # System logs
```

## 🎬 Features

### Implemented
- ✅ **Multi-Agent Simulation**: Autonomous agents with personalities, memories, and goals
- ✅ **Prompt-Chain System**: Concept → Refinement → Drama → Dialogue → Coherence
- ✅ **Drama Operators**: Reversals, foreshadowing, callbacks, escalation, cliffhangers
- ✅ **Plot Pattern Management**: ABABCAB interweaving
- ✅ **Scene Compilation**: Screenplay formatting and structured output
- ✅ **Quality Metrics**: Character consistency, narrative coherence, dialogue naturalness
- ✅ **Configuration System**: YAML/JSON configs, environment variables

### In Progress
- 🔧 **Voice Synthesis**: ElevenLabs integration for character voices
- 🔧 **Sound Effects**: Automated sound effect placement

### Planned
- 🚧 **Visual Rendering**: Camera system and scene visualization
- 🚧 **SHOW-1 Integration**: Custom model training
- 🚧 **Real-time Generation**: Streaming episode creation

## 🧪 Testing

```bash
# Run all tests
pytest

# Specific modules
pytest tests/unit/test_agents.py
pytest tests/integration/

# With coverage
pytest --cov=src --cov-report=html
```

## 📊 Example Output

The system generates:
1. **Episode JSON**: Complete structured data with scenes, dialogue, and metadata
2. **Screenplay**: Industry-standard formatted script
3. **Statistics**: Character line distribution, tension curves, quality metrics
4. **Audio Timeline**: Voice synthesis timing (when configured)

Sample output structure:
```json
{
  "title": "The Algorithm's Edge",
  "synopsis": "...",
  "scenes": [
    {
      "scene_number": 1,
      "location": "Startup Office",
      "dialogue": [...],
      "dramatic_operators": ["foreshadowing", "escalation"],
      "tension_level": 0.7
    }
  ],
  "dramatic_arc": {
    "average_tension": 0.65,
    "peaks": 3,
    "has_climax": true
  }
}
```

## 🔧 Configuration

### Environment Variables (.env)
```bash
OPENAI_API_KEY=your_key_here
ELEVENLABS_API_KEY=optional_key
DEFAULT_MODEL=gpt-4
```

### Generation Settings (config/default_config.yaml)
```yaml
generation:
  max_scenes: 14
  scene_duration_seconds: 90
  target_episode_minutes: 22

dramatic_operators:
  max_per_scene: 3
  min_tension: 0.2
  max_tension: 0.95
```

## 📚 Documentation

- [System Architecture](SHOWRUNNER_SYSTEM_ARCHITECTURE.md) - Technical architecture details
- [Detailed Design](SHOWRUNNER_DETAILED_DESIGN.md) - Implementation specifications
- [Agent Design](SHOWRUNNER_AGENTS_DESIGN.md) - Multi-agent system design
- [API Reference](docs/api.md) - Module documentation

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## 📝 License

This project is for educational and research purposes.

## 🙏 Acknowledgments

Based on the groundbreaking research by Fable Studio:
- Paper: "To Infinity and Beyond: SHOW-1 and Showrunner Agents in Multi-Agent Simulations"
- Authors: Fable Studio Research Team

## 🚨 Current Limitations

- Requires OpenAI API key (GPT-4 recommended)
- Voice synthesis requires ElevenLabs API (optional)
- Visual rendering not yet implemented
- Episode generation takes 30-60 seconds depending on complexity