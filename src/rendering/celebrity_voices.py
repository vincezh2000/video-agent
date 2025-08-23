"""Celebrity voice generation using ElevenLabs."""

import os
import asyncio
import random
from typing import Dict, List, Optional, Union
from pathlib import Path
from loguru import logger
import hashlib

# Optional imports for voice synthesis
try:
    from elevenlabs.client import ElevenLabs
    from elevenlabs import Voice, VoiceSettings, save
    ELEVENLABS_AVAILABLE = True
except ImportError:
    ELEVENLABS_AVAILABLE = False
    logger.warning("ElevenLabs not installed. Voice synthesis will be limited.")

from .voice_profiles import CelebrityProfile, get_profile, list_celebrities, get_display_names


class CelebrityVoiceGenerator:
    """Generates celebrity voices using ElevenLabs."""
    
    def __init__(self, api_key: Optional[str] = None, cache_enabled: bool = True):
        """Initialize celebrity voice generator.
        
        Args:
            api_key: ElevenLabs API key
            cache_enabled: Whether to cache generated audio files
        """
        self.api_key = api_key or os.getenv("ELEVENLABS_API_KEY")
        self.cache_enabled = cache_enabled
        self.audio_cache: Dict[str, str] = {}  # Cache for generated audio paths
        self.voice_rotation: Dict[str, int] = {}  # Track voice ID rotation
        
        if not self.api_key:
            logger.error("ElevenLabs API key not found. Set ELEVENLABS_API_KEY environment variable.")
            raise ValueError("ElevenLabs API key is required")
            
        if not ELEVENLABS_AVAILABLE:
            logger.error("ElevenLabs package not installed. Run: pip install elevenlabs")
            raise ImportError("ElevenLabs package is required")
            
        # Initialize ElevenLabs client with API key
        self.client = ElevenLabs(api_key=self.api_key)
        
        logger.info(f"Celebrity voice generator initialized with {len(list_celebrities())} celebrities")
    
    def generate(
        self,
        celebrity: str,
        text: str,
        style: str = "default",
        output_path: Optional[str] = None,
        use_rotation: bool = True
    ) -> str:
        """Generate celebrity voice from text.
        
        Args:
            celebrity: Celebrity name (e.g., 'elon_musk', 'trump')
            text: Text to convert to speech
            style: Speaking style ('default', 'excited', 'calm', 'confident')
            output_path: Optional output path
            use_rotation: Whether to rotate between voice IDs
            
        Returns:
            Path to generated audio file
        """
        # Get celebrity profile
        profile = get_profile(celebrity)
        if not profile:
            available = ", ".join(list_celebrities())
            raise ValueError(f"Celebrity '{celebrity}' not found. Available: {available}")
        
        # Check cache
        cache_key = self._generate_cache_key(celebrity, text, style)
        if self.cache_enabled and cache_key in self.audio_cache:
            logger.debug(f"Using cached audio for {profile.display_name}")
            return self.audio_cache[cache_key]
        
        try:
            # Process text using celebrity's text processor
            processed_text = text
            if profile.text_processor:
                processed_text = profile.text_processor(text)
            
            # Select voice ID (rotate if enabled)
            voice_id = self._select_voice_id(profile, use_rotation)
            
            # Adjust voice settings based on style
            voice_settings = self._adjust_voice_settings(profile.voice_settings, style)
            
            # Generate audio using text_to_speech
            audio = self.client.text_to_speech.convert(
                voice_id=voice_id,
                text=processed_text,
                voice_settings=voice_settings
            )
            
            # Determine output path
            if not output_path:
                output_path = self._generate_output_path(celebrity, cache_key)
            
            # Ensure output directory exists
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Save audio
            save(audio, output_path)
            
            # Cache the result
            if self.cache_enabled:
                self.audio_cache[cache_key] = output_path
            
            logger.info(f"Generated {profile.display_name} voice: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to generate {profile.display_name} voice: {e}")
            raise
    
    async def generate_async(
        self,
        celebrity: str,
        text: str,
        style: str = "default",
        output_path: Optional[str] = None,
        use_rotation: bool = True
    ) -> str:
        """Async version of generate method."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, self.generate, celebrity, text, style, output_path, use_rotation
        )
    
    def generate_batch(
        self,
        texts: List[Dict[str, Union[str, dict]]],
        output_dir: str = "output/audio/batch"
    ) -> List[Dict[str, str]]:
        """Generate multiple celebrity voices in batch.
        
        Args:
            texts: List of generation configs, each containing:
                   - celebrity: str
                   - text: str
                   - style: str (optional)
                   - filename: str (optional)
            output_dir: Output directory
            
        Returns:
            List of results with file paths
        """
        results = []
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        for i, config in enumerate(texts):
            try:
                celebrity = config["celebrity"]
                text = config["text"]
                style = config.get("style", "default")
                filename = config.get("filename", f"batch_{i:03d}.mp3")
                
                output_path = str(Path(output_dir) / filename)
                
                audio_path = self.generate(
                    celebrity=celebrity,
                    text=text,
                    style=style,
                    output_path=output_path
                )
                
                results.append({
                    "celebrity": celebrity,
                    "text": text,
                    "style": style,
                    "audio_path": audio_path,
                    "status": "success"
                })
                
            except Exception as e:
                logger.error(f"Failed to generate batch item {i}: {e}")
                results.append({
                    "celebrity": config.get("celebrity", "unknown"),
                    "text": config.get("text", ""),
                    "style": config.get("style", "default"),
                    "audio_path": None,
                    "status": "error",
                    "error": str(e)
                })
        
        logger.info(f"Batch generation completed: {len(results)} items")
        return results
    
    def generate_conversation(
        self,
        conversation: List[Dict[str, str]],
        output_dir: str = "output/audio/conversation"
    ) -> Dict[str, Union[List, str]]:
        """Generate a conversation between celebrities.
        
        Args:
            conversation: List of dialogue items with 'celebrity' and 'text' keys
            output_dir: Output directory
            
        Returns:
            Conversation manifest with audio files and timing
        """
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        manifest = {
            "conversation_id": hashlib.md5(str(conversation).encode()).hexdigest()[:8],
            "participants": list(set(item["celebrity"] for item in conversation)),
            "audio_files": [],
            "timeline": [],
            "total_duration": 0.0
        }
        
        current_time = 0.0
        
        for i, dialogue in enumerate(conversation):
            celebrity = dialogue["celebrity"]
            text = dialogue["text"]
            style = dialogue.get("style", "default")
            
            # Generate audio
            filename = f"conv_{manifest['conversation_id']}_{i:03d}_{celebrity}.mp3"
            output_path = str(Path(output_dir) / filename)
            
            try:
                audio_path = self.generate(
                    celebrity=celebrity,
                    text=text,
                    style=style,
                    output_path=output_path
                )
                
                # Estimate duration (would get actual duration from audio file in production)
                duration = self._estimate_duration(text)
                
                manifest["audio_files"].append(audio_path)
                manifest["timeline"].append({
                    "index": i,
                    "celebrity": celebrity,
                    "text": text,
                    "style": style,
                    "audio_file": audio_path,
                    "start_time": current_time,
                    "duration": duration
                })
                
                current_time += duration + 0.8  # Add pause between speakers
                
            except Exception as e:
                logger.error(f"Failed to generate conversation item {i}: {e}")
                manifest["timeline"].append({
                    "index": i,
                    "celebrity": celebrity,
                    "text": text,
                    "style": style,
                    "audio_file": None,
                    "start_time": current_time,
                    "duration": 0.0,
                    "error": str(e)
                })
        
        manifest["total_duration"] = current_time
        
        logger.info(f"Generated conversation: {len(manifest['audio_files'])} audio files, "
                   f"{current_time:.1f}s total")
        return manifest
    
    def _select_voice_id(self, profile: CelebrityProfile, use_rotation: bool) -> str:
        """Select voice ID from profile, optionally rotating."""
        if not use_rotation or len(profile.voice_ids) == 1:
            return profile.primary_voice_id
        
        # Rotate through voice IDs
        celebrity = profile.name
        if celebrity not in self.voice_rotation:
            self.voice_rotation[celebrity] = 0
        
        voice_id = profile.voice_ids[self.voice_rotation[celebrity]]
        self.voice_rotation[celebrity] = (self.voice_rotation[celebrity] + 1) % len(profile.voice_ids)
        
        return voice_id
    
    def _adjust_voice_settings(self, base_settings: VoiceSettings, style: str) -> VoiceSettings:
        """Adjust voice settings based on speaking style."""
        # Create a copy of base settings
        settings_dict = {
            "stability": base_settings.stability,
            "similarity_boost": base_settings.similarity_boost,
            "style": base_settings.style,
            "use_speaker_boost": base_settings.use_speaker_boost
        }
        
        # Adjust based on style
        if style == "excited":
            settings_dict["stability"] = max(0.1, settings_dict["stability"] - 0.2)
            settings_dict["style"] = min(1.0, settings_dict["style"] + 0.3)
        elif style == "calm":
            # 为了更有磁性的声音：高stability + 高similarity + 低style
            settings_dict["stability"] = 0.85  # 很稳定，磁性声音的关键
            settings_dict["similarity_boost"] = 1.0  # 最大化音色丰富度
            settings_dict["style"] = 0.0  # 最小变化，更深沉有磁性
        elif style == "confident":
            settings_dict["stability"] = min(0.8, settings_dict["stability"] + 0.1)
            settings_dict["similarity_boost"] = min(1.0, settings_dict["similarity_boost"] + 0.1)
        elif style == "magnetic":
            # 专门的磁性声音设置
            settings_dict["stability"] = 0.9   # 极高稳定性
            settings_dict["similarity_boost"] = 1.0  # 最大相似度
            settings_dict["style"] = 0.05  # 极少变化，保持深沉磁性
        
        return VoiceSettings(**settings_dict)
    
    def _generate_cache_key(self, celebrity: str, text: str, style: str) -> str:
        """Generate cache key for audio file."""
        content = f"{celebrity}_{text}_{style}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _generate_output_path(self, celebrity: str, cache_key: str) -> str:
        """Generate output path for audio file."""
        output_dir = Path(f"output/audio/celebrities/{celebrity}")
        output_dir.mkdir(parents=True, exist_ok=True)
        return str(output_dir / f"{cache_key}.mp3")
    
    def _estimate_duration(self, text: str) -> float:
        """Estimate audio duration from text."""
        # Rough estimate: 150 words per minute
        words = len(text.split())
        return (words / 150) * 60 + 0.5
    
    def list_available_celebrities(self) -> Dict[str, str]:
        """Get list of available celebrities with display names."""
        return get_display_names()
    
    def get_celebrity_info(self, celebrity: str) -> Optional[Dict]:
        """Get information about a celebrity."""
        profile = get_profile(celebrity)
        if not profile:
            return None
        
        return {
            "name": profile.name,
            "display_name": profile.display_name,
            "voice_ids": profile.voice_ids,
            "primary_voice": profile.primary_voice_id,
            "speaking_patterns": profile.speaking_patterns,
            "has_text_processor": profile.text_processor is not None
        }
    
    def clear_cache(self):
        """Clear audio cache."""
        self.audio_cache.clear()
        logger.info("Audio cache cleared")


# Convenience functions for quick usage
def generate_elon_voice(text: str, output_path: Optional[str] = None, style: str = "default") -> str:
    """Quick function to generate Elon Musk voice."""
    generator = CelebrityVoiceGenerator()
    return generator.generate("elon_musk", text, style, output_path)


def generate_trump_voice(text: str, output_path: Optional[str] = None, style: str = "default") -> str:
    """Quick function to generate Trump voice."""
    generator = CelebrityVoiceGenerator()
    return generator.generate("trump", text, style, output_path)


def quick_conversation(elon_text: str, trump_text: str, output_dir: str = "output/conversation") -> Dict:
    """Quick function to generate a conversation between Elon and Trump."""
    generator = CelebrityVoiceGenerator()
    conversation = [
        {"celebrity": "elon_musk", "text": elon_text},
        {"celebrity": "trump", "text": trump_text}
    ]
    return generator.generate_conversation(conversation, output_dir)