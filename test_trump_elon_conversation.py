#!/usr/bin/env python3
"""Test script to generate Trump and Elon conversation and save to ./output/audio/conversation"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from rendering.celebrity_voices import CelebrityVoiceGenerator


def test_trump_elon_conversation():
    """Generate Trump and Elon conversation test."""
    print("🎭 Generating Trump vs Elon Conversation Test")
    print("=" * 50)
    
    # Initialize generator
    generator = CelebrityVoiceGenerator()
    
    # Create conversation about technology and America
    conversation = [
        {
            "celebrity": "trump",
            "text": "Elon, your rockets are incredible! SpaceX is making America the leader in space technology.",
            "style": "confident"
        },
        {
            "celebrity": "elon_musk",
            "text": "Thank you. Space exploration is fundamentally important for humanity's future. We need to make life multiplanetary.",
            "style": "default"
        },
        {
            "celebrity": "trump", 
            "text": "And Tesla! Electric cars are the future. American innovation at its finest, believe me.",
            "style": "excited"
        },
        {
            "celebrity": "elon_musk",
            "text": "Well, um, sustainable energy is critical. We're accelerating the world's transition to renewable energy.",
            "style": "default"
        },
        {
            "celebrity": "trump",
            "text": "The jobs you're creating, the technology - it's tremendous! This is what making America great looks like.",
            "style": "confident"
        },
        {
            "celebrity": "elon_musk",
            "text": "Innovation and hard work can solve humanity's greatest challenges. That's what we're working towards.",
            "style": "default"
        }
    ]
    
    # Set output directory
    output_dir = "./output/audio/conversation"
    
    print(f"🎯 Generating conversation with {len(conversation)} exchanges...")
    print(f"📁 Output directory: {output_dir}")
    
    try:
        # Generate the conversation
        manifest = generator.generate_conversation(conversation, output_dir)
        
        print("\n✅ Conversation generated successfully!")
        print(f"🎭 Participants: {', '.join(manifest['participants'])}")
        print(f"🎵 Audio files: {len(manifest['audio_files'])}")
        print(f"⏱️ Total duration: {manifest['total_duration']:.1f} seconds")
        
        print(f"\n🎧 Generated audio files:")
        for i, item in enumerate(manifest['timeline']):
            if item.get('audio_file'):
                speaker = item['celebrity'].replace('_', ' ').title()
                duration = item.get('duration', 0)
                print(f"  {i+1}. {speaker} ({duration:.1f}s): {item['audio_file']}")
                print(f"     Text: \"{item['text'][:60]}...\"")
        
        print(f"\n📂 All files saved to: {output_dir}")
        
        # Verify files exist
        print(f"\n🔍 Verifying generated files:")
        for audio_file in manifest['audio_files']:
            if Path(audio_file).exists():
                file_size = Path(audio_file).stat().st_size / 1024
                print(f"  ✅ {audio_file} ({file_size:.1f} KB)")
            else:
                print(f"  ❌ {audio_file} - File not found!")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to generate conversation: {e}")
        return False


def main():
    """Main test function."""
    print("🚀 Trump & Elon Conversation Test")
    print("=" * 35)
    
    # Check API key
    if not os.getenv('ELEVENLABS_API_KEY'):
        print("❌ ELEVENLABS_API_KEY not found in environment variables")
        print("Please set your ElevenLabs API key:")
        print("export ELEVENLABS_API_KEY='your-api-key-here'")
        return
    
    # Ensure output directory exists
    output_dir = Path("./output/audio/conversation")
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"📁 Output directory ready: {output_dir}")
    
    # Run the test
    success = test_trump_elon_conversation()
    
    if success:
        print(f"\n🎉 Test completed successfully!")
        print(f"🎧 Check the ./output/audio/conversation/ directory for audio files")
        print(f"💡 You can play these files to hear the Trump vs Elon conversation")
    else:
        print(f"\n❌ Test failed. Please check the error messages above.")


if __name__ == "__main__":
    main()