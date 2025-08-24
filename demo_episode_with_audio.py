#!/usr/bin/env python3
"""Demo script to generate an episode with celebrity voice audio."""

import asyncio
import json
import os
from pathlib import Path
from datetime import datetime
from loguru import logger

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Import the Showrunner system
from src.main import ShowrunnerSystem


async def generate_tech_debate_episode():
    """Generate a tech debate episode with Elon and Trump voices."""
    
    # Configure logging
    logger.add("logs/audio_episode_generation.log", rotation="10 MB")
    
    # Episode configuration
    episode_config = {
        "title": "The Great Tech Debate",
        "synopsis": "Tech titans debate the future of AI and space exploration in a heated discussion about humanity's priorities.",
        "themes": ["technology", "innovation", "future", "debate"],
        "genre": "drama",
        "tone": "tense",
        "simulation_hours": 0.01,  # Very short simulation for demo
        "plot_pattern": "ABAB"
    }
    
    # Characters designed to match celebrity voices
    characters = [
        {
            "name": "Elon Tesla",  # Will map to Elon Musk voice
            "backstory": "Visionary tech entrepreneur focused on Mars colonization and sustainable energy.",
            "personality": {
                "openness": 0.95,
                "conscientiousness": 0.85,
                "extraversion": 0.6,
                "agreeableness": 0.5,
                "neuroticism": 0.4
            },
            "age": 45,
            "occupation": "Tech Leader"
        },
        {
            "name": "Donald Magnus",  # Will map to Trump voice
            "backstory": "Business magnate turned political figure with strong opinions on American innovation.",
            "personality": {
                "openness": 0.4,
                "conscientiousness": 0.6,
                "extraversion": 0.9,
                "agreeableness": 0.3,
                "neuroticism": 0.3
            },
            "age": 70,
            "occupation": "Businessman"
        },
        {
            "name": "Sarah Chen",  # Will use default voice
            "backstory": "AI researcher trying to mediate between competing visions.",
            "personality": {
                "openness": 0.8,
                "conscientiousness": 0.9,
                "extraversion": 0.5,
                "agreeableness": 0.8,
                "neuroticism": 0.5
            },
            "age": 35,
            "occupation": "AI Researcher"
        }
    ]
    
    # Character to celebrity voice mapping
    character_voice_mapping = {
        "Elon Tesla": "elon_musk",
        "Donald Magnus": "trump",
        # Sarah Chen will use default voice
    }
    
    # Initialize the system
    logger.info("Initializing Showrunner system...")
    system = ShowrunnerSystem()
    
    # Check if audio is available
    if not system.audio_renderer:
        logger.warning("Audio renderer not available. Make sure ELEVENLABS_API_KEY is set.")
        print("\n⚠️ Audio features not available. Set ELEVENLABS_API_KEY to enable voice generation.")
    
    try:
        print("\n" + "="*60)
        print("🎬 GENERATING EPISODE WITH CELEBRITY VOICES")
        print("="*60)
        print(f"Title: {episode_config['title']}")
        print(f"Genre: {episode_config['genre']}")
        print(f"Characters: {', '.join([c['name'] for c in characters])}")
        print(f"Voice Mapping: {json.dumps(character_voice_mapping, indent=2)}")
        print("="*60)
        
        # Generate the episode with audio
        episode = await asyncio.wait_for(
            system.generate_episode(
                title=episode_config["title"],
                synopsis=episode_config["synopsis"],
                themes=episode_config["themes"],
                genre=episode_config["genre"],
                tone=episode_config["tone"],
                characters=characters,
                simulation_hours=episode_config["simulation_hours"],
                plot_pattern=episode_config["plot_pattern"],
                generate_audio=True,  # Enable audio generation
                character_voice_mapping=character_voice_mapping
            ),
            timeout=600.0  # 10 minute timeout
        )
        
        # Save the episode
        output_dir = Path("output/episodes_with_audio")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        episode_file = output_dir / f"tech_debate_{timestamp}.json"
        
        with open(episode_file, 'w') as f:
            json.dump(episode, f, indent=2)
        
        print("\n" + "="*60)
        print("✅ EPISODE GENERATION COMPLETE")
        print("="*60)
        
        # Display summary
        print(f"📝 Title: {episode.get('title')}")
        print(f"🎭 Genre: {episode.get('genre')}")
        print(f"📺 Scenes: {episode.get('total_scenes', 0)}")
        
        # Audio summary
        if episode.get("audio_generated"):
            audio_manifest = episode.get("audio_manifest", {})
            print(f"\n🎵 AUDIO GENERATION SUCCESSFUL")
            print(f"⏱️ Total Duration: {audio_manifest.get('total_duration', 0):.1f} seconds")
            print(f"🎧 Audio Files: {len(audio_manifest.get('scenes', []))} scenes")
            
            # Show character voices used
            if "character_voices" in audio_manifest:
                print(f"\n🎤 Character Voices:")
                for char, voice in audio_manifest["character_voices"].items():
                    print(f"   - {char}: {voice}")
            
            # Show first few dialogue lines
            if episode.get("scenes") and len(episode["scenes"]) > 0:
                first_scene = episode["scenes"][0]
                if "dialogue" in first_scene and len(first_scene["dialogue"]) > 0:
                    print(f"\n📝 Sample Dialogue (Scene 1):")
                    for i, line in enumerate(first_scene["dialogue"][:3]):
                        character = line.get("character", "Unknown")
                        text = line.get("line", "...")
                        voice = character_voice_mapping.get(character, "default")
                        print(f"   {i+1}. [{voice}] {character}: {text[:80]}...")
            
            # Audio file locations
            if "episode_id" in audio_manifest:
                audio_dir = Path("output/audio/episodes") / audio_manifest["episode_id"]
                print(f"\n📁 Audio files saved to: {audio_dir}")
                
                # List first few audio files
                if audio_dir.exists():
                    audio_files = list(audio_dir.glob("**/*.mp3"))[:5]
                    if audio_files:
                        print(f"\n🎵 Sample audio files:")
                        for audio_file in audio_files:
                            print(f"   - {audio_file.name}")
        else:
            print(f"\n⚠️ Audio generation was not performed or failed")
            if "audio_error" in episode:
                print(f"   Error: {episode['audio_error']}")
            elif "audio_note" in episode:
                print(f"   Note: {episode['audio_note']}")
        
        print(f"\n💾 Episode saved to: {episode_file}")
        print("="*60)
        
        return episode
        
    except asyncio.TimeoutError:
        logger.warning("Episode generation timed out")
        print("\n⚠️ Episode generation timed out after 10 minutes")
        return None
        
    except Exception as e:
        logger.error(f"Episode generation failed: {e}")
        print(f"\n❌ Episode generation failed: {e}")
        import traceback
        traceback.print_exc()
        return None
        
    finally:
        await system.close()


