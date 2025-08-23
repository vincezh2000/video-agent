"""Audio rendering module for voice synthesis and sound effects."""

import os
import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path
from loguru import logger

# Optional imports for voice synthesis
try:
    from elevenlabs import Voice, VoiceSettings, generate, save
    ELEVENLABS_AVAILABLE = True
except ImportError:
    ELEVENLABS_AVAILABLE = False
    logger.warning("ElevenLabs not installed. Voice synthesis will be limited.")


@dataclass
class VoiceProfile:
    """Voice profile for a character."""
    character_name: str
    voice_id: str  # ElevenLabs voice ID or preset name
    pitch: float = 1.0  # Pitch adjustment
    speed: float = 1.0  # Speed adjustment
    emotion_default: str = "neutral"
    accent: Optional[str] = None
    age_group: str = "adult"  # child, teen, adult, elderly
    
    # Voice characteristics
    stability: float = 0.5  # 0-1, how consistent the voice is
    similarity_boost: float = 0.5  # 0-1, how closely to match the voice
    style: float = 0.0  # 0-1, style exaggeration
    use_speaker_boost: bool = True


class AudioRenderer:
    """Renders audio for episodes."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize audio renderer.
        
        Args:
            api_key: ElevenLabs API key
        """
        self.api_key = api_key or os.getenv("ELEVENLABS_API_KEY")
        self.voice_profiles: Dict[str, VoiceProfile] = {}
        self.audio_cache: Dict[str, str] = {}  # Cache rendered audio paths
        
        if self.api_key and ELEVENLABS_AVAILABLE:
            # Initialize ElevenLabs client
            os.environ["ELEVENLABS_API_KEY"] = self.api_key
            logger.info("ElevenLabs initialized for voice synthesis")
        else:
            logger.warning("Voice synthesis not available. Using placeholder audio.")
            
    def add_voice_profile(self, profile: VoiceProfile):
        """Add a voice profile for a character.
        
        Args:
            profile: Voice profile to add
        """
        self.voice_profiles[profile.character_name] = profile
        logger.debug(f"Added voice profile for {profile.character_name}")
        
    def create_default_profiles(self, characters: List[Dict[str, Any]]):
        """Create default voice profiles for characters.
        
        Args:
            characters: List of character data
        """
        # Default voice IDs (would be actual ElevenLabs voice IDs in production)
        default_voices = [
            "21m00Tcm4TlvDq8ikWAM",  # Rachel
            "AZnzlk1XvdvUeBnXmlld",  # Domi
            "EXAVITQu4vr4xnSDxMaL",  # Bella
            "ErXwobaYiN019PkySvjV",  # Antoni
            "MF3mGyEYCl7XYWbV9V6O",  # Elli
        ]
        
        for i, char in enumerate(characters):
            name = char.get("name", f"Character_{i}")
            
            # Assign voice based on character traits
            voice_id = default_voices[i % len(default_voices)]
            
            # Determine voice characteristics based on personality
            personality = char.get("personality", {})
            stability = 0.3 + (personality.get("conscientiousness", 0.5) * 0.4)
            style = personality.get("openness", 0.5) * 0.3
            
            profile = VoiceProfile(
                character_name=name,
                voice_id=voice_id,
                stability=stability,
                style=style,
                age_group=self._determine_age_group(char.get("age"))
            )
            
            self.add_voice_profile(profile)
            
    def _determine_age_group(self, age: Optional[int]) -> str:
        """Determine age group from age."""
        if not age:
            return "adult"
        elif age < 13:
            return "child"
        elif age < 20:
            return "teen"
        elif age < 60:
            return "adult"
        else:
            return "elderly"
            
    async def render_dialogue(
        self,
        character: str,
        text: str,
        emotion: str = "neutral",
        output_path: Optional[str] = None
    ) -> Optional[str]:
        """Render a single dialogue line.
        
        Args:
            character: Character name
            text: Dialogue text
            emotion: Emotion for delivery
            output_path: Optional output path
            
        Returns:
            Path to rendered audio file or None
        """
        # Check cache
        cache_key = f"{character}_{hash(text)}_{emotion}"
        if cache_key in self.audio_cache:
            logger.debug(f"Using cached audio for {character}")
            return self.audio_cache[cache_key]
            
        if not ELEVENLABS_AVAILABLE or not self.api_key:
            logger.debug(f"Skipping audio render for: {character}: {text[:50]}...")
            return None
            
        profile = self.voice_profiles.get(character)
        if not profile:
            logger.warning(f"No voice profile for {character}")
            return None
            
        try:
            # Adjust text based on emotion
            processed_text = self._process_text_for_emotion(text, emotion)
            
            # Generate audio with ElevenLabs
            audio = generate(
                text=processed_text,
                voice=Voice(
                    voice_id=profile.voice_id,
                    settings=VoiceSettings(
                        stability=profile.stability,
                        similarity_boost=profile.similarity_boost,
                        style=profile.style,
                        use_speaker_boost=profile.use_speaker_boost
                    )
                )
            )
            
            # Save audio
            if not output_path:
                output_dir = Path("output/audio")
                output_dir.mkdir(parents=True, exist_ok=True)
                output_path = str(output_dir / f"{cache_key}.mp3")
                
            save(audio, output_path)
            
            # Cache the result
            self.audio_cache[cache_key] = output_path
            
            logger.debug(f"Rendered audio for {character} to {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to render audio for {character}: {e}")
            return None
            
    def _process_text_for_emotion(self, text: str, emotion: str) -> str:
        """Process text to convey emotion through punctuation and emphasis.
        
        Args:
            text: Original text
            emotion: Target emotion
            
        Returns:
            Processed text
        """
        if emotion == "happy":
            # Add exclamation for happiness
            if not text.endswith(("!", "?", ".")):
                text += "!"
        elif emotion == "sad":
            # Add ellipsis for sadness
            if not text.endswith("..."):
                text = text.rstrip(".!?") + "..."
        elif emotion == "angry":
            # Uppercase for anger
            text = text.upper()
        elif emotion == "fearful":
            # Add stammering for fear
            words = text.split()
            if len(words) > 3:
                words[0] = f"{words[0][0]}-{words[0]}"
            text = " ".join(words)
        elif emotion == "surprised":
            # Add exclamation for surprise
            text = text.rstrip(".") + "!"
            
        return text
        
    async def render_scene_audio(
        self,
        scene_data: Dict[str, Any],
        output_dir: str = "output/audio/scenes"
    ) -> Dict[str, Any]:
        """Render all audio for a scene.
        
        Args:
            scene_data: Scene data with dialogue
            output_dir: Output directory for audio files
            
        Returns:
            Audio manifest with file paths and timing
        """
        manifest = {
            "scene_id": scene_data.get("scene_id", "unknown"),
            "audio_files": [],
            "total_duration": 0.0,
            "dialogue_timing": []
        }
        
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Render each dialogue line
        current_time = 0.0
        for i, dialogue in enumerate(scene_data.get("dialogue", [])):
            character = dialogue.get("character")
            text = dialogue.get("line")
            emotion = dialogue.get("emotion", "neutral")
            
            # Render audio
            audio_path = await self.render_dialogue(
                character=character,
                text=text,
                emotion=emotion,
                output_path=f"{output_dir}/scene_{scene_data.get('scene_id')}_{i:03d}.mp3"
            )
            
            if audio_path:
                # Estimate duration (would get actual duration from audio file)
                duration = self._estimate_duration(text)
                
                manifest["audio_files"].append(audio_path)
                manifest["dialogue_timing"].append({
                    "character": character,
                    "text": text,
                    "audio_file": audio_path,
                    "start_time": current_time,
                    "duration": duration
                })
                
                current_time += duration + 0.5  # Add pause between lines
                
        manifest["total_duration"] = current_time
        return manifest
        
    def _estimate_duration(self, text: str) -> float:
        """Estimate audio duration from text length.
        
        Args:
            text: Dialogue text
            
        Returns:
            Estimated duration in seconds
        """
        # Rough estimate: 150 words per minute
        words = len(text.split())
        return (words / 150) * 60 + 0.5  # Add small buffer
        
    async def add_sound_effects(
        self,
        scene_audio: Dict[str, Any],
        scene_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Add sound effects to scene audio.
        
        Args:
            scene_audio: Audio manifest from render_scene_audio
            scene_data: Scene data with stage directions
            
        Returns:
            Updated audio manifest with sound effects
        """
        # This would integrate with a sound effects library
        # For now, just log what effects would be added
        
        effects = []
        
        # Analyze stage directions for sound cues
        for direction in scene_data.get("stage_directions", []):
            direction_lower = direction.lower()
            
            if "door" in direction_lower:
                effects.append({"type": "door", "timestamp": 0.0})
            elif "phone" in direction_lower or "ring" in direction_lower:
                effects.append({"type": "phone_ring", "timestamp": 0.0})
            elif "footsteps" in direction_lower:
                effects.append({"type": "footsteps", "timestamp": 0.0})
            elif "car" in direction_lower:
                effects.append({"type": "car_engine", "timestamp": 0.0})
                
        scene_audio["sound_effects"] = effects
        
        if effects:
            logger.debug(f"Added {len(effects)} sound effects to scene")
            
        return scene_audio
        
    def create_audio_timeline(
        self,
        episode_audio: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create a timeline for all episode audio.
        
        Args:
            episode_audio: List of scene audio manifests
            
        Returns:
            Complete audio timeline
        """
        timeline = {
            "scenes": [],
            "total_duration": 0.0,
            "tracks": {
                "dialogue": [],
                "effects": [],
                "music": []
            }
        }
        
        current_time = 0.0
        
        for scene_audio in episode_audio:
            scene_start = current_time
            
            # Add dialogue track entries
            for timing in scene_audio.get("dialogue_timing", []):
                timeline["tracks"]["dialogue"].append({
                    "file": timing["audio_file"],
                    "start": scene_start + timing["start_time"],
                    "duration": timing["duration"],
                    "character": timing["character"]
                })
                
            # Add sound effects
            for effect in scene_audio.get("sound_effects", []):
                timeline["tracks"]["effects"].append({
                    "type": effect["type"],
                    "start": scene_start + effect["timestamp"],
                    "duration": 2.0  # Default effect duration
                })
                
            timeline["scenes"].append({
                "scene_id": scene_audio["scene_id"],
                "start": scene_start,
                "duration": scene_audio["total_duration"]
            })
            
            current_time += scene_audio["total_duration"] + 1.0  # Scene transition
            
        timeline["total_duration"] = current_time
        
        logger.info(f"Created audio timeline: {current_time:.1f} seconds total")
        return timeline