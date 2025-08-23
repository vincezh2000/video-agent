#!/usr/bin/env python3
"""Examples demonstrating celebrity voice generation usage."""

import os
import sys
from pathlib import Path

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from rendering.celebrity_voices import CelebrityVoiceGenerator, generate_elon_voice, generate_trump_voice, quick_conversation


def example_1_basic_usage():
    """Example 1: Basic voice generation."""
    print("🎯 Example 1: Basic Voice Generation")
    print("=" * 40)
    
    # Initialize generator
    generator = CelebrityVoiceGenerator()
    
    # Generate Elon Musk voice
    elon_audio = generator.generate(
        celebrity="elon_musk",
        text="The path to sustainable energy is through electric vehicles and renewable power generation.",
        style="default"
    )
    print(f"Elon audio generated: {elon_audio}")
    
    # Generate Trump voice
    trump_audio = generator.generate(
        celebrity="trump",
        text="This is going to be the most incredible breakthrough in American technology.",
        style="confident"
    )
    print(f"Trump audio generated: {trump_audio}")


def example_2_different_styles():
    """Example 2: Different speaking styles."""
    print("\n🎭 Example 2: Different Speaking Styles")
    print("=" * 40)
    
    generator = CelebrityVoiceGenerator()
    text = "Artificial intelligence will transform everything we know about technology."
    
    styles = ["default", "excited", "calm", "confident"]
    
    for celebrity in ["elon_musk", "trump"]:
        print(f"\n{celebrity.replace('_', ' ').title()}:")
        for style in styles:
            try:
                audio_path = generator.generate(
                    celebrity=celebrity,
                    text=text,
                    style=style,
                    output_path=f"output/examples/{celebrity}_{style}.mp3"
                )
                print(f"  {style}: {audio_path}")
            except Exception as e:
                print(f"  {style}: Error - {e}")


def example_3_conversation():
    """Example 3: Generate a conversation between celebrities."""
    print("\n💬 Example 3: Celebrity Conversation")
    print("=" * 40)
    
    # Define a tech debate conversation
    tech_debate = [
        {
            "celebrity": "elon_musk",
            "text": "I think we should focus on making life multiplanetary. Mars is the obvious next step for humanity.",
            "style": "excited"
        },
        {
            "celebrity": "trump", 
            "text": "That's tremendous, Elon, but we need to fix Earth first. America needs the best technology right here.",
            "style": "confident"
        },
        {
            "celebrity": "elon_musk",
            "text": "Well, um, I think we can do both simultaneously. SpaceX technology actually helps terrestrial applications too.",
            "style": "default"
        },
        {
            "celebrity": "trump",
            "text": "You're absolutely right. Space technology, electric cars - it's all going to make America incredible.",
            "style": "excited"
        },
        {
            "celebrity": "elon_musk", 
            "text": "Exactly. The future is looking very bright for sustainable technology and space exploration.",
            "style": "calm"
        }
    ]
    
    generator = CelebrityVoiceGenerator()
    manifest = generator.generate_conversation(tech_debate, "output/examples/tech_debate")
    
    print(f"Conversation generated:")
    print(f"  Participants: {', '.join(manifest['participants'])}")
    print(f"  Total duration: {manifest['total_duration']:.1f} seconds")
    print(f"  Audio files: {len(manifest['audio_files'])}")
    
    # Show timeline
    print("\nConversation timeline:")
    for item in manifest['timeline']:
        print(f"  {item['start_time']:.1f}s - {item['celebrity']}: {item['text'][:50]}...")


def example_4_batch_quotes():
    """Example 4: Generate famous quotes in batch."""
    print("\n📦 Example 4: Batch Quote Generation")
    print("=" * 40)
    
    famous_quotes = [
        {
            "celebrity": "elon_musk",
            "text": "When something is important enough, you do it even if the odds are not in your favor.",
            "style": "default",
            "filename": "elon_quote_1.mp3"
        },
        {
            "celebrity": "elon_musk", 
            "text": "I think it's very important to have a feedback loop, where you're constantly thinking about what you've done and how you could be doing it better.",
            "style": "calm",
            "filename": "elon_quote_2.mp3"
        },
        {
            "celebrity": "trump",
            "text": "The point is that you can't be too greedy.",
            "style": "confident", 
            "filename": "trump_quote_1.mp3"
        },
        {
            "celebrity": "trump",
            "text": "I like thinking big. If you're going to be thinking anything, you might as well think big.",
            "style": "excited",
            "filename": "trump_quote_2.mp3"
        }
    ]
    
    generator = CelebrityVoiceGenerator()
    results = generator.generate_batch(famous_quotes, "output/examples/famous_quotes")
    
    print("Batch generation results:")
    for result in results:
        status = "✅" if result['status'] == 'success' else "❌"
        celebrity_name = result['celebrity'].replace('_', ' ').title()
        print(f"  {status} {celebrity_name}: {result['text'][:40]}...")
        if result['status'] == 'success':
            print(f"     → {result['audio_path']}")


