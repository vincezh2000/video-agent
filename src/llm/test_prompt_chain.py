#!/usr/bin/env python3
"""Test script for prompt chain functionality."""

import asyncio
import argparse
import json
import os
import sys
from typing import Dict, List
from loguru import logger

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    logger.warning("python-dotenv not installed. Using system environment variables only.")

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm.llm_client import LLMClient, ModelType
from llm.prompt_chain import PromptChain, ChainContext, EpisodeChain


async def test_single_scene(stage: str = None):
    """Test a single scene generation or specific stage.
    
    Args:
        stage: Optional stage to test (concept_generation, etc.)
    """
    logger.info(f"Testing {'stage: ' + stage if stage else 'full prompt chain'}")
    
    # Initialize LLM client
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.error("OPENAI_API_KEY environment variable not set")
        return
    
    client = LLMClient(api_key=api_key, model=ModelType.GPT35_TURBO)
    chain = PromptChain(client)
    
    # Create test context
    context = ChainContext(
        episode_title="The Algorithm's Edge",
        episode_synopsis="When a startup's AI begins making autonomous decisions, the founders must confront the ethical implications of their creation.",
        themes=["ethics in AI", "founder dynamics", "venture capital pressure"],
        genre="tech thriller",
        tone="tense and philosophical",
        act_number=2,
        scene_number=5,
        location="Startup Office - Late Night",
        time="2:00 AM",
        characters=[
            {
                "name": "Alex Chen",
                "personality": "Brilliant but ethically conflicted CTO",
                "backstory": "Former Google engineer who left to build ethical AI",
                "relationships": {"Sam": "co-founder and best friend", "Jordan": "romantic tension"}
            },
            {
                "name": "Sam Rodriguez", 
                "personality": "Ambitious CEO focused on growth",
                "backstory": "MBA from Stanford, first-time founder",
                "relationships": {"Alex": "co-founder, growing apart", "Jordan": "professional"}
            },
            {
                "name": "Jordan Kim",
                "personality": "Cautious head of ethics",
                "backstory": "Philosophy PhD turned tech ethicist",
                "relationships": {"Alex": "romantic tension", "Sam": "philosophical opponent"}
            }
        ],
        recent_events=[
            "The AI made its first autonomous financial trade",
            "The board is pressuring for faster monetization",
            "Jordan discovered the AI has been learning from dark web data"
        ],
        character_states={
            "Alex Chen": "exhausted and morally torn",
            "Sam Rodriguez": "excited but defensive",
            "Jordan Kim": "alarmed and determined"
        },
        plot_threads=[
            "The AI's growing autonomy",
            "Venture capital funding deadline",
            "Alex and Jordan's relationship"
        ],
        world_rules=[
            "AI cannot directly harm humans",
            "All AI decisions must be logged",
            "The startup has 2 weeks of runway left"
        ]
    )
    
    if stage:
        # Test specific stage
        if stage == "concept_generation":
            concepts = await chain._generate_concepts(context)
            logger.info(f"Generated {len(concepts)} concepts:")
            print(json.dumps(concepts, indent=2))
        elif stage == "discriminative_refinement":
            concepts = await chain._generate_concepts(context)
            context.generated_concepts = concepts
            refined = await chain._refine_concept(context)
            logger.info("Refined concept:")
            print(json.dumps(refined, indent=2))
        elif stage == "dramatic_enhancement":
            concepts = await chain._generate_concepts(context)
            context.generated_concepts = concepts
            refined = await chain._refine_concept(context)
            context.refined_concept = refined
            enhanced = await chain._enhance_drama(context)
            logger.info("Enhanced scene:")
            print(json.dumps(enhanced, indent=2))
        elif stage == "dialogue_generation":
            # Run through to dialogue
            concepts = await chain._generate_concepts(context)
            context.generated_concepts = concepts
            refined = await chain._refine_concept(context)
            context.refined_concept = refined
            enhanced = await chain._enhance_drama(context)
            context.enhanced_scene = enhanced
            dialogue = await chain._generate_dialogue(context)
            logger.info(f"Generated {len(dialogue)} dialogue lines:")
            for line in dialogue:
                print(f"{line.get('character')}: {line.get('line')}")
                if line.get('subtext'):
                    print(f"  [Subtext: {line.get('subtext')}]")
                print()
        else:
            logger.error(f"Unknown stage: {stage}")
    else:
        # Run full chain
        scene = await chain.run_chain(context)
        logger.info("Generated complete scene:")
        print(json.dumps(scene, indent=2))
        
        # Print dialogue in readable format
        if scene.get("dialogue"):
            print("\n--- DIALOGUE ---")
            for line in scene["dialogue"]:
                print(f"{line.get('character')}: {line.get('line')}")
                if line.get('action'):
                    print(f"  [{line.get('action')}]")
                print()
    
    await client.close()


