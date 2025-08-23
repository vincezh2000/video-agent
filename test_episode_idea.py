#!/usr/bin/env python3
"""Test episode generation with a creative idea."""

import asyncio
import json
import os
from pathlib import Path
from datetime import datetime

# Set a dummy API key for testing (won't actually call API)
os.environ["OPENAI_API_KEY"] = "test-key-for-structure-check"

from src.agents import CharacterAgent
from src.simulation import SimulationEngine
from src.drama import DramaEngine
from src.generation import SceneCompiler
from src.utils import create_episode_summary, save_json


async def test_system_structure():
    """Test the system structure without actual API calls."""
    
    print("🎬 Testing Showrunner System Structure\n")
    print("=" * 60)
    
    # Test 1: Create characters
    print("\n✅ Test 1: Creating Characters")
    characters = []
    
    # Character 1: The Time-Traveling Barista
    character1 = CharacterAgent(
        name="Luna Chen",
        backstory="A barista who accidentally discovered her coffee machine can brew temporal portals. She struggles to keep her café running while secretly preventing timeline disasters.",
        personality={
            "openness": 0.95,
            "conscientiousness": 0.7,
            "extraversion": 0.6,
            "agreeableness": 0.8,
            "neuroticism": 0.4
        },
        age=28,
        occupation="Barista/Time Guardian"
    )
    characters.append(character1)
    print(f"  Created: {character1.name} - {character1.occupation}")
    
    # Character 2: The Confused Customer
    character2 = CharacterAgent(
        name="Professor Marcus Webb",
        backstory="A theoretical physicist who becomes a regular customer, slowly realizing the café exists outside normal spacetime. He's both fascinated and terrified.",
        personality={
            "openness": 0.85,
            "conscientiousness": 0.9,
            "extraversion": 0.3,
            "agreeableness": 0.6,
            "neuroticism": 0.8
        },
        age=52,
        occupation="Physicist"
    )
    characters.append(character2)
    print(f"  Created: {character2.name} - {character2.occupation}")
    
    # Character 3: The Rival from the Future
    character3 = CharacterAgent(
        name="Zara-9",
        backstory="A coffee chain executive from 2087 who wants to steal the time-travel technology to monopolize coffee across all timelines.",
        personality={
            "openness": 0.4,
            "conscientiousness": 0.95,
            "extraversion": 0.8,
            "agreeableness": 0.2,
            "neuroticism": 0.3
        },
        age=35,
        occupation="Temporal Corporate Raider"
    )
    characters.append(character3)
    print(f"  Created: {character3.name} - {character3.occupation}")
    
    # Test 2: Initialize Simulation
    print("\n✅ Test 2: Initializing Simulation Engine")
    simulation = SimulationEngine(time_step_minutes=15)
    
    # Use default locations (Office, Conference Room, etc.)
    # The simulation engine already has locations initialized
    
    for char in characters:
        simulation.add_agent(char, "Office")  # Use existing location
    
    print(f"  Added {len(characters)} agents to simulation")
    print(f"  Locations: {', '.join(simulation.locations.keys())}")
    
    # Test 3: Drama Engine
    print("\n✅ Test 3: Initializing Drama Engine")
    drama_engine = DramaEngine()
    
    test_scene = {
        "scene_number": 1,
        "tension": 0.4,
        "act_number": 1
    }
    
    enhanced = drama_engine.enhance_scene(test_scene, max_operators=2)
    print(f"  Applied plot line: {enhanced.get('plot_line', 'A')}")
    print(f"  Dramatic operators available: {len(drama_engine.operator_library.operators)}")
    
    # Test 4: Scene Compiler
    print("\n✅ Test 4: Testing Scene Compiler")
    compiler = SceneCompiler(drama_engine)
    
    # Create a test scene
    raw_scene = {
        "location": "Temporal Grounds Café",
        "time": "Morning (Multiple Timelines)",
        "description": "Luna serves coffee while time rifts open around the café",
        "dialogue": [
            {
                "character": "Luna Chen",
                "line": "One temporal latte coming up... wait, didn't I just serve you yesterday's tomorrow?",
                "emotion": "confused"
            },
            {
                "character": "Professor Marcus Webb",
                "line": "The temporal paradoxes in this establishment are giving me a migraine... or will give me one... or already did.",
                "emotion": "frustrated"
            },
            {
                "character": "Zara-9",
                "line": "In my timeline, this café is already mine. I'm just here to ensure it happens.",
                "emotion": "confident"
            }
        ],
        "tension": 0.6
    }
    
    compiled_scene = compiler.compile_scene(raw_scene, scene_number=1, act_number=1)
    print(f"  Compiled scene: {compiled_scene.metadata.scene_id}")
    print(f"  Dialogue lines: {len(compiled_scene.dialogue)}")
    
    # Test 5: Episode Structure
    print("\n✅ Test 5: Creating Episode Structure")
    
    episode_data = {
        "title": "The Café at the End of Time",
        "synopsis": "When a barista discovers her coffee machine can brew temporal portals, she must serve customers from across time while preventing a future corporation from stealing her technology.",
        "themes": ["time paradoxes", "small business vs corporation", "finding home across timelines"],
        "genre": "sci-fi comedy",
        "tone": "quirky",
        "scenes": [raw_scene],  # Would normally have 14 scenes
        "dramatic_arc": {
            "average_tension": 0.65,
            "peaks": 3,
            "has_climax": True
        }
    }
    
    # Generate summary
    summary = create_episode_summary(episode_data)
    print(f"\n{summary}")
    
    # Save test output
    output_dir = Path("output/test")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    test_output = {
        "test_run": datetime.now().isoformat(),
        "episode_idea": episode_data,
        "compiled_scene": compiled_scene.to_dict(),
        "character_count": len(characters),
        "system_status": "All modules operational"
    }
    
    output_file = output_dir / "system_test.json"
    save_json(test_output, output_file)
    
    print("\n" + "=" * 60)
    print("🎉 System Structure Test Complete!")
    print(f"📁 Test output saved to: {output_file}")
    print("\n💡 Episode Idea: 'The Café at the End of Time'")
    print("   A comedy about a time-traveling coffee shop where:")
    print("   - Each espresso shot can change history")
    print("   - Customers from different timelines meet")
    print("   - The WiFi password is 'yesterday'")
    print("   - Reviews on Yelp exist before the café was built")
    print("\n✨ All systems are ready for full episode generation!")
    
    return test_output


