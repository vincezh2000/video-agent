#!/usr/bin/env python3
"""Test script for fal.ai API integration."""

import asyncio
import os
from pathlib import Path
from loguru import logger

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

from src.video.video_generator_v2 import VideoGeneratorV2, PRESET_STYLES_V2


async def test_ideogram_v3():
    """Test Ideogram V3 image generation."""
    print("\n🎨 Testing Ideogram V3 Image Generation")
    print("="*50)
    
    fal_key = os.getenv("FAL_KEY") or os.getenv("FAL_API_KEY")
    if not fal_key:
        print("❌ fal.ai API key not set (FAL_KEY or FAL_API_KEY)")
        return None
    
    try:
        # Initialize generator
        generator = VideoGeneratorV2()
        generator.set_visual_style(PRESET_STYLES_V2["tech_noir"])
        
        # Test character generation
        print("\n1️⃣ Generating character portrait...")
        character_image = await generator.generate_character_image(
            character_name="Alex Chen",
            character_prompt="young Asian tech entrepreneur, intelligent, wearing glasses, business casual"
        )
        print(f"✅ Character image: {character_image}")
        
        # Test scene background
        print("\n2️⃣ Generating scene background...")
        scene_image = await generator.generate_scene_background(
            scene_number=1,
            environment_prompt="modern tech laboratory, blue LED lighting, computer screens, futuristic"
        )
        print(f"✅ Scene background: {scene_image}")
        
        return character_image, scene_image
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return None


async def test_flux_kontext():
    """Test Flux Kontext Multi for compositing."""
    print("\n🎭 Testing Flux Kontext Multi Compositing")
    print("="*50)
    
    fal_key = os.getenv("FAL_KEY") or os.getenv("FAL_API_KEY")
    if not fal_key:
        print("❌ fal.ai API key not set (FAL_KEY or FAL_API_KEY)")
        return None
    
    try:
        generator = VideoGeneratorV2()
        generator.set_visual_style(PRESET_STYLES_V2["cinematic"])
        
        # First generate images
        print("\n📸 Generating base images...")
        
        # Character
        character_image = await generator.generate_character_image(
            character_name="Sarah Chen",
            character_prompt="professional woman, 30s, confident, business attire"
        )
        
        # Scene
        scene_image = await generator.generate_scene_background(
            scene_number=1,
            environment_prompt="modern office conference room, glass walls, city view"
        )
        
        # Composite
        print("\n🔄 Compositing character into scene...")
        composite_image = await generator.composite_character_in_scene(
            scene_number=1,
            character_name="Sarah Chen",
            position_prompt="Place Sarah Chen standing at the conference table, professional pose"
        )
        
        print(f"✅ Composite image: {composite_image}")
        return composite_image
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return None


async def test_hedra_video():
    """Test Hedra Character-2 for talking video generation."""
    print("\n🎥 Testing Hedra Character-2 Video Generation")
    print("="*50)
    
    fal_key = os.getenv("FAL_KEY") or os.getenv("FAL_API_KEY")
    if not fal_key:
        print("❌ fal.ai API key not set (FAL_KEY or FAL_API_KEY)")
        return None
    
    if not os.getenv("ELEVENLABS_API_KEY"):
        print("⚠️ ELEVENLABS_API_KEY not set - using test audio")
    
    try:
        generator = VideoGeneratorV2()
        generator.set_visual_style(PRESET_STYLES_V2["realistic"])
        
        # Generate character image
        print("\n📸 Generating character image...")
        character_image = await generator.generate_character_image(
            character_name="Test Speaker",
            character_prompt="professional person, friendly face, looking at camera"
        )
        
        # Check for test audio file
        test_audio = "output/test_audio.mp3"
        if not Path(test_audio).exists():
            print("⚠️ No test audio found. Please provide an audio file at output/test_audio.mp3")
            
            # Create a simple test audio if possible
            if os.getenv("ELEVENLABS_API_KEY"):
                print("🎵 Generating test audio with ElevenLabs...")
                from src.rendering.audio_renderer import AudioRenderer
                renderer = AudioRenderer()
                test_audio = await renderer.render_dialogue(
                    character="Test Speaker",
                    text="Hello, this is a test of the video generation system.",
                    emotion="neutral",
                    output_path=test_audio
                )
                if test_audio:
                    print(f"✅ Test audio created: {test_audio}")
                else:
                    print("❌ Could not create test audio")
                    return None
            else:
                return None
        
        # Generate talking video
        print("\n🎬 Generating talking video with Hedra...")
        video_path = await generator.generate_talking_video_with_hedra(
            character_name="Test Speaker",
            scene_number=1,
            audio_path=test_audio
        )
        
        print(f"✅ Video generated: {video_path}")
        return video_path
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return None


async def test_complete_pipeline():
    """Test the complete video generation pipeline."""
    print("\n🚀 Testing Complete Video Pipeline")
    print("="*60)
    
    try:
        # Test each component
        print("\n📋 Step 1: Ideogram V3 Generation")
        images = await test_ideogram_v3()
        
        print("\n📋 Step 2: Flux Kontext Compositing")
        composite = await test_flux_kontext()
        
        print("\n📋 Step 3: Hedra Video Generation")
        video = await test_hedra_video()
        
        print("\n" + "="*60)
        print("✅ PIPELINE TEST COMPLETE")
        print("="*60)
        
        if images:
            print(f"✓ Character image: {images[0]}")
            print(f"✓ Scene background: {images[1]}")
        if composite:
            print(f"✓ Composite image: {composite}")
        if video:
            print(f"✓ Video output: {video}")
        
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Pipeline test failed: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test fal.ai API integration")
    parser.add_argument(
        "--test",
        choices=["ideogram", "kontext", "hedra", "all"],
        default="all",
        help="Which API to test"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    
    args = parser.parse_args()
    
    if args.debug:
        logger.add("logs/fal_api_test.log", level="DEBUG")
    
    # Check API key
    fal_key = os.getenv("FAL_KEY") or os.getenv("FAL_API_KEY")
    if not fal_key:
        print("❌ fal.ai API key not found in environment")
        print("Please set one of the following:")
        print("  export FAL_KEY='your-fal-key'  (recommended)")
        print("  export FAL_API_KEY='your-fal-key'")
        print("\nGet your API key from: https://fal.ai/dashboard")
        return
    
    # Run tests
    if args.test == "ideogram":
        asyncio.run(test_ideogram_v3())
    elif args.test == "kontext":
        asyncio.run(test_flux_kontext())
    elif args.test == "hedra":
        asyncio.run(test_hedra_video())
    else:
        asyncio.run(test_complete_pipeline())


if __name__ == "__main__":
    main()