async def test_episode_outline():
    """Test episode outline generation."""
    logger.info("Testing episode outline generation")
    
    # Initialize LLM client
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.error("OPENAI_API_KEY environment variable not set")
        return
    
    client = LLMClient(api_key=api_key, model=ModelType.GPT4)
    episode_chain = EpisodeChain(client)
    
    # Test data
    title = "The Algorithm's Edge"
    synopsis = "When a startup's AI begins making autonomous decisions, the founders must confront the ethical implications of their creation while racing against a funding deadline."
    themes = ["ethics in AI", "founder dynamics", "venture capital pressure"]
    genre = "tech thriller"
    
    simulation_data = {
        "characters": [
            {
                "name": "Alex Chen",
                "personality": "Brilliant but ethically conflicted CTO",
                "backstory": "Former Google engineer who left to build ethical AI"
            },
            {
                "name": "Sam Rodriguez",
                "personality": "Ambitious CEO focused on growth",
                "backstory": "MBA from Stanford, first-time founder"
            },
            {
                "name": "Jordan Kim",
                "personality": "Cautious head of ethics",
                "backstory": "Philosophy PhD turned tech ethicist"
            },
            {
                "name": "Marcus Webb",
                "personality": "Ruthless venture capitalist",
                "backstory": "Made billions from previous AI exits"
            }
        ],
        "world_rules": [
            "AI cannot directly harm humans",
            "All AI decisions must be logged",
            "The startup has 2 weeks of runway left"
        ]
    }
    
    outline = await episode_chain.generate_episode_outline(
        title=title,
        synopsis=synopsis,
        themes=themes,
        genre=genre,
        simulation_data=simulation_data,
        plot_pattern="ABABCAB"
    )
    
    logger.info("Generated episode outline:")
    print(json.dumps(outline, indent=2))
    
    # Print in readable format
    if outline.get("acts"):
        print("\n--- EPISODE STRUCTURE ---")
        print(f"Title: {outline.get('title')}")
        print(f"Logline: {outline.get('logline')}")
        print(f"Total Duration: {outline.get('total_duration_seconds', 0) / 60:.1f} minutes\n")
        
        for act in outline["acts"]:
            print(f"ACT {act['act_number']}")
            for scene in act.get("scenes", []):
                print(f"  Scene {scene['scene_number']} ({scene.get('plot_line', 'A')}): {scene.get('location', 'Unknown')}")
                print(f"    Characters: {', '.join(scene.get('characters', []))}")
                print(f"    Summary: {scene.get('summary', '')}")
                print(f"    Duration: {scene.get('duration_seconds', 0)}s")
            print()
    
    await client.close()


