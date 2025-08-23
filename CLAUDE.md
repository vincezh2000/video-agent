# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Showrunner Agents system implementation based on Fable Studio's research paper "To Infinity and Beyond: SHOW-1 and Showrunner Agents in Multi-Agent Simulations". The system generates full TV episodes (22 minutes) through multi-agent simulation and AI-driven content generation.

## System Architecture

The project follows a complex pipeline architecture:
```
User Input → Agent Simulation → Data Collection → LLM Processing → Scene Generation → Multi-modal Output
```

### Core Components

1. **Multi-Agent Simulation**: Autonomous agents with personalities, backstories, and decision-making capabilities that generate "creative fuel" for story generation
2. **Prompt-Chain System**: Multi-step LLM processing that simulates discontinuous creative thinking
3. **Drama Enhancement**: Procedural injection of dramatic operators (reversals, foreshadowing, cliffhangers)
4. **Multi-modal Generation**: Integrated voice synthesis, visual rendering, and camera systems

### Key Design Patterns

- **Prompt-Chaining**: Sequential LLM calls where each step acts as discriminator for the previous
- **Plot Patterns**: Storyline interweaving (e.g., ABABC pattern for alternating between character groups)
- **Dramatic Fingerprints**: IP-specific style characteristics for training SHOW-1 model
- **Reverie System**: Agent reflection mechanism for memory consolidation and pattern recognition

## Development Setup

### Python Implementation (Recommended)
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Core dependencies for initial development
pip install openai  # For GPT-4/GPT-3.5 integration
pip install asyncio  # For concurrent processing
pip install pydantic  # For data models
pip install numpy    # For simulation calculations

# Additional dependencies for full implementation
pip install elevenlabs  # For voice synthesis
pip install pygame      # For basic rendering/playback
```

### Running the System
```bash
# Main episode generation (once implemented)
python src/main.py --episode-title "Your Episode Title" --simulation-hours 3

# Running agent simulation only
python src/simulation/run_simulation.py --agents 10 --timesteps 1000

# Testing prompt chains
python src/llm/test_prompt_chain.py --stage concept_generation
```

## Implementation Priority

Follow this order when implementing:

1. **Phase 1**: LLM Integration & Prompt-Chain (start here)
   - Focus on `src/llm/prompt_chain.py` and prompt templates
   - Implement basic scene generation without agents

2. **Phase 2**: Agent System
   - Implement `src/agents/character_agent.py` with personality models
   - Build simulation loop in `src/simulation/`

3. **Phase 3**: Drama Enhancement
   - Add dramatic operators in `src/generation/drama_operators.py`
   - Implement plot pattern management

4. **Phase 4**: Multi-modal Output
   - Integrate voice synthesis
   - Add visual rendering components

## Critical Implementation Details

### Latency Management
- Use GPT-3.5-turbo for non-critical prompt stages
- Implement voice buffering system (generate n+1 while playing n)
- Hide generation time during user interaction periods

### Solving Key Problems
- **Blank Page Problem**: Always provide simulation context before generation
- **10,000 Bowls of Oatmeal**: Enforce 3-hour gaps between episode generation
- **Slot Machine Effect**: Use multi-agent simulation for non-random creativity

### State Management
The system uses complex state machines for agents:
- IDLE → PERCEIVING → DECIDING → ACTING → REFLECTING
- Maintain exactly ONE agent in "in_progress" state at a time

### Quality Checkpoints
Implement quality checks at:
- Character consistency (threshold: 0.8)
- Narrative coherence (threshold: 0.85)
- Dialogue naturalness (threshold: 0.75)

## Testing Strategy

```bash
# Unit tests for individual modules
pytest tests/unit/

# Integration tests for full pipeline
pytest tests/integration/ --simulation-mock

# Quality tests for generated content
python tests/quality/coherence_test.py --samples 10
```

## Configuration

System configuration should follow this structure:
```yaml
# config.yaml
simulation:
  time_step_minutes: 15
  max_agents: 10
generation:
  llm_model: gpt-4
  temperature: 0.8
  prompt_chain_stages: [concept, discriminate, dramatic, coherence, polish]
dramatic_operators:
  available: [reversal, foreshadowing, callback, escalation, cliffhanger]
  max_per_scene: 3
```

## File Structure Expectations

```
src/
  agents/          # Character agents and personality models
  simulation/      # Simulation loop and data collection
  llm/            # LLM processing and prompt chains
  generation/     # Scene and dialogue generation
  drama/          # Dramatic operators and plot patterns
  rendering/      # Visual and audio output systems
  models/         # Data models and structures
```

## Important Prompting Patterns

When implementing LLM prompts, follow these patterns from the design docs:
- Always include character personality and backstory in context
- Use role-switching in prompt chains (generator → evaluator → refiner)
- Include "dramatic potential" scoring in concept evaluation
- Implement fallback templates for generation failures