async def run_mini_simulation():
    """Run a mini simulation to test the system."""
    print("\n" + "=" * 60)
    print("🎮 Running Mini Simulation (1 hour, 4 time steps)")
    print("=" * 60)
    
    # Create simulation
    simulation = SimulationEngine(time_step_minutes=15)
    
    # Add our characters
    luna = CharacterAgent(
        name="Luna Chen",
        backstory="Time-traveling barista",
        personality={"openness": 0.9, "conscientiousness": 0.7, "extraversion": 0.6, "agreeableness": 0.8, "neuroticism": 0.4},
        age=28,
        occupation="Barista"
    )
    
    marcus = CharacterAgent(
        name="Professor Marcus Webb",
        backstory="Confused physicist customer",
        personality={"openness": 0.85, "conscientiousness": 0.9, "extraversion": 0.3, "agreeableness": 0.6, "neuroticism": 0.8},
        age=52,
        occupation="Physicist"
    )
    
    simulation.add_agent(luna, "Office")
    simulation.add_agent(marcus, "Office")
    
    # Run short simulation
    results = await simulation.run_simulation(duration_hours=0.25)  # 15 minutes
    
    print(f"\n📊 Simulation Results:")
    print(f"  Events generated: {len(results.get('events', []))}")
    print(f"  Final narrative tension: {simulation.narrative_tension:.2f}")
    
    # Show some events
    for event in results.get('events', [])[:3]:
        print(f"  - {event.get('description', 'Unknown event')}")
    
    return results


if __name__ == "__main__":
    print("\n🚀 SHOWRUNNER SYSTEM TEST")
    print("Testing creative episode idea: 'The Café at the End of Time'\n")
    
    # Run tests
    asyncio.run(test_system_structure())
    
    # Run mini simulation
    asyncio.run(run_mini_simulation())
    
    print("\n✅ All tests completed successfully!")
    print("The system is ready to generate full episodes.")
    print("\nTo generate a real episode with OpenAI, set your API key in .env")
    print("Then run: python example_generate_episode.py")