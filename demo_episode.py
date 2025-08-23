#!/usr/bin/env python3
"""Demo episode generation without API calls."""

import json
from datetime import datetime
from pathlib import Path
from src.drama import DramaEngine
from src.generation import SceneCompiler
from src.utils import create_episode_summary, save_json

def generate_demo_episode():
    """Generate a demo episode without API calls."""
    
    print("\n🎬 DEMO EPISODE GENERATION")
    print("=" * 60)
    print("Generating: 'The Quantum Debugger'")
    print("A thriller about a programmer who can debug reality itself")
    print("=" * 60)
    
    # Initialize components
    drama_engine = DramaEngine()
    compiler = SceneCompiler(drama_engine)
    
    # Episode metadata
    episode_data = {
        "title": "The Quantum Debugger",
        "synopsis": "When a programmer discovers their IDE can edit reality's source code, they must fix critical bugs in the universe before it crashes.",
        "themes": ["reality as code", "responsibility", "unintended consequences"],
        "genre": "sci-fi",
        "tone": "tense",
        "scenes": []
    }
    
    # Generate 3 demo scenes
    scenes_data = [
        {
            "scene_number": 1,
            "act_number": 1,
            "location": "Tech Startup Office - Night",
            "time": "2:00 AM",
            "description": "Alex discovers the quantum debugging feature",
            "dialogue": [
                {
                    "character": "Alex Rivera",
                    "line": "Wait... this stacktrace shows calls from... reality itself?",
                    "emotion": "shocked"
                },
                {
                    "character": "Debug Console",
                    "line": "REALITY.EXE has encountered an unhandled exception at 0x00000000DEADBEEF",
                    "emotion": "neutral"
                },
                {
                    "character": "Alex Rivera",
                    "line": "If I can see the error... maybe I can fix it. What could go wrong?",
                    "emotion": "curious"
                }
            ],
            "tension": 0.6,
            "duration_seconds": 90
        },
        {
            "scene_number": 2,
            "act_number": 1,
            "location": "Coffee Shop - Morning",
            "time": "8:00 AM",
            "description": "Reality starts glitching after Alex's first 'fix'",
            "dialogue": [
                {
                    "character": "Barista",
                    "line": "Your coffee, sir... sir... sir... ERROR: NullPointerException in customer.memory",
                    "emotion": "confused"
                },
                {
                    "character": "Alex Rivera",
                    "line": "Oh no. The garbage collector is removing people's memories!",
                    "emotion": "panicked"
                },
                {
                    "character": "Sam Chen",
                    "line": "Alex, why do I have undefined variables in my thoughts?",
                    "emotion": "fearful"
                }
            ],
            "tension": 0.8,
            "duration_seconds": 120
        },
        {
            "scene_number": 3,
            "act_number": 2,
            "location": "Server Room of Reality",
            "time": "Timeless",
            "description": "Alex enters the core system to fix the cascading failures",
            "dialogue": [
                {
                    "character": "System Administrator",
                    "line": "You shouldn't be here. This is kernel space.",
                    "emotion": "stern"
                },
                {
                    "character": "Alex Rivera",
                    "line": "I caused this mess. I need root access to fix it.",
                    "emotion": "determined"
                },
                {
                    "character": "System Administrator",
                    "line": "Every bug fix creates ten new bugs. That's the first law of reality programming.",
                    "emotion": "wise"
                },
                {
                    "character": "Alex Rivera",
                    "line": "Then I'll need to refactor the entire universe. Starting... now.",
                    "emotion": "resolved"
                }
            ],
            "tension": 0.9,
            "duration_seconds": 150
        }
    ]
    
    # Compile scenes with drama enhancement
    print("\n📝 Compiling scenes with dramatic enhancement...")
    
    for scene_data in scenes_data:
        # Apply drama operators
        enhanced = drama_engine.enhance_scene(scene_data, max_operators=2)
        
        # Compile scene
        compiled = compiler.compile_scene(enhanced, 
                                         scene_data["scene_number"], 
                                         scene_data["act_number"])
        
        # Add to episode
        episode_data["scenes"].append(compiled.to_dict())
        
        print(f"  ✓ Scene {scene_data['scene_number']}: {scene_data['location']}")
        if enhanced.get("dramatic_operators"):
            print(f"    Applied: {', '.join([op['name'] for op in enhanced['dramatic_operators']])}")
    
    # Calculate statistics
    total_duration = sum(s["metadata"]["duration_seconds"] for s in episode_data["scenes"])
    avg_tension = sum(s["metadata"]["tension_level"] for s in episode_data["scenes"]) / len(episode_data["scenes"])
    
    episode_data["statistics"] = {
        "total_scenes": len(episode_data["scenes"]),
        "total_duration_seconds": total_duration,
        "total_duration_minutes": total_duration / 60,
        "average_tension": avg_tension,
        "dramatic_peaks": 2
    }
    
    # Add dramatic arc
    episode_data["dramatic_arc"] = drama_engine.analyze_dramatic_arc(episode_data["scenes"])
    
    # Generate screenplay format
    screenplay = []
    screenplay.append(f"TITLE: {episode_data['title'].upper()}")
    screenplay.append(f"\n{episode_data['synopsis']}\n")
    screenplay.append("=" * 50 + "\n")
    
    for scene in compiler.compiled_scenes:
        screenplay.append(scene.to_screenplay_format())
        screenplay.append("\n" + "-" * 30 + "\n")
    
    episode_data["screenplay"] = "\n".join(screenplay)
    
    # Save output
    output_dir = Path("output/demo")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / "quantum_debugger_episode.json"
    save_json(episode_data, output_file)
    
    screenplay_file = output_dir / "quantum_debugger_screenplay.txt"
    with open(screenplay_file, 'w') as f:
        f.write(episode_data["screenplay"])
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 EPISODE GENERATION COMPLETE")
    print("=" * 60)
    
    summary = create_episode_summary(episode_data)
    print(summary)
    
    print("\n🎭 SAMPLE DIALOGUE:")
    print("-" * 40)
    for line in episode_data["scenes"][0]["dialogue"][:3]:
        print(f"{line['character']}: {line['line']}")
        if line.get('emotion') != 'neutral':
            print(f"  [{line['emotion']}]")
    
    print("\n📁 OUTPUT FILES:")
    print(f"  JSON: {output_file}")
    print(f"  Screenplay: {screenplay_file}")
    
    print("\n✨ Demo episode generated successfully!")
    print("This demonstrates the system's capability without API calls.")
    print("\nFor full AI-generated content, add your OpenAI API key to .env")
    
    return episode_data

if __name__ == "__main__":
    generate_demo_episode()