def example_5_convenience_functions():
    """Example 5: Using convenience functions."""
    print("\n⚡ Example 5: Convenience Functions")
    print("=" * 40)
    
    # Quick Elon voice
    elon_audio = generate_elon_voice(
        "Tesla's mission is to accelerate the world's transition to sustainable energy.",
        "output/examples/quick_elon.mp3"
    )
    print(f"Quick Elon: {elon_audio}")
    
    # Quick Trump voice
    trump_audio = generate_trump_voice(
        "We're going to have the best electric cars, believe me.",
        "output/examples/quick_trump.mp3"
    )
    print(f"Quick Trump: {trump_audio}")
    
    # Quick conversation
    conversation_manifest = quick_conversation(
        elon_text="Neural networks are the future of artificial intelligence.",
        trump_text="AI is going to make American businesses the most successful in the world.",
        output_dir="output/examples/quick_ai_chat"
    )
    print(f"Quick conversation: {len(conversation_manifest['audio_files'])} files generated")


def example_6_voice_rotation():
    """Example 6: Voice ID rotation for variety."""
    print("\n🔄 Example 6: Voice ID Rotation")
    print("=" * 40)
    
    generator = CelebrityVoiceGenerator()
    text = "This is a test of voice rotation to add variety to the generated speech."
    
    # Generate same text multiple times to see rotation
    print("Generating same text with voice rotation:")
    for i in range(3):
        audio_path = generator.generate(
            celebrity="elon_musk",
            text=text,
            style="default",
            output_path=f"output/examples/rotation_test_{i+1}.mp3",
            use_rotation=True
        )
        print(f"  Generation {i+1}: {audio_path}")
        
    print("\nNote: Each generation may use a different voice ID for variety.")


def example_7_celebrity_info():
    """Example 7: Get celebrity information."""
    print("\n📊 Example 7: Celebrity Information")
    print("=" * 40)
    
    generator = CelebrityVoiceGenerator()
    
    # List all celebrities
    celebrities = generator.list_available_celebrities()
    print("Available celebrities:")
    for name, display_name in celebrities.items():
        print(f"  {name}: {display_name}")
    
    # Get detailed info for specific celebrities
    for celebrity in ["elon_musk", "trump"]:
        info = generator.get_celebrity_info(celebrity)
        if info:
            print(f"\n{info['display_name']} details:")
            print(f"  Voice IDs: {len(info['voice_ids'])}")
            print(f"  Primary voice: {info['primary_voice']}")
            print(f"  Has text processor: {info['has_text_processor']}")
            if info['speaking_patterns']:
                print(f"  Speaking patterns: {list(info['speaking_patterns'].keys())}")


def main():
    """Run all examples."""
    print("🎪 Celebrity Voice Generator Examples")
    print("=" * 50)
    
    # Check API key
    if not os.getenv("ELEVENLABS_API_KEY"):
        print("❌ Please set ELEVENLABS_API_KEY environment variable")
        print("export ELEVENLABS_API_KEY='your-api-key-here'")
        return
    
    # Create output directory
    Path("output/examples").mkdir(parents=True, exist_ok=True)
    
    examples = [
        example_1_basic_usage,
        example_2_different_styles, 
        example_3_conversation,
        example_4_batch_quotes,
        example_5_convenience_functions,
        example_6_voice_rotation,
        example_7_celebrity_info
    ]
    
    for example_func in examples:
        try:
            example_func()
        except Exception as e:
            print(f"❌ Example failed: {e}")
            continue
    
    print(f"\n🎉 Examples completed! Check output/examples/ for generated audio files.")


if __name__ == "__main__":
    main()