async def test_audio_only():
    """Test just the audio generation without full episode."""
    
    print("\n🎤 Testing Audio Generation Only")
    print("="*40)
    
    # Sample scene data
    test_scene = {
        "scene_id": "test_scene_001",
        "scene_number": 1,
        "act_number": 1,
        "location": "Tech Conference",
        "dialogue": [
            {
                "character": "Elon Tesla",
                "line": "The future of humanity depends on becoming a multiplanetary species. Mars is our next home.",
                "emotion": "confident"
            },
            {
                "character": "Donald Magnus",
                "line": "That's tremendous, just tremendous! But we need to make America the leader in space!",
                "emotion": "excited"
            },
            {
                "character": "Elon Tesla",
                "line": "Well, um, it's not about countries anymore. It's about humanity working together.",
                "emotion": "calm"
            },
            {
                "character": "Donald Magnus", 
                "line": "Nobody knows more about making deals than me. We'll get the best space deals!",
                "emotion": "confident"
            }
        ]
    }
    
    # Initialize audio renderer
    from src.rendering.episode_audio_renderer import EpisodeAudioRenderer
    
    try:
        renderer = EpisodeAudioRenderer()
        
        # Set up voice mappings
        renderer.map_character_to_celebrity("Elon Tesla", "elon_musk")
        renderer.map_character_to_celebrity("Donald Magnus", "trump")
        
        # Generate audio for scene
        print("🎬 Generating audio for test scene...")
        manifest = await renderer.render_scene_with_celebrities(
            scene_data=test_scene,
            output_dir="output/audio/test_scene"
        )
        
        print(f"✅ Audio generated successfully!")
        print(f"📁 Files: {len(manifest['audio_files'])}")
        print(f"⏱️ Duration: {manifest['total_duration']:.1f}s")
        print(f"🎤 Voice types: {json.dumps(manifest['voice_types'], indent=2)}")
        
        return manifest
        
    except Exception as e:
        print(f"❌ Audio test failed: {e}")
        return None


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate episode with celebrity voice audio")
    parser.add_argument(
        "--mode",
        choices=["full", "audio-test"],
        default="full",
        help="Generation mode"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    
    args = parser.parse_args()
    
    if args.debug:
        logger.add("logs/debug_audio.log", level="DEBUG")
    
    # Check for API keys
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not found in environment variables")
        print("Please set it in your .env file or environment")
        return
    
    if not os.getenv("ELEVENLABS_API_KEY"):
        print("⚠️ ELEVENLABS_API_KEY not found")
        print("Audio features will be disabled. To enable:")
        print("export ELEVENLABS_API_KEY='your-api-key-here'")
        response = input("\nContinue without audio? (y/n): ")
        if response.lower() != 'y':
            return
    
    # Run generation
    if args.mode == "full":
        asyncio.run(generate_tech_debate_episode())
    else:
        asyncio.run(test_audio_only())


if __name__ == "__main__":
    main()