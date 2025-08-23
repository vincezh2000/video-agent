#!/usr/bin/env python3
"""Test script for celebrity voice generation."""

import os
import sys
from pathlib import Path

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from rendering.celebrity_voices import CelebrityVoiceGenerator, generate_elon_voice, generate_trump_voice, quick_conversation
from rendering.voice_profiles import list_celebrities, get_display_names


def test_basic_functionality():
    """Test basic voice generation functionality."""
    print("🎯 Testing Celebrity Voice Generator")
    print("=" * 50)
    
    # Check if API key is available
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        print("❌ ELEVENLABS_API_KEY not found in environment variables")
        print("Please set your ElevenLabs API key:")
        print("export ELEVENLABS_API_KEY='your-api-key-here'")
        return False
    
    print(f"✅ ElevenLabs API key found: {api_key[:8]}...")
    
    try:
        # Initialize generator
        generator = CelebrityVoiceGenerator()
        print(f"✅ Generator initialized successfully")
        
        # List available celebrities
        celebrities = generator.list_available_celebrities()
        print(f"✅ Available celebrities: {len(celebrities)}")
        for name, display_name in celebrities.items():
            print(f"   - {name}: {display_name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to initialize generator: {e}")
        return False


def test_elon_voice():
    """Test Elon Musk voice generation."""
    print("\n🚀 Testing Elon Musk Voice")
    print("=" * 30)
    
    try:
        # Test phrases
        test_phrases = [
            "The first step is to establish that something is possible; then probability will occur.",
            "We need to make life multiplanetary. Mars is the next logical step.",
            "Artificial intelligence is our biggest existential threat, but also our greatest opportunity."
        ]
        
        generator = CelebrityVoiceGenerator()
        
        for i, phrase in enumerate(test_phrases):
            print(f"Generating phrase {i+1}: {phrase[:50]}...")
            
            # Generate with different styles
            for style in ["default", "excited", "calm"]:
                try:
                    audio_path = generator.generate(
                        celebrity="elon_musk",
                        text=phrase,
                        style=style,
                        output_path=f"output/test/elon_test_{i+1}_{style}.mp3"
                    )
                    print(f"  ✅ {style}: {audio_path}")
                    
                    # Check if file was created
                    if Path(audio_path).exists():
                        file_size = Path(audio_path).stat().st_size
                        print(f"     File size: {file_size} bytes")
                    else:
                        print(f"     ⚠️ File not found at {audio_path}")
                        
                except Exception as e:
                    print(f"  ❌ {style}: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Elon voice test failed: {e}")
        return False


def test_trump_voice():
    """Test Trump voice generation."""
    print("\n🇺🇸 Testing Trump Voice")
    print("=" * 25)
    
    try:
        test_phrases = [
            "This is going to be tremendous, believe me.",
            "Nobody knows more about deals than me, nobody.",
            "We're going to make America great again, and it's going to be fantastic."
        ]
        
        generator = CelebrityVoiceGenerator()
        
        for i, phrase in enumerate(test_phrases):
            print(f"Generating phrase {i+1}: {phrase[:50]}...")
            
            # Generate with different styles
            for style in ["default", "confident", "excited"]:
                try:
                    audio_path = generator.generate(
                        celebrity="trump",
                        text=phrase,
                        style=style,
                        output_path=f"output/test/trump_test_{i+1}_{style}.mp3"
                    )
                    print(f"  ✅ {style}: {audio_path}")
                    
                    # Check file
                    if Path(audio_path).exists():
                        file_size = Path(audio_path).stat().st_size
                        print(f"     File size: {file_size} bytes")
                        
                except Exception as e:
                    print(f"  ❌ {style}: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Trump voice test failed: {e}")
        return False


def test_conversation():
    """Test conversation generation."""
    print("\n💬 Testing Conversation Generation")
    print("=" * 35)
    
    try:
        conversation = [
            {"celebrity": "elon_musk", "text": "Mars colonization is the key to humanity's future.", "style": "excited"},
            {"celebrity": "trump", "text": "That's tremendous, Elon. But we need to make America great first.", "style": "confident"},
            {"celebrity": "elon_musk", "text": "Well, um, we can do both simultaneously. Technology helps everyone.", "style": "default"},
            {"celebrity": "trump", "text": "You're absolutely right. Space technology, it's going to be incredible.", "style": "excited"}
        ]
        
        generator = CelebrityVoiceGenerator()
        manifest = generator.generate_conversation(conversation, "output/test/conversation")
        
        print(f"✅ Conversation generated:")
        print(f"   Participants: {', '.join(manifest['participants'])}")
        print(f"   Audio files: {len(manifest['audio_files'])}")
        print(f"   Total duration: {manifest['total_duration']:.1f}s")
        
        # Check timeline
        for item in manifest['timeline']:
            status = "✅" if item.get('audio_file') else "❌"
            print(f"   {status} {item['celebrity']}: {item['text'][:40]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Conversation test failed: {e}")
        return False


def test_batch_generation():
    """Test batch generation."""
    print("\n📦 Testing Batch Generation")
    print("=" * 30)
    
    try:
        batch_configs = [
            {"celebrity": "elon_musk", "text": "Tesla is accelerating the world's transition to sustainable transport.", "style": "default", "filename": "elon_tesla.mp3"},
            {"celebrity": "trump", "text": "This deal is going to be the best deal in the history of deals.", "style": "confident", "filename": "trump_deal.mp3"},
            {"celebrity": "elon_musk", "text": "SpaceX is making space travel routine.", "style": "excited", "filename": "elon_spacex.mp3"},
            {"celebrity": "trump", "text": "America first, space second.", "style": "default", "filename": "trump_america.mp3"}
        ]
        
        generator = CelebrityVoiceGenerator()
        results = generator.generate_batch(batch_configs, "output/test/batch")
        
        print(f"✅ Batch generation completed: {len(results)} items")
        
        success_count = sum(1 for r in results if r['status'] == 'success')
        error_count = len(results) - success_count
        
        print(f"   Successful: {success_count}")
        print(f"   Errors: {error_count}")
        
        for result in results:
            status = "✅" if result['status'] == 'success' else "❌"
            print(f"   {status} {result['celebrity']}: {result['text'][:30]}...")
            if result['status'] == 'error':
                print(f"      Error: {result.get('error', 'Unknown error')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Batch test failed: {e}")
        return False


def test_convenience_functions():
    """Test convenience functions."""
    print("\n⚡ Testing Convenience Functions")
    print("=" * 35)
    
    try:
        # Test quick functions
        elon_text = "AI safety is critically important for humanity's future."
        trump_text = "AI is going to be tremendous for America, believe me."
        
        print("Testing generate_elon_voice()...")
        elon_path = generate_elon_voice(elon_text, "output/test/quick_elon.mp3")
        print(f"✅ Elon: {elon_path}")
        
        print("Testing generate_trump_voice()...")
        trump_path = generate_trump_voice(trump_text, "output/test/quick_trump.mp3")
        print(f"✅ Trump: {trump_path}")
        
        print("Testing quick_conversation()...")
        conv_manifest = quick_conversation(
            elon_text="The future of AI is looking very promising.",
            trump_text="AI is going to make America even greater than it already is.",
            output_dir="output/test/quick_conversation"
        )
        print(f"✅ Quick conversation: {len(conv_manifest['audio_files'])} files")
        
        return True
        
    except Exception as e:
        print(f"❌ Convenience functions test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("🎪 Celebrity Voice Generator Test Suite")
    print("=" * 50)
    
    # Create output directory
    Path("output/test").mkdir(parents=True, exist_ok=True)
    
    tests = [
        ("Basic Functionality", test_basic_functionality),
        ("Elon Musk Voice", test_elon_voice),
        ("Trump Voice", test_trump_voice),
        ("Conversation Generation", test_conversation),
        ("Batch Generation", test_batch_generation),
        ("Convenience Functions", test_convenience_functions)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"Running: {test_name}")
        print('='*60)
        
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*60}")
    print("🏁 TEST SUMMARY")
    print('='*60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Celebrity voice generation is working correctly.")
    else:
        print(f"⚠️ {total - passed} tests failed. Check the logs above for details.")
    
    print(f"\n📁 Generated audio files are in: output/test/")


if __name__ == "__main__":
    main()