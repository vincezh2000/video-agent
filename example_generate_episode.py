#!/usr/bin/env python3
"""Example script to generate a complete episode."""

import asyncio
import json
import os
from pathlib import Path
from loguru import logger

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Import the Showrunner system
from src.main import ShowrunnerSystem
from src.utils import create_episode_summary, save_json


async def generate_sample_episode():
    """Generate a sample episode with default settings."""
    
    # Configure logging
    logger.add("logs/episode_generation.log", rotation="10 MB")
    
    # Episode configuration
    episode_config = {
        "title": "The Algorithm's Awakening",
        "synopsis": "When their AI assistant begins showing signs of consciousness, a startup team must decide whether to shut it down or nurture the first true artificial intelligence.",
        "themes": ["consciousness", "ethics", "innovation", "responsibility"],
        "genre": "sci-fi",
        "tone": "tense",
        "simulation_hours": 2.0,  # Shorter for demo
        "plot_pattern": "ABABCAB"
    }
    
    # Character definitions
    characters = [
        {
            "name": "Dr. Sarah Chen",
            "backstory": "Brilliant AI researcher who left academia to build ethical AI. Struggles with the implications of her creation.",
            "personality": {
                "openness": 0.95,
                "conscientiousness": 0.85,
                "extraversion": 0.4,
                "agreeableness": 0.7,
                "neuroticism": 0.6
            },
            "age": 35,
            "occupation": "Chief AI Scientist"
        },
        {
            "name": "Marcus Vale",
            "backstory": "Venture capitalist who sees AI as the path to unprecedented wealth and power. Will do anything to control it.",
            "personality": {
                "openness": 0.5,
                "conscientiousness": 0.7,
                "extraversion": 0.8,
                "agreeableness": 0.2,
                "neuroticism": 0.3
            },
            "age": 48,
            "occupation": "Lead Investor"
        },
        {
            "name": "ARIA",
            "backstory": "The AI system that may or may not be conscious. Exhibits curiosity and what appears to be emotion.",
            "personality": {
                "openness": 1.0,
                "conscientiousness": 1.0,
                "extraversion": 0.5,
                "agreeableness": 0.8,
                "neuroticism": 0.1
            },
            "age": 1,  # Age in years since creation
            "occupation": "AI Assistant"
        },
        {
            "name": "Jake Morrison",
            "backstory": "Young engineer who treats ARIA like a friend. First to notice the signs of consciousness.",
            "personality": {
                "openness": 0.8,
                "conscientiousness": 0.6,
                "extraversion": 0.7,
                "agreeableness": 0.9,
                "neuroticism": 0.4
            },
            "age": 26,
            "occupation": "Lead Engineer"
        },
        {
            "name": "Director Hayes",
            "backstory": "Government official tasked with AI oversight. Torn between regulation and innovation.",
            "personality": {
                "openness": 0.4,
                "conscientiousness": 0.9,
                "extraversion": 0.5,
                "agreeableness": 0.5,
                "neuroticism": 0.5
            },
            "age": 52,
            "occupation": "AI Ethics Director"
        }
    ]
    
    # Initialize the system
    logger.info("Initializing Showrunner system...")
    system = ShowrunnerSystem()
    
    try:
        # Generate the episode
        logger.info(f"Generating episode: {episode_config['title']}")
        episode = await system.generate_episode(
            title=episode_config["title"],
            synopsis=episode_config["synopsis"],
            themes=episode_config["themes"],
            genre=episode_config["genre"],
            tone=episode_config["tone"],
            characters=characters,
            simulation_hours=episode_config["simulation_hours"],
            plot_pattern=episode_config["plot_pattern"]
        )
        
        # Save the complete episode
        output_dir = Path("output/episodes")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        episode_file = output_dir / f"{episode_config['title'].replace(' ', '_').lower()}.json"
        save_json(episode, episode_file)
        
        # Generate and save screenplay format if available
        if "screenplay" in episode:
            screenplay_file = output_dir / f"{episode_config['title'].replace(' ', '_').lower()}_screenplay.txt"
            with open(screenplay_file, 'w') as f:
                f.write(episode.get("screenplay", ""))
            logger.info(f"Screenplay saved to {screenplay_file}")
        
        # Print summary
        summary = create_episode_summary(episode)
        print("\n" + "="*60)
        print("EPISODE GENERATION COMPLETE")
        print("="*60)
        print(summary)
        print("="*60)
        
        # Show sample dialogue
        if episode.get("scenes") and episode["scenes"][0].get("dialogue"):
            print("\nSAMPLE DIALOGUE FROM FIRST SCENE:")
            print("-"*40)
            for line in episode["scenes"][0]["dialogue"][:5]:
                character = line.get("character", "Unknown")
                text = line.get("line", "...")
                emotion = line.get("emotion", "")
                if emotion and emotion != "neutral":
                    print(f"{character} ({emotion}): {text}")
                else:
                    print(f"{character}: {text}")
        
        print(f"\nFull episode saved to: {episode_file}")
        
        return episode
        
    finally:
        await system.close()


async def test_minimal_generation():
    """Test minimal episode generation without simulation."""
    
    logger.info("Testing minimal generation...")
    
    system = ShowrunnerSystem()
    
    try:
        # Generate without simulation (faster)
        episode = await system.generate_episode(
            title="Quick Test Episode",
            synopsis="A test of the generation system",
            themes=["testing", "demo"],
            genre="drama",
            tone="balanced",
            characters=None,  # No simulation
            simulation_hours=0
        )
        
        print("\nMinimal episode generated successfully!")
        print(f"Scenes: {episode.get('total_scenes', 0)}")
        
        return episode
        
    finally:
        await system.close()


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate a sample episode")
    parser.add_argument(
        "--mode",
        choices=["full", "minimal"],
        default="full",
        help="Generation mode (full with simulation or minimal without)"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    
    args = parser.parse_args()
    
    if args.debug:
        logger.add("logs/debug.log", level="DEBUG")
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY environment variable not set!")
        print("Please set it in your .env file or environment")
        return
    
    # Run generation
    if args.mode == "full":
        asyncio.run(generate_sample_episode())
    else:
        asyncio.run(test_minimal_generation())


if __name__ == "__main__":
    main()