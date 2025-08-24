"""Episode audio rendering with celebrity voices integration."""

import os
import json
import asyncio
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from loguru import logger

from .audio_renderer import AudioRenderer, VoiceProfile
from .celebrity_voices import CelebrityVoiceGenerator
from ..models.episode_models import EpisodeModel, SceneModel


class EpisodeAudioRenderer:
    """Integrated audio renderer for full episode generation with celebrity voices."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize episode audio renderer.
        
        Args:
            api_key: ElevenLabs API key
        """
        self.api_key = api_key or os.getenv("ELEVENLABS_API_KEY")
        
        # Initialize renderers
        self.base_renderer = AudioRenderer(api_key=self.api_key)
        self.celebrity_generator = None
        
        # Try to initialize celebrity generator if API key is available
        if self.api_key:
            try:
                self.celebrity_generator = CelebrityVoiceGenerator(api_key=self.api_key)
                logger.info("Celebrity voice generator initialized")
            except Exception as e:
                logger.warning(f"Celebrity voice generator not available: {e}")
                self.celebrity_generator = None
        
        # Character voice mapping (character name -> celebrity or voice profile)
        self.character_voice_mapping: Dict[str, Union[str, VoiceProfile]] = {}
        
        # Audio generation cache
        self.audio_cache: Dict[str, str] = {}
    
    def map_character_to_celebrity(self, character_name: str, celebrity_name: str):
        """Map a character to a celebrity voice.
        
        Args:
            character_name: Character name in the episode
            celebrity_name: Celebrity voice to use (e.g., 'elon_musk', 'trump')
        """
        if self.celebrity_generator:
            available = self.celebrity_generator.list_available_celebrities()
            if celebrity_name in available:
                self.character_voice_mapping[character_name] = celebrity_name
                logger.info(f"Mapped {character_name} to {celebrity_name} voice")
            else:
                logger.warning(f"Celebrity {celebrity_name} not available")
        else:
            logger.warning("Celebrity generator not initialized")
    
    def map_character_to_voice_profile(self, character_name: str, voice_profile: VoiceProfile):
        """Map a character to a custom voice profile.
        
        Args:
            character_name: Character name in the episode
            voice_profile: Custom voice profile
        """
        self.character_voice_mapping[character_name] = voice_profile
        self.base_renderer.add_voice_profile(voice_profile)
        logger.info(f"Mapped {character_name} to custom voice profile")
    
    def auto_map_characters(self, characters: List[Dict[str, Any]]):
        """Automatically map characters to appropriate voices.
        
        Args:
            characters: List of character data from episode
        """
        # Predefined celebrity mappings for common archetypes
        celebrity_archetypes = {
            "tech_leader": "elon_musk",
            "politician": "trump",
            "businessman": "trump",
            "scientist": "elon_musk",
            "president": "joe_biden",
            "leader": "obama"
        }
        
        # Analyze characters and assign voices
        for char in characters:
            name = char.get("name", "Unknown")
            occupation = char.get("occupation", "").lower()
            personality = char.get("personality", {})
            
            # Check if character matches a celebrity archetype
            celebrity_assigned = False
            for archetype, celebrity in celebrity_archetypes.items():
                if archetype in occupation:
                    self.map_character_to_celebrity(name, celebrity)
                    celebrity_assigned = True
                    break
            
            # If no celebrity match, create custom voice profile
            if not celebrity_assigned:
                # Use personality traits to determine voice characteristics
                voice_profile = self._create_voice_profile_from_personality(name, personality)
                self.map_character_to_voice_profile(name, voice_profile)
    
    def _create_voice_profile_from_personality(
        self, 
        character_name: str, 
        personality: Dict[str, float]
    ) -> VoiceProfile:
        """Create voice profile based on personality traits.
        
        Args:
            character_name: Character name
            personality: Personality traits dictionary
            
        Returns:
            Generated voice profile
        """
        # Default ElevenLabs voice IDs
        voice_options = [
            "21m00Tcm4TlvDq8ikWAM",  # Rachel
            "AZnzlk1XvdvUeBnXmlld",  # Domi  
            "EXAVITQu4vr4xnSDxMaL",  # Bella
            "ErXwobaYiN019PkySvjV",  # Antoni
            "MF3mGyEYCl7XYWbV9V6O",  # Elli
        ]
        
        # Select voice based on personality
        voice_index = int(personality.get("extraversion", 0.5) * len(voice_options))
        voice_id = voice_options[min(voice_index, len(voice_options) - 1)]
        
        # Determine voice characteristics
        stability = 0.3 + (personality.get("conscientiousness", 0.5) * 0.4)
        style = personality.get("openness", 0.5) * 0.3
        
        return VoiceProfile(
            character_name=character_name,
            voice_id=voice_id,
            stability=stability,
            similarity_boost=0.7,
            style=style,
            use_speaker_boost=True
        )
    
    async def render_scene_with_celebrities(
        self,
        scene_data: Dict[str, Any],
        output_dir: str = "output/audio/scenes"
    ) -> Dict[str, Any]:
        """Render scene audio using celebrity voices where mapped.
        
        Args:
            scene_data: Scene data with dialogue
            output_dir: Output directory
            
        Returns:
            Audio manifest with file paths and timing
        """
        manifest = {
            "scene_id": scene_data.get("scene_id", "unknown"),
            "audio_files": [],
            "total_duration": 0.0,
            "dialogue_timing": [],
            "voice_types": {}  # Track which voice type was used
        }
        
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        current_time = 0.0
        
        # Process each dialogue line
        for i, dialogue in enumerate(scene_data.get("dialogue", [])):
            character = dialogue.get("character")
            text = dialogue.get("line")
            emotion = dialogue.get("emotion", "neutral")
            
            # Determine output path
            scene_id = scene_data.get("scene_id", "unknown")
            output_path = f"{output_dir}/scene_{scene_id}_{i:03d}_{character}.mp3"
            
            # Check if character has celebrity voice mapping
            if character in self.character_voice_mapping:
                voice_mapping = self.character_voice_mapping[character]
                
                if isinstance(voice_mapping, str) and self.celebrity_generator:
                    # Use celebrity voice
                    try:
                        # Map emotions to celebrity styles
                        style_map = {
                            "happy": "excited",
                            "sad": "calm",
                            "angry": "confident",
                            "neutral": "default"
                        }
                        style = style_map.get(emotion, "default")
                        
                        audio_path = self.celebrity_generator.generate(
                            celebrity=voice_mapping,
                            text=text,
                            style=style,
                            output_path=output_path
                        )
                        manifest["voice_types"][character] = f"celebrity:{voice_mapping}"
                        
                    except Exception as e:
                        logger.error(f"Failed to generate celebrity voice for {character}: {e}")
                        # Fallback to base renderer
                        audio_path = await self.base_renderer.render_dialogue(
                            character=character,
                            text=text,
                            emotion=emotion,
                            output_path=output_path
                        )
                        manifest["voice_types"][character] = "default"
                        
                elif isinstance(voice_mapping, VoiceProfile):
                    # Use custom voice profile
                    audio_path = await self.base_renderer.render_dialogue(
                        character=character,
                        text=text,
                        emotion=emotion,
                        output_path=output_path
                    )
                    manifest["voice_types"][character] = "custom_profile"
                else:
                    audio_path = None
            else:
                # No mapping, use default
                audio_path = await self.base_renderer.render_dialogue(
                    character=character,
                    text=text,
                    emotion=emotion,
                    output_path=output_path
                )
                manifest["voice_types"][character] = "default"
            
            if audio_path:
                # Estimate duration
                duration = self._estimate_duration(text)
                
                manifest["audio_files"].append(audio_path)
                manifest["dialogue_timing"].append({
                    "character": character,
                    "text": text,
                    "emotion": emotion,
                    "audio_file": audio_path,
                    "start_time": current_time,
                    "duration": duration
                })
                
                current_time += duration + 0.5  # Pause between lines
        
        manifest["total_duration"] = current_time
        
        # Add sound effects
        manifest = await self.base_renderer.add_sound_effects(manifest, scene_data)
        
        logger.info(f"Rendered scene {scene_data.get('scene_id')} with {len(manifest['audio_files'])} audio files")
        return manifest
    
    async def render_full_episode(
        self,
        episode_data: Dict[str, Any],
        output_dir: str = "output/audio/episodes",
        character_mapping: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Render audio for entire episode.
        
        Args:
            episode_data: Complete episode data
            output_dir: Output directory
            character_mapping: Optional explicit character to celebrity mapping
            
        Returns:
            Complete episode audio manifest
        """
        episode_id = episode_data.get("episode_id", "unknown")
        episode_dir = Path(output_dir) / episode_id
        episode_dir.mkdir(parents=True, exist_ok=True)
        
        # Set up character mappings
        if character_mapping:
            for char, celebrity in character_mapping.items():
                self.map_character_to_celebrity(char, celebrity)
        else:
            # Auto-map based on character data
            characters = episode_data.get("characters", [])
            if characters:
                self.auto_map_characters(characters)
        
        # Episode manifest
        manifest = {
            "episode_id": episode_id,
            "title": episode_data.get("title", "Untitled"),
            "scenes": [],
            "total_duration": 0.0,
            "character_voices": self._get_character_voice_summary(),
            "audio_timeline": None
        }
        
        # Render each scene
        scene_manifests = []
        for scene in episode_data.get("scenes", []):
            scene_id = scene.get("scene_id", f"scene_{len(scene_manifests)}")
            scene_dir = episode_dir / scene_id
            
            logger.info(f"Rendering scene {scene_id}")
            scene_manifest = await self.render_scene_with_celebrities(
                scene_data=scene,
                output_dir=str(scene_dir)
            )
            
            scene_manifests.append(scene_manifest)
            manifest["scenes"].append({
                "scene_id": scene_id,
                "duration": scene_manifest["total_duration"],
                "audio_files": len(scene_manifest["audio_files"])
            })
        
        # Create episode timeline
        timeline = self.base_renderer.create_audio_timeline(scene_manifests)
        manifest["audio_timeline"] = timeline
        manifest["total_duration"] = timeline["total_duration"]
        
        # Save manifest
        manifest_path = episode_dir / "audio_manifest.json"
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        logger.info(f"Episode audio rendering complete: {manifest['total_duration']:.1f}s total")
        logger.info(f"Manifest saved to: {manifest_path}")
        
        return manifest
    
    def _estimate_duration(self, text: str) -> float:
        """Estimate audio duration from text."""
        words = len(text.split())
        return (words / 150) * 60 + 0.5
    
    def _get_character_voice_summary(self) -> Dict[str, str]:
        """Get summary of character voice mappings."""
        summary = {}
        for char, mapping in self.character_voice_mapping.items():
            if isinstance(mapping, str):
                summary[char] = f"celebrity:{mapping}"
            elif isinstance(mapping, VoiceProfile):
                summary[char] = f"custom:{mapping.voice_id[:8]}"
            else:
                summary[char] = "unknown"
        return summary
    
    async def render_episode_from_model(
        self,
        episode: EpisodeModel,
        output_dir: str = "output/audio/episodes",
        character_mapping: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Render audio from EpisodeModel object.
        
        Args:
            episode: EpisodeModel instance
            output_dir: Output directory
            character_mapping: Optional character to celebrity mapping
            
        Returns:
            Episode audio manifest
        """
        # Convert model to dict for processing
        episode_data = {
            "episode_id": episode.episode_id or "generated",
            "title": episode.title,
            "characters": [char.dict() for char in episode.characters],
            "scenes": []
        }
        
        # Extract scenes from acts
        for act in episode.acts:
            for scene in act.scenes:
                scene_dict = scene.dict()
                episode_data["scenes"].append(scene_dict)
        
        return await self.render_full_episode(
            episode_data=episode_data,
            output_dir=output_dir,
            character_mapping=character_mapping
        )


# Convenience function for quick integration
async def render_episode_with_celebrities(
    episode_data: Dict[str, Any],
    character_mapping: Dict[str, str],
    output_dir: str = "output/audio/episodes"
) -> Dict[str, Any]:
    """Quick function to render episode with celebrity voices.
    
    Args:
        episode_data: Episode data
        character_mapping: Character to celebrity mapping
        output_dir: Output directory
        
    Returns:
        Audio manifest
    """
    renderer = EpisodeAudioRenderer()
    return await renderer.render_full_episode(
        episode_data=episode_data,
        output_dir=output_dir,
        character_mapping=character_mapping
    )