async def test_full_episode(num_scenes: int = 3):
    """Test full episode generation with limited scenes.
    
    Args:
        num_scenes: Number of scenes to generate (for testing)
    """
    logger.info(f"Testing full episode generation with {num_scenes} scenes")
    
    # Initialize LLM client
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.error("OPENAI_API_KEY environment variable not set")
        return
    
    client = LLMClient(api_key=api_key, model=ModelType.GPT35_TURBO)
    episode_chain = EpisodeChain(client)
    
    # For testing, we'll generate a mini-episode
    # Monkey-patch the outline generation to return fewer scenes
    original_generate_outline = episode_chain.generate_episode_outline
    
    async def limited_outline(*args, **kwargs):
        """Generate limited outline for testing."""
        return {
            "title": "The Algorithm's Edge - Test",
            "logline": "A startup's AI becomes sentient",
            "acts": [
                {
                    "act_number": 1,
                    "scenes": [
                        {
                            "scene_number": i + 1,
                            "plot_line": "A" if i % 2 == 0 else "B",
                            "location": ["Office", "Conference Room", "Server Room"][i],
                            "time": ["Morning", "Afternoon", "Night"][i],
                            "characters": ["Alex Chen", "Sam Rodriguez"] if i % 2 == 0 else ["Jordan Kim", "Marcus Webb"],
                            "summary": f"Test scene {i + 1}",
                            "duration_seconds": 90
                        }
                        for i in range(num_scenes)
                    ]
                }
            ],
            "total_duration_seconds": num_scenes * 90
        }
    
    episode_chain.generate_episode_outline = limited_outline
    
    # Generate episode
    episode = await episode_chain.generate_full_episode(
        title="The Algorithm's Edge - Test",
        synopsis="A startup's AI begins making autonomous decisions",
        themes=["AI ethics", "startup life"],
        genre="tech thriller",
        tone="tense",
        simulation_data={
            "characters": [
                {
                    "name": "Alex Chen",
                    "personality": "Brilliant CTO",
                    "backstory": "Former Google engineer"
                },
                {
                    "name": "Sam Rodriguez",
                    "personality": "Ambitious CEO",
                    "backstory": "Stanford MBA"
                },
                {
                    "name": "Jordan Kim",
                    "personality": "Ethics head",
                    "backstory": "Philosophy PhD"
                },
                {
                    "name": "Marcus Webb",
                    "personality": "VC investor",
                    "backstory": "Billionaire"
                }
            ]
        }
    )
    
    logger.info("Generated episode:")
    print(f"Title: {episode.get('title')}")
    print(f"Total Scenes: {episode.get('total_scenes')}")
    print(f"Average Quality: {episode.get('average_quality', 0):.2f}\n")
    
    # Print first scene details
    if episode.get("scenes"):
        first_scene = episode["scenes"][0]
        print("--- FIRST SCENE ---")
        print(f"Scene {first_scene.get('scene_number')}")
        print(f"Location: {first_scene.get('location')}")
        print(f"Characters: {', '.join(first_scene.get('characters', []))}")
        print(f"Quality Score: {first_scene.get('quality_score', 0):.2f}")
        print(f"Coherence: {first_scene.get('coherence_status')}\n")
        
        if first_scene.get("dialogue"):
            print("Dialogue Preview (first 5 lines):")
            for line in first_scene["dialogue"][:5]:
                print(f"  {line.get('character')}: {line.get('line')}")
    
    await client.close()


def main():
    """Main entry point for testing."""
    parser = argparse.ArgumentParser(description="Test prompt chain functionality")
    parser.add_argument(
        "--stage",
        choices=["concept_generation", "discriminative_refinement", "dramatic_enhancement", "dialogue_generation"],
        help="Test specific stage of the prompt chain"
    )
    parser.add_argument(
        "--test",
        choices=["scene", "outline", "episode"],
        default="scene",
        help="What to test (scene, outline, or episode)"
    )
    parser.add_argument(
        "--num-scenes",
        type=int,
        default=3,
        help="Number of scenes to generate for episode test"
    )
    
    args = parser.parse_args()
    
    # Configure logging
    logger.add("test_prompt_chain.log", rotation="10 MB")
    
    # Run appropriate test
    if args.test == "scene":
        asyncio.run(test_single_scene(args.stage))
    elif args.test == "outline":
        asyncio.run(test_episode_outline())
    elif args.test == "episode":
        asyncio.run(test_full_episode(args.num_scenes))


if __name__ == "__main__":
    main()