"""Complete episode video generation pipeline."""

import os
import json
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime
from loguru import logger
import subprocess
from dataclasses import dataclass, field

from .script_extractor import ScriptExtractor, SceneData, CharacterProfile
from .video_generator import VideoGenerator, VisualStyle, PRESET_STYLES
from ..rendering.episode_audio_renderer import EpisodeAudioRenderer


@dataclass
class VideoSegment:
    """Single video segment for a dialogue."""
    scene_number: int
    dialogue_index: int
    character: str
    video_path: str
    audio_path: str
    duration: float
    dialogue_text: str
    emotion: str


@dataclass
class SceneVideo:
    """Complete scene video data."""
    scene_number: int
    segments: List[VideoSegment]
    combined_video_path: Optional[str] = None
    total_duration: float = 0.0


class EpisodeVideoPipeline:
    """Complete pipeline for generating episode videos."""
    
    def __init__(
        self,
        fal_api_key: Optional[str] = None,
        elevenlabs_api_key: Optional[str] = None
    ):
        """Initialize episode video pipeline.
        
        Args:
            fal_api_key: fal.ai API key (optional, will use FAL_KEY or FAL_API_KEY env var)
            elevenlabs_api_key: ElevenLabs API key for audio
        """
        # Initialize components
        self.script_extractor = ScriptExtractor()
        self.video_generator = VideoGenerator(fal_api_key)
        self.audio_renderer = EpisodeAudioRenderer(elevenlabs_api_key)
        
        # Storage
        self.extracted_data: Optional[Dict[str, Any]] = None
        self.scene_videos: Dict[int, SceneVideo] = {}
        self.output_dir = Path("output/episode_videos")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Pipeline state
        self.current_episode_id: Optional[str] = None
        self.visual_style: Optional[VisualStyle] = None
        
        logger.info("Episode video pipeline initialized")
    
    async def generate_episode_video(
        self,
        episode_json_path: str,
        visual_style: str = "cinematic",
        character_voice_mapping: Optional[Dict[str, str]] = None,
        output_path: Optional[str] = None
    ) -> str:
        """Generate complete episode video from JSON.
        
        Args:
            episode_json_path: Path to episode JSON file
            visual_style: Visual style preset or custom style
            character_voice_mapping: Optional character to celebrity voice mapping
            output_path: Optional output path for final video
            
        Returns:
            Path to final video file
        """
        logger.info(f"Starting episode video generation from {episode_json_path}")
        
        # Generate episode ID
        self.current_episode_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        episode_dir = self.output_dir / self.current_episode_id
        episode_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Step 1: Extract script data
            logger.info("Step 1: Extracting script data...")
            self.extracted_data = self.script_extractor.extract_from_json(episode_json_path)
            extraction_path = episode_dir / "extraction.json"
            self.script_extractor.save_extraction(str(extraction_path))
            
            # Step 2: Set visual style
            logger.info("Step 2: Setting visual style...")
            if visual_style in PRESET_STYLES:
                self.visual_style = PRESET_STYLES[visual_style]
            else:
                # Default to cinematic
                self.visual_style = PRESET_STYLES["cinematic"]
            self.video_generator.set_visual_style(self.visual_style)
            
            # Step 3: Generate character images
            logger.info("Step 3: Generating character images...")
            await self._generate_all_character_images()
            
            # Step 4: Generate scene backgrounds
            logger.info("Step 4: Generating scene backgrounds...")
            await self._generate_all_scene_backgrounds()
            
            # Step 5: Generate audio for all dialogues
            logger.info("Step 5: Generating dialogue audio...")
            audio_manifest = await self._generate_all_audio(character_voice_mapping)
            
            # Step 6: Create composite images for each scene
            logger.info("Step 6: Creating scene composites...")
            await self._create_all_composites()
            
            # Step 7: Generate talking videos for each dialogue
            logger.info("Step 7: Generating talking videos...")
            await self._generate_all_talking_videos(audio_manifest)
            
            # Step 8: Assemble final video
            logger.info("Step 8: Assembling final video...")
            if not output_path:
                output_path = str(episode_dir / "final_episode.mp4")
            
            final_video = await self._assemble_final_video(output_path)
            
            logger.info(f"Episode video generation complete: {final_video}")
            return final_video
            
        except Exception as e:
            logger.error(f"Episode video generation failed: {e}")
            raise
    
    async def _generate_all_character_images(self):
        """Generate images for all characters."""
        characters = self.extracted_data.get("characters", {})
        
        tasks = []
        for char_name, char_data in characters.items():
            if not self._is_special_character(char_name):
                visual_prompt = char_data.get("visual_prompt", f"portrait of {char_name}")
                task = self.video_generator.generate_character_image(
                    character_name=char_name,
                    character_prompt=visual_prompt
                )
                tasks.append(task)
        
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Failed to generate character image: {result}")
    
    async def _generate_all_scene_backgrounds(self):
        """Generate backgrounds for all scenes."""
        scenes = self.extracted_data.get("scenes", [])
        
        tasks = []
        for scene_data in scenes:
            scene_number = scene_data["scene_number"]
            env_description = scene_data.get("environment_description", "modern indoor setting")
            
            task = self.video_generator.generate_scene_background(
                scene_number=scene_number,
                environment_prompt=env_description
            )
            tasks.append(task)
        
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Failed to generate scene background: {result}")
    
    async def _generate_all_audio(
        self,
        character_voice_mapping: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Generate audio for all dialogues."""
        # Prepare episode data for audio renderer
        episode_data = {
            "episode_id": self.current_episode_id,
            "title": self.extracted_data["metadata"]["title"],
            "characters": list(self.extracted_data["characters"].values()),
            "scenes": []
        }
        
        # Convert extracted scenes to audio renderer format
        for scene_data in self.extracted_data["scenes"]:
            scene = {
                "scene_id": f"scene_{scene_data['scene_number']:03d}",
                "scene_number": scene_data["scene_number"],
                "act_number": scene_data["act_number"],
                "location": scene_data["location"],
                "dialogue": []
            }
            
            for dialogue in scene_data["dialogue_sequence"]:
                scene["dialogue"].append({
                    "character": dialogue["character"],
                    "line": dialogue["line"],
                    "emotion": dialogue["emotion"],
                    "action": dialogue["action"]
                })
            
            episode_data["scenes"].append(scene)
        
        # Generate audio
        audio_dir = self.output_dir / self.current_episode_id / "audio"
        audio_manifest = await self.audio_renderer.render_full_episode(
            episode_data=episode_data,
            output_dir=str(audio_dir),
            character_mapping=character_voice_mapping
        )
        
        return audio_manifest
    
    async def _create_all_composites(self):
        """Create composite images for all scene-character combinations."""
        scenes = self.extracted_data.get("scenes", [])
        
        for scene_data in scenes:
            scene_number = scene_data["scene_number"]
            characters = scene_data["characters"]
            
            # Composite each character into the scene
            for character in characters:
                if not self._is_special_character(character):
                    try:
                        await self.video_generator.composite_character_in_scene(
                            scene_number=scene_number,
                            character_name=character
                        )
                    except Exception as e:
                        logger.error(f"Failed to composite {character} in scene {scene_number}: {e}")
    
    async def _generate_all_talking_videos(self, audio_manifest: Dict[str, Any]):
        """Generate talking videos for all dialogues."""
        scenes = self.extracted_data.get("scenes", [])
        
        for scene_data in scenes:
            scene_number = scene_data["scene_number"]
            scene_video = SceneVideo(scene_number=scene_number, segments=[])
            
            # Get audio data for this scene
            scene_audio_dir = Path(f"output/audio/episodes/{self.current_episode_id}/scene_{scene_number:03d}")
            
            for i, dialogue in enumerate(scene_data["dialogue_sequence"]):
                character = dialogue["character"]
                
                if self._is_special_character(character):
                    continue
                
                # Find audio file for this dialogue
                audio_path = None
                audio_files = list(scene_audio_dir.glob(f"*_{i:03d}_{character}*.mp3"))
                if audio_files:
                    audio_path = str(audio_files[0])
                else:
                    logger.warning(f"No audio found for {character} dialogue {i} in scene {scene_number}")
                    continue
                
                # Generate talking video
                try:
                    video_path = await self.video_generator.generate_talking_video(
                        character_name=character,
                        scene_number=scene_number,
                        audio_path=audio_path,
                        dialogue_text=dialogue["line"],
                        emotion=dialogue["emotion"]
                    )
                    
                    # Create video segment
                    segment = VideoSegment(
                        scene_number=scene_number,
                        dialogue_index=i,
                        character=character,
                        video_path=video_path,
                        audio_path=audio_path,
                        duration=dialogue["duration"],
                        dialogue_text=dialogue["line"],
                        emotion=dialogue["emotion"]
                    )
                    
                    scene_video.segments.append(segment)
                    scene_video.total_duration += dialogue["duration"]
                    
                except Exception as e:
                    logger.error(f"Failed to generate video for {character} in scene {scene_number}: {e}")
            
            self.scene_videos[scene_number] = scene_video
    
    async def _assemble_final_video(self, output_path: str) -> str:
        """Assemble all video segments into final episode video."""
        logger.info("Assembling final video...")
        
        # Create list of all video segments in order
        all_segments = []
        for scene_number in sorted(self.scene_videos.keys()):
            scene_video = self.scene_videos[scene_number]
            all_segments.extend(scene_video.segments)
        
        if not all_segments:
            raise ValueError("No video segments to assemble")
        
        # Create concat file for ffmpeg
        concat_file = self.output_dir / self.current_episode_id / "concat.txt"
        with open(concat_file, 'w') as f:
            for segment in all_segments:
                f.write(f"file '{segment.video_path}'\n")
        
        # Use ffmpeg to concatenate videos
        try:
            cmd = [
                'ffmpeg',
                '-f', 'concat',
                '-safe', '0',
                '-i', str(concat_file),
                '-c', 'copy',
                '-y',
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"ffmpeg error: {result.stderr}")
                raise RuntimeError(f"ffmpeg failed: {result.stderr}")
            
            logger.info(f"Final video assembled: {output_path}")
            
            # Generate subtitle file
            subtitle_path = self._generate_subtitles(all_segments, output_path)
            logger.info(f"Subtitles generated: {subtitle_path}")
            
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to assemble video: {e}")
            raise
    
    def _generate_subtitles(self, segments: List[VideoSegment], video_path: str) -> str:
        """Generate subtitle file for the video."""
        subtitle_path = video_path.replace('.mp4', '.srt')
        
        with open(subtitle_path, 'w', encoding='utf-8') as f:
            current_time = 0.0
            
            for i, segment in enumerate(segments, 1):
                start_time = current_time
                end_time = current_time + segment.duration
                
                # Format timestamps
                start_str = self._format_timestamp(start_time)
                end_str = self._format_timestamp(end_time)
                
                # Write subtitle entry
                f.write(f"{i}\n")
                f.write(f"{start_str} --> {end_str}\n")
                f.write(f"{segment.character}: {segment.dialogue_text}\n")
                f.write("\n")
                
                current_time = end_time
        
        return subtitle_path
    
    def _format_timestamp(self, seconds: float) -> str:
        """Format seconds to SRT timestamp format."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{secs:06.3f}".replace('.', ',')
    
    def _is_special_character(self, name: str) -> bool:
        """Check if character is special/system character."""
        special = ["AI System", "System", "Narrator", "off-screen", "Family", "Investors"]
        return any(s in name for s in special)


async def generate_episode_video_from_json(
    json_path: str,
    visual_style: str = "cinematic",
    character_voices: Optional[Dict[str, str]] = None,
    output_path: Optional[str] = None
) -> str:
    """Convenience function to generate episode video.
    
    Args:
        json_path: Path to episode JSON
        visual_style: Visual style preset
        character_voices: Character to celebrity voice mapping
        output_path: Optional output path
        
    Returns:
        Path to generated video
    """
    pipeline = EpisodeVideoPipeline()
    return await pipeline.generate_episode_video(
        episode_json_path=json_path,
        visual_style=visual_style,
        character_voice_mapping=character_voices,
        output_path=output_path
    )