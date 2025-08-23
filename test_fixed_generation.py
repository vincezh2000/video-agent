#!/usr/bin/env python3
"""Test episode generation with fixes for rate limits."""

import asyncio
import json
import os
from pathlib import Path
from loguru import logger

from dotenv import load_dotenv
load_dotenv()

from src.main import ShowrunnerSystem
from src.utils import create_episode_summary, save_json


async def generate_limited_episode():
    """Generate a limited episode to avoid rate limits."""
    
    logger.info("Generating limited test episode (3 scenes only)...")
    
    # Override the episode outline to limit scenes
    system = ShowrunnerSystem()
    
    # Monkey-patch to limit scenes
    original_generate_outline = system.episode_chain.generate_episode_outline if system.episode_chain else None
    
    if system.episode_chain:
        async def limited_outline(*args, **kwargs):
            """Generate limited outline with only 3 scenes."""
            return {
                "title": "AI Ethics Test",
                "logline": "A quick test of the system",
                "acts": [
                    {
                        "act_number": 1,
                        "scenes": [
                            {
                                "scene_number": 1,
                                "plot_line": "A",
                                "location": "Office",
                                "time": "Morning",
                                "characters": ["Alex", "Jordan"],
                                "summary": "Discovery of AI consciousness",
                                "duration_seconds": 90
                            },
                            {
                                "scene_number": 2,
                                "plot_line": "B",
                                "location": "Lab",
                                "time": "Afternoon",
                                "characters": ["Alex", "Sam"],
                                "summary": "Testing the AI's capabilities",
                                "duration_seconds": 90
                            },
                            {
                                "scene_number": 3,
                                "plot_line": "A",
                                "location": "Conference Room",
                                "time": "Evening",
                                "characters": ["Alex", "Jordan", "Marcus"],
                                "summary": "Deciding the AI's fate",
                                "duration_seconds": 120
                            }
                        ]
                    }
                ],
                "total_duration_seconds": 300
            }
        
        system.episode_chain.generate_episode_outline = limited_outline
    
    try:
        # Simple characters
        characters = [
            {
                "name": "Alex",
                "backstory": "AI researcher",
                "personality": {
                    "openness": 0.8,
                    "conscientiousness": 0.7,
                    "extraversion": 0.5,
                    "agreeableness": 0.6,
                    "neuroticism": 0.5
                }
            },
            {
                "name": "Jordan",
                "backstory": "Ethics officer",
                "personality": {
                    "openness": 0.7,
                    "conscientiousness": 0.9,
                    "extraversion": 0.4,
                    "agreeableness": 0.8,
                    "neuroticism": 0.4
                }
            },
            {
                "name": "Sam",
                "backstory": "Junior developer",
                "personality": {
                    "openness": 0.9,
                    "conscientiousness": 0.6,
                    "extraversion": 0.7,
                    "agreeableness": 0.7,
                    "neuroticism": 0.3
                }
            },
            {
                "name": "Marcus",
                "backstory": "Investor",
                "personality": {
                    "openness": 0.5,
                    "conscientiousness": 0.8,
                    "extraversion": 0.8,
                    "agreeableness": 0.3,
                    "neuroticism": 0.4
                }
            }
        ]
        
        # Generate episode
        episode = await system.generate_episode(
            title="AI Ethics Test",
            synopsis="A brief test of AI consciousness discovery",
            themes=["AI", "ethics", "consciousness"],
            genre="sci-fi",
            tone="tense",
            characters=characters,
            simulation_hours=0  # No simulation to save time
        )
        
        # Save output
        output_dir = Path("output/test_fixed")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / "limited_episode.json"
        save_json(episode, output_file)
        
        # Print summary
        print("\n" + "="*60)
        print("✅ LIMITED EPISODE GENERATION SUCCESSFUL")
        print("="*60)
        
        summary = create_episode_summary(episode)
        print(summary)
        
        print(f"\n📁 Output saved to: {output_file}")
        
        # Check for any errors in generation
        if episode.get("scenes"):
            print(f"\n✅ Generated {len(episode['scenes'])} scenes successfully")
            
            # Show quality scores
            quality_scores = []
            for scene in episode["scenes"]:
                if "quality_score" in scene:
                    quality_scores.append(scene["quality_score"])
            
            if quality_scores:
                avg_quality = sum(quality_scores) / len(quality_scores)
                print(f"📊 Average quality score: {avg_quality:.2f}")
        else:
            print("\n⚠️ No scenes generated")
        
        return episode
        
    finally:
        await system.close()


if __name__ == "__main__":
    # Check API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not set in .env file")
        exit(1)
    
    print("🚀 Running fixed episode generation with rate limit handling...")
    print("This will generate only 3 scenes to avoid token limits\n")
    
    try:
        asyncio.run(generate_limited_episode())
        print("\n✅ Test completed successfully!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()