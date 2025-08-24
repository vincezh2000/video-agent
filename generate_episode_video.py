#!/usr/bin/env python3
"""Generate video from episode JSON using fal.ai models."""

import asyncio
import json
import os
from pathlib import Path
from loguru import logger

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

from src.video.episode_video_pipeline import EpisodeVideoPipeline, generate_episode_video_from_json


async def generate_video_from_latest_episode():
    """Generate video from the latest episode JSON."""
    
    # Configure logging
    logger.add("logs/video_generation.log", rotation="10 MB")
    
    # Input and output paths
    episode_json = "output/latest_episode_mock.json"
    
    # Character to celebrity voice mapping
    character_voice_mapping = {
        "Alex Chen": "elon_musk",      # Tech founder → Elon voice
        "Sam Rodriguez": "trump",       # Business leader → Trump voice
        "Jordan Park": "obama"          # Competitor → Obama voice
    }
    
    # Visual style options: cinematic, realistic, dramatic, tech_noir
    visual_style = "tech_noir"  # Fits the tech thriller genre
    
    print("\n" + "="*60)
    print("🎬 EPISODE VIDEO GENERATION")
    print("="*60)
    print(f"📄 Episode JSON: {episode_json}")
    print(f"🎨 Visual Style: {visual_style}")
    print(f"🎤 Voice Mapping:")
    for char, voice in character_voice_mapping.items():
        print(f"   - {char}: {voice}")
    print("="*60)
    
    # Check required API keys
    fal_key = os.getenv("FAL_KEY") or os.getenv("FAL_API_KEY")
    if not fal_key:
        print("❌ fal.ai API key not found in environment")
        print("Please set one of the following:")
        print("  export FAL_KEY='your-fal-key'  (recommended)")
        print("  export FAL_API_KEY='your-fal-key'")
        print("\nGet your API key from: https://fal.ai/dashboard")
        return None
    
    if not os.getenv("ELEVENLABS_API_KEY"):
        print("⚠️ ELEVENLABS_API_KEY not found")
        print("Audio will not be generated. To enable:")
        print("export ELEVENLABS_API_KEY='your-elevenlabs-api-key'")
    
    try:
        # Initialize pipeline
        print("\n🚀 Initializing video generation pipeline...")
        pipeline = EpisodeVideoPipeline(
            fal_api_key=fal_key,  # Use the detected key
            elevenlabs_api_key=os.getenv("ELEVENLABS_API_KEY")
        )
        
        # Generate video
        print("\n🎬 Starting video generation...")
        print("This process will:")
        print("  1. Extract script data")
        print("  2. Generate character portraits")
        print("  3. Generate scene backgrounds")
        print("  4. Generate dialogue audio")
        print("  5. Create scene composites")
        print("  6. Generate talking videos")
        print("  7. Assemble final video")
        print("\n⏱️ This may take 10-20 minutes depending on episode length...")
        
        video_path = await pipeline.generate_episode_video(
            episode_json_path=episode_json,
            visual_style=visual_style,
            character_voice_mapping=character_voice_mapping
        )
        
        print("\n" + "="*60)
        print("✅ VIDEO GENERATION COMPLETE!")
        print("="*60)
        print(f"🎥 Final Video: {video_path}")
        
        # Check file size
        if Path(video_path).exists():
            size_mb = Path(video_path).stat().st_size / (1024 * 1024)
            print(f"📊 File Size: {size_mb:.2f} MB")
        
        # Check for subtitles
        subtitle_path = video_path.replace('.mp4', '.srt')
        if Path(subtitle_path).exists():
            print(f"📝 Subtitles: {subtitle_path}")
        
        print("="*60)
        
        return video_path
        
    except Exception as e:
        logger.error(f"Video generation failed: {e}")
        print(f"\n❌ Video generation failed: {e}")
        import traceback
        traceback.print_exc()
        return None


async def test_extraction_only():
    """Test just the script extraction step."""
    from src.video.script_extractor import extract_episode_for_video
    
    print("\n📝 Testing Script Extraction")
    print("="*40)
    
    episode_json = "output/latest_episode_mock.json"
    extraction = extract_episode_for_video(
        episode_json,
        "output/test_extraction.json"
    )
    
    print(f"✅ Extraction complete:")
    print(f"   - Scenes: {extraction['statistics']['total_scenes']}")
    print(f"   - Characters: {extraction['statistics']['total_characters']}")
    print(f"   - Dialogues: {extraction['statistics']['total_dialogues']}")
    print(f"   - Duration: {extraction['statistics']['estimated_duration_minutes']:.1f} minutes")
    
    # Show sample scene
    if extraction['scenes']:
        scene = extraction['scenes'][0]
        print(f"\n📍 Sample Scene {scene['scene_number']}:")
        print(f"   Location: {scene['location']}")
        print(f"   Environment: {scene['environment_description']}")
        print(f"   Characters: {', '.join(scene['characters'])}")
        print(f"   Dialogues: {len(scene['dialogue_sequence'])}")
    
    return extraction


async def test_character_generation():
    """Test character image generation only."""
    from src.video.video_generator import VideoGenerator, PRESET_STYLES
    
    print("\n🎨 Testing Character Image Generation")
    print("="*40)
    
    fal_key = os.getenv("FAL_KEY") or os.getenv("FAL_API_KEY")
    if not fal_key:
        print("❌ fal.ai API key not set (FAL_KEY or FAL_API_KEY)")
        return
    
    generator = VideoGenerator()
    generator.set_visual_style(PRESET_STYLES["tech_noir"])
    
    # Generate a test character
    image_path = await generator.generate_character_image(
        character_name="Alex Chen",
        character_prompt="young tech entrepreneur, professional, intelligent, focused"
    )
    
    print(f"✅ Character image generated: {image_path}")
    return image_path


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate video from episode JSON")
    parser.add_argument(
        "--mode",
        choices=["full", "extract", "character"],
        default="full",
        help="Generation mode"
    )
    parser.add_argument(
        "--episode",
        default="output/latest_episode_mock.json",
        help="Path to episode JSON file"
    )
    parser.add_argument(
        "--style",
        choices=["cinematic", "realistic", "dramatic", "tech_noir"],
        default="tech_noir",
        help="Visual style preset"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    
    args = parser.parse_args()
    
    if args.debug:
        logger.add("logs/debug_video.log", level="DEBUG")
    
    # Run selected mode
    if args.mode == "full":
        asyncio.run(generate_video_from_latest_episode())
    elif args.mode == "extract":
        asyncio.run(test_extraction_only())
    elif args.mode == "character":
        asyncio.run(test_character_generation())


if __name__ == "__main__":
    main()