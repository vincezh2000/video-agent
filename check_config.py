#!/usr/bin/env python3
"""Configuration checker for all APIs and environment variables."""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_config():
    """Check all API configurations."""
    print("\n" + "="*60)
    print("🔍 CONFIGURATION CHECK")
    print("="*60)
    
    config_status = {
        "OpenAI": False,
        "ElevenLabs": False,
        "fal.ai": False
    }
    
    # Check OpenAI API
    print("\n1️⃣ OpenAI API Configuration:")
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        print(f"   ✅ OPENAI_API_KEY is set ({openai_key[:8]}...{openai_key[-4:]})")
        config_status["OpenAI"] = True
    else:
        print("   ❌ OPENAI_API_KEY not found")
        print("   → Required for episode generation")
        print("   → Set in .env: OPENAI_API_KEY=your-key")
    
    # Check ElevenLabs API
    print("\n2️⃣ ElevenLabs API Configuration:")
    elevenlabs_key = os.getenv("ELEVENLABS_API_KEY")
    if elevenlabs_key:
        print(f"   ✅ ELEVENLABS_API_KEY is set ({elevenlabs_key[:8]}...{elevenlabs_key[-4:]})")
        config_status["ElevenLabs"] = True
    else:
        print("   ⚠️ ELEVENLABS_API_KEY not found")
        print("   → Optional for voice synthesis")
        print("   → Set in .env: ELEVENLABS_API_KEY=your-key")
    
    # Check fal.ai API
    print("\n3️⃣ fal.ai API Configuration:")
    fal_key = os.getenv("FAL_KEY")
    fal_api_key = os.getenv("FAL_API_KEY")
    
    if fal_key:
        print(f"   ✅ FAL_KEY is set (recommended) ({fal_key[:8] if len(fal_key) > 8 else fal_key}...)")
        config_status["fal.ai"] = True
    elif fal_api_key:
        print(f"   ✅ FAL_API_KEY is set (alternative) ({fal_api_key[:8] if len(fal_api_key) > 8 else fal_api_key}...)")
        config_status["fal.ai"] = True
    else:
        print("   ⚠️ fal.ai API key not found")
        print("   → Optional for video generation")
        print("   → Set in .env: FAL_KEY=your-key (recommended)")
        print("   → Or: FAL_API_KEY=your-key")
        print("   → Get key from: https://fal.ai/dashboard")
    
    # Check Python packages
    print("\n4️⃣ Python Package Dependencies:")
    packages_status = {}
    
    # Check required packages
    required_packages = {
        "openai": "OpenAI API client",
        "fal_client": "fal.ai API client",
        "elevenlabs": "ElevenLabs voice synthesis",
        "loguru": "Advanced logging",
        "pydantic": "Data validation",
        "aiohttp": "Async HTTP client",
        "pillow": "Image processing"
    }
    
    for package, description in required_packages.items():
        try:
            __import__(package.replace("-", "_"))
            packages_status[package] = True
            print(f"   ✅ {package}: {description}")
        except ImportError:
            packages_status[package] = False
            print(f"   ❌ {package}: {description} - Run: pip install {package}")
    
    # Check FFmpeg
    print("\n5️⃣ System Dependencies:")
    import subprocess
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("   ✅ FFmpeg is installed")
        else:
            print("   ❌ FFmpeg error")
    except FileNotFoundError:
        print("   ❌ FFmpeg not found - Required for video assembly")
        print("   → Install: brew install ffmpeg (macOS)")
        print("   → Or: apt-get install ffmpeg (Linux)")
    
    # Summary
    print("\n" + "="*60)
    print("📊 CONFIGURATION SUMMARY")
    print("="*60)
    
    # Core functionality status
    print("\n🎬 Episode Generation:")
    if config_status["OpenAI"]:
        print("   ✅ Ready - OpenAI API configured")
    else:
        print("   ❌ Not ready - OpenAI API required")
    
    print("\n🎵 Voice Synthesis:")
    if config_status["ElevenLabs"]:
        print("   ✅ Ready - ElevenLabs API configured")
    else:
        print("   ⚠️ Disabled - ElevenLabs API not configured")
    
    print("\n🎥 Video Generation:")
    if config_status["fal.ai"]:
        print("   ✅ Ready - fal.ai API configured")
    else:
        print("   ⚠️ Disabled - fal.ai API not configured")
    
    # Environment file check
    print("\n📁 Environment Files:")
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if env_file.exists():
        print(f"   ✅ .env file exists ({env_file.absolute()})")
    else:
        print("   ❌ .env file not found")
        print("   → Copy .env.example to .env and add your API keys")
    
    if env_example.exists():
        print(f"   ✅ .env.example file exists")
    else:
        print("   ⚠️ .env.example file not found")
    
    # Recommendations
    print("\n💡 RECOMMENDATIONS:")
    
    if not config_status["OpenAI"]:
        print("\n1. Set up OpenAI API (required):")
        print("   - Get API key from: https://platform.openai.com/api-keys")
        print("   - Add to .env: OPENAI_API_KEY=your-key")
    
    if not config_status["ElevenLabs"] and not config_status["fal.ai"]:
        print("\n2. For full multimedia features, set up:")
        print("   - ElevenLabs for voice: https://elevenlabs.io")
        print("   - fal.ai for video: https://fal.ai/dashboard")
    
    missing_packages = [pkg for pkg, status in packages_status.items() if not status]
    if missing_packages:
        print(f"\n3. Install missing Python packages:")
        print(f"   pip install {' '.join(missing_packages)}")
    
    print("\n" + "="*60)
    
    # Return status code
    if config_status["OpenAI"]:
        return 0  # At minimum, OpenAI is configured
    else:
        return 1  # Core functionality not available


if __name__ == "__main__":
    sys.exit(check_config())