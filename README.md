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

### Command reference

- **Generate a complete episode (`example_generate_episode.py`)**:
  - Purpose: End-to-end demo with built-in characters and story; supports full mode (with simulation) and minimal mode (no simulation, faster).
  - Requirements: `OPENAI_API_KEY` in `.env` or environment; otherwise this script will print an error and exit.
  - Logs: `logs/episode_generation.log`; add `--debug` to also write `logs/debug.log`.
  - Output: JSON saved under `output/episodes/`. If the response includes a `screenplay` field, a screenplay `.txt` is also saved.
  - Usage examples:
```bash
# Full demo (with simulation)
python example_generate_episode.py --mode full

# Fast smoke test (skip simulation + debug logging)
python example_generate_episode.py --mode minimal --debug
```

- **Generate with custom parameters (`src/main.py`)**:
  - Purpose: Primary CLI to generate an episode with your own title, synopsis, themes, genre, tone, characters, and config.
  - Required: `--title` and `--synopsis`.
  - Optional:
    - `--themes <t1> <t2> ...` themes list, default `["drama","conflict","resolution"]`
    - `--genre {drama,comedy,thriller,sci-fi,mystery}` default `drama`
    - `--tone {light,balanced,dark,tense,comedic}` default `balanced`
    - `--simulation-hours <float>` hours to simulate, default `3.0`
    - `--characters-file <path>` JSON file of character definitions; if omitted, uses built-in test characters
    - `--config <path>` configuration file for overrides; NOTE: expects JSON for this CLI flag
    - `--output <path>` output file path, default `episode_output.json`
    - `--plot-pattern <str>` plot interweaving pattern, default `ABABCAB`
  - Model fallback: If `OPENAI_API_KEY` is missing, generation falls back to a basic structure without LLM (with a warning).
  - Usage examples:
```bash
# Your original example (uses built-in sample characters)
python src/main.py \
  --title "The Algorithm's Edge" \
  --synopsis "An AI becomes sentient" \
  --themes "consciousness" "ethics" \
  --genre sci-fi \
  --tone tense

# With custom characters and JSON config
python src/main.py \
  --title "My Episode" \
  --synopsis "..." \
  --themes "ai" "ethics" \
  --genre sci-fi \
  --tone tense \
  --characters-file /absolute/path/characters.json \
  --config /absolute/path/config.json \
  --output /absolute/path/out.json
```

  - Characters file (JSON) example:
```json
[
  {
    "name": "Alex Chen",
    "backstory": "Brilliant but conflicted tech founder",
    "personality": { "openness": 0.9, "conscientiousness": 0.7, "extraversion": 0.6, "agreeableness": 0.5, "neuroticism": 0.6 },
    "age": 32,
    "occupation": "CEO"
  }
]
```

- **Run agent simulation only (`src/simulation/run_simulation.py`)**:
  - Purpose: Run the multi-agent simulation independently of LLM generation; useful to inspect event distribution, tension curve, and narrative peaks.
  - Options:
    - `--agents <int>` number of agents to simulate (uses the first N of 5 built-in prototypes)
    - `--hours <float>` duration in hours
    - `--timestep <int>` minutes per timestep, default `15`
    - `--output <path>` output JSON, default `simulation_output.json`
  - Logs: `simulation.log`; console prints a summary and sample events.
  - Usage examples:
```bash
# 5 agents for 3 hours
python src/simulation/run_simulation.py --agents 5 --hours 3

# Custom timestep and output
python src/simulation/run_simulation.py --agents 3 --hours 1.5 --timestep 10 --output /absolute/path/sim.json
```

- **Test prompt chain (`src/llm/test_prompt_chain.py`)**:
  - Purpose: Debug and iterate on the LLM prompt chain by stage or end-to-end.
  - Options:
    - `--test {scene|outline|episode}` what to test; `scene` runs a single-scene chain, `outline` builds an episode outline, `episode` generates a mini-episode
    - `--stage {concept_generation|discriminative_refinement|dramatic_enhancement|dialogue_generation}` stage within the scene chain (only applies to `--test scene`)
    - `--num-scenes <int>` number of scenes when `--test episode` (default `3`)
  - Models: `scene`/`episode` default to GPT‑3.5; `outline` uses GPT‑4. Requires `OPENAI_API_KEY`.
  - Usage examples:
```bash
# End-to-end single-scene generation
python src/llm/test_prompt_chain.py --test scene

# Dialogue stage only
python src/llm/test_prompt_chain.py --test scene --stage dialogue_generation

# Mini-episode with 5 scenes
python src/llm/test_prompt_chain.py --test episode --num-scenes 5
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

### CLI config overrides (JSON for --config)

When using the CLI flag `--config` with `python src/main.py`, provide a JSON file. This overrides the internal defaults used by the orchestrator. Example:
```json
{
  "generation": {
    "llm_model": "gpt-4.1",
    "temperature": 0.7,
    "max_scenes": 14,
    "scene_duration_seconds": 90
  },
  "simulation": {
    "time_step_minutes": 15,
    "default_duration_hours": 3
  },
  "dramatic_operators": {
    "max_per_scene": 3,
    "min_tension": 0.3,
    "max_tension": 0.9
  },
  "output": {
    "format": "json",
    "include_metadata": true,
    "save_intermediate": true
  }
}
```

Notes:
- `generation.llm_model` determines the model: contains `"gpt-4.1"` → GPT‑4.1; contains `"gpt-4"` → GPT‑4; otherwise falls back to GPT‑3.5.
- `config/default_config.yaml` documents typical settings; the `--config` flag specifically expects JSON for the CLI.

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