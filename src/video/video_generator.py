"""Video generation pipeline using fal.ai models."""

import os
import json
import asyncio
import hashlib
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from pathlib import Path
from loguru import logger
import aiohttp
import base64
from io import BytesIO
from PIL import Image

# Import fal.ai client
try:
    import fal_client
    FAL_AVAILABLE = True
except ImportError:
    FAL_AVAILABLE = False
    logger.warning("fal_client not installed. Install with: pip install fal-client")


@dataclass
class VisualStyle:
    """Visual style configuration for consistent generation."""
    style_name: str
    style_prompt: str
    negative_prompt: str = ""
    aspect_ratio: str = "16:9"
    resolution: Tuple[int, int] = (1920, 1080)
    
    # Ideogram specific settings
    ideogram_model: str = "ideogram-v2"
    ideogram_style_preset: str = "photographic"
    magic_prompt_option: str = "auto"
    
    # Style reference images (optional)
    style_references: List[str] = field(default_factory=list)
    
    def get_full_prompt(self, base_prompt: str) -> str:
        """Combine base prompt with style prompt."""
        return f"{base_prompt}, {self.style_prompt}"


@dataclass
class CharacterVisual:
    """Visual representation of a character."""
    character_name: str
    visual_prompt: str
    image_path: Optional[str] = None
    image_url: Optional[str] = None
    generated_at: Optional[str] = None


@dataclass
class SceneVisual:
    """Visual representation of a scene."""
    scene_number: int
    environment_prompt: str
    background_image_path: Optional[str] = None
    characters_in_scene: List[str] = field(default_factory=list)
    composite_images: Dict[str, str] = field(default_factory=dict)  # character -> image_path


class VideoGenerator:
    """Main video generation pipeline using fal.ai models."""
    
    def __init__(self, fal_api_key: Optional[str] = None):
        """Initialize video generator.
        
        Args:
            fal_api_key: fal.ai API key
        """
        # Try multiple environment variable names (FAL_KEY is the official one)
        self.api_key = (
            fal_api_key or 
            os.getenv("FAL_KEY") or 
            os.getenv("FAL_API_KEY")
        )
        
        if not self.api_key:
            logger.error("fal.ai API key not found. Set FAL_KEY or FAL_API_KEY environment variable.")
            raise ValueError("fal.ai API key is required. Get one from https://fal.ai/dashboard")
        
        if not FAL_AVAILABLE:
            logger.error("fal_client not installed. Run: pip install fal-client")
            raise ImportError("fal_client is required")
        
        # Set the official environment variable for fal client
        os.environ["FAL_KEY"] = self.api_key
        
        # Storage
        self.visual_style: Optional[VisualStyle] = None
        self.character_visuals: Dict[str, CharacterVisual] = {}
        self.scene_visuals: Dict[int, SceneVisual] = {}
        self.generated_videos: List[str] = []
        
        # Cache directory
        self.cache_dir = Path("output/video_generation")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("Video generator initialized with fal.ai")
    
    def set_visual_style(self, style: VisualStyle):
        """Set the visual style for the entire episode.
        
        Args:
            style: Visual style configuration
        """
        self.visual_style = style
        logger.info(f"Visual style set: {style.style_name}")
    
    async def generate_character_image(
        self, 
        character_name: str, 
        character_prompt: str,
        save_path: Optional[str] = None
    ) -> str:
        """Generate character image using Ideogram.
        
        Args:
            character_name: Character name
            character_prompt: Visual description prompt
            save_path: Optional save path
            
        Returns:
            Path to generated image
        """
        if not self.visual_style:
            raise ValueError("Visual style must be set before generating images")
        
        # Combine with style
        full_prompt = self.visual_style.get_full_prompt(character_prompt)
        full_prompt = f"portrait of {character_name}, {full_prompt}"
        
        logger.info(f"Generating character image for {character_name}")
        logger.debug(f"Prompt: {full_prompt}")
        
        try:
            # Generate with Ideogram via fal.ai
            result = await self._call_ideogram(
                prompt=full_prompt,
                negative_prompt=self.visual_style.negative_prompt,
                aspect_ratio="1:1",  # Square for portraits
                model=self.visual_style.ideogram_model
            )
            
            # Save image
            if not save_path:
                save_path = str(self.cache_dir / "characters" / f"{character_name.replace(' ', '_')}.png")
            
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Download and save image
            image_url = result.get("images", [{}])[0].get("url")
            if image_url:
                await self._download_image(image_url, save_path)
                
                # Store character visual
                self.character_visuals[character_name] = CharacterVisual(
                    character_name=character_name,
                    visual_prompt=full_prompt,
                    image_path=save_path,
                    image_url=image_url
                )
                
                logger.info(f"Character image saved: {save_path}")
                return save_path
            else:
                raise ValueError("No image URL in response")
                
        except Exception as e:
            logger.error(f"Failed to generate character image: {e}")
            raise
    
    async def generate_scene_background(
        self,
        scene_number: int,
        environment_prompt: str,
        save_path: Optional[str] = None
    ) -> str:
        """Generate scene background using Ideogram.
        
        Args:
            scene_number: Scene number
            environment_prompt: Environment description
            save_path: Optional save path
            
        Returns:
            Path to generated background
        """
        if not self.visual_style:
            raise ValueError("Visual style must be set before generating images")
        
        # Combine with style
        full_prompt = self.visual_style.get_full_prompt(environment_prompt)
        full_prompt = f"wide shot, environment, no people, {full_prompt}"
        
        logger.info(f"Generating background for scene {scene_number}")
        logger.debug(f"Prompt: {full_prompt}")
        
        try:
            # Generate with Ideogram
            result = await self._call_ideogram(
                prompt=full_prompt,
                negative_prompt=f"people, characters, humans, {self.visual_style.negative_prompt}",
                aspect_ratio=self.visual_style.aspect_ratio,
                model=self.visual_style.ideogram_model
            )
            
            # Save image
            if not save_path:
                save_path = str(self.cache_dir / "scenes" / f"scene_{scene_number:03d}_bg.png")
            
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Download and save
            image_url = result.get("images", [{}])[0].get("url")
            if image_url:
                await self._download_image(image_url, save_path)
                
                # Store scene visual
                if scene_number not in self.scene_visuals:
                    self.scene_visuals[scene_number] = SceneVisual(
                        scene_number=scene_number,
                        environment_prompt=full_prompt
                    )
                self.scene_visuals[scene_number].background_image_path = save_path
                
                logger.info(f"Scene background saved: {save_path}")
                return save_path
            else:
                raise ValueError("No image URL in response")
                
        except Exception as e:
            logger.error(f"Failed to generate scene background: {e}")
            raise
    
    async def composite_character_in_scene(
        self,
        scene_number: int,
        character_name: str,
        save_path: Optional[str] = None
    ) -> str:
        """Composite character into scene using Flux Kontekt Pro.
        
        Args:
            scene_number: Scene number
            character_name: Character to composite
            save_path: Optional save path
            
        Returns:
            Path to composite image
        """
        # Get character and scene images
        if character_name not in self.character_visuals:
            raise ValueError(f"Character {character_name} not generated yet")
        
        if scene_number not in self.scene_visuals:
            raise ValueError(f"Scene {scene_number} not generated yet")
        
        character_visual = self.character_visuals[character_name]
        scene_visual = self.scene_visuals[scene_number]
        
        if not character_visual.image_path or not scene_visual.background_image_path:
            raise ValueError("Images not available for compositing")
        
        logger.info(f"Compositing {character_name} into scene {scene_number}")
        
        try:
            # Call Flux Kontekt Pro for compositing
            result = await self._call_flux_kontekt(
                character_image=character_visual.image_path,
                background_image=scene_visual.background_image_path,
                prompt=f"{character_name} in the scene, natural lighting, photorealistic"
            )
            
            # Save composite
            if not save_path:
                save_path = str(self.cache_dir / "composites" / 
                              f"scene_{scene_number:03d}_{character_name.replace(' ', '_')}.png")
            
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Download and save
            image_url = result.get("image", {}).get("url")
            if image_url:
                await self._download_image(image_url, save_path)
                
                # Store in scene visual
                self.scene_visuals[scene_number].composite_images[character_name] = save_path
                
                logger.info(f"Composite saved: {save_path}")
                return save_path
            else:
                raise ValueError("No image URL in response")
                
        except Exception as e:
            logger.error(f"Failed to composite character: {e}")
            raise
    
    async def generate_talking_video(
        self,
        character_name: str,
        scene_number: int,
        audio_path: str,
        dialogue_text: str,
        emotion: str = "neutral",
        save_path: Optional[str] = None
    ) -> str:
        """Generate talking video using Stable Avatar.
        
        Args:
            character_name: Character name
            scene_number: Scene number
            audio_path: Path to audio file
            dialogue_text: Dialogue text
            emotion: Emotion for expression
            save_path: Optional save path
            
        Returns:
            Path to generated video
        """
        # Get composite image
        if scene_number not in self.scene_visuals:
            raise ValueError(f"Scene {scene_number} not prepared")
        
        composite_path = self.scene_visuals[scene_number].composite_images.get(character_name)
        if not composite_path:
            # Fallback to character image if no composite
            if character_name in self.character_visuals:
                composite_path = self.character_visuals[character_name].image_path
            else:
                raise ValueError(f"No image available for {character_name}")
        
        logger.info(f"Generating talking video for {character_name} in scene {scene_number}")
        
        try:
            # Call Stable Avatar
            result = await self._call_stable_avatar(
                image_path=composite_path,
                audio_path=audio_path,
                emotion=emotion
            )
            
            # Save video
            if not save_path:
                save_path = str(self.cache_dir / "videos" / 
                              f"scene_{scene_number:03d}_{character_name.replace(' ', '_')}.mp4")
            
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Download and save video
            video_url = result.get("video", {}).get("url")
            if video_url:
                await self._download_video(video_url, save_path)
                
                self.generated_videos.append(save_path)
                logger.info(f"Video saved: {save_path}")
                return save_path
            else:
                raise ValueError("No video URL in response")
                
        except Exception as e:
            logger.error(f"Failed to generate talking video: {e}")
            raise
    
    async def _call_ideogram(
        self, 
        prompt: str, 
        negative_prompt: str = "",
        aspect_ratio: str = "16:9",
        model: str = "ideogram-v2"
    ) -> Dict[str, Any]:
        """Call Ideogram API via fal.ai."""
        try:
            import fal_client
            
            result = await fal_client.run_async(
                "fal-ai/ideogram",
                arguments={
                    "prompt": prompt,
                    "negative_prompt": negative_prompt,
                    "aspect_ratio": aspect_ratio,
                    "model": model,
                    "magic_prompt_option": "auto",
                    "num_images": 1
                }
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Ideogram API call failed: {e}")
            raise
    
    async def _call_flux_kontekt(
        self,
        character_image: str,
        background_image: str,
        prompt: str
    ) -> Dict[str, Any]:
        """Call Flux Kontekt Pro for compositing."""
        try:
            import fal_client
            
            # Upload images to fal.ai
            with open(character_image, 'rb') as f:
                character_url = fal_client.upload(f.read(), "image/png")
            
            with open(background_image, 'rb') as f:
                background_url = fal_client.upload(f.read(), "image/png")
            
            result = await fal_client.run_async(
                "fal-ai/flux-kontekst-pro",
                arguments={
                    "foreground_image_url": character_url,
                    "background_image_url": background_url,
                    "prompt": prompt,
                    "guidance_scale": 7.5,
                    "num_inference_steps": 50
                }
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Flux Kontekt API call failed: {e}")
            raise
    
    async def _call_stable_avatar(
        self,
        image_path: str,
        audio_path: str,
        emotion: str = "neutral"
    ) -> Dict[str, Any]:
        """Call Stable Avatar for video generation."""
        try:
            import fal_client
            
            # Upload files to fal.ai
            with open(image_path, 'rb') as f:
                image_url = fal_client.upload(f.read(), "image/png")
            
            with open(audio_path, 'rb') as f:
                audio_url = fal_client.upload(f.read(), "audio/mpeg")
            
            # Map emotion to expression
            expression_map = {
                "neutral": "neutral",
                "happy": "smile",
                "sad": "sad",
                "angry": "angry",
                "surprised": "surprise",
                "fearful": "fear"
            }
            expression = expression_map.get(emotion, "neutral")
            
            result = await fal_client.run_async(
                "fal-ai/stable-avatar",
                arguments={
                    "image_url": image_url,
                    "audio_url": audio_url,
                    "expression": expression,
                    "blink": True,
                    "eye_gaze": "camera",
                    "head_motion": "natural"
                }
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Stable Avatar API call failed: {e}")
            raise
    
    async def _download_image(self, url: str, save_path: str):
        """Download image from URL."""
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    content = await response.read()
                    with open(save_path, 'wb') as f:
                        f.write(content)
                else:
                    raise ValueError(f"Failed to download image: {response.status}")
    
    async def _download_video(self, url: str, save_path: str):
        """Download video from URL."""
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    content = await response.read()
                    with open(save_path, 'wb') as f:
                        f.write(content)
                else:
                    raise ValueError(f"Failed to download video: {response.status}")


# Preset visual styles
PRESET_STYLES = {
    "cinematic": VisualStyle(
        style_name="Cinematic",
        style_prompt="cinematic lighting, film grain, professional cinematography, depth of field, color graded",
        negative_prompt="cartoon, anime, illustration, painting, low quality",
        ideogram_style_preset="cinematic"
    ),
    "realistic": VisualStyle(
        style_name="Photorealistic",
        style_prompt="photorealistic, high detail, natural lighting, professional photography, 8k resolution",
        negative_prompt="cartoon, anime, illustration, painting, artificial",
        ideogram_style_preset="photographic"
    ),
    "dramatic": VisualStyle(
        style_name="Dramatic",
        style_prompt="dramatic lighting, high contrast, moody atmosphere, cinematic composition",
        negative_prompt="bright, cheerful, cartoon, flat lighting",
        ideogram_style_preset="cinematic"
    ),
    "tech_noir": VisualStyle(
        style_name="Tech Noir",
        style_prompt="tech noir style, neon lighting, cyberpunk aesthetic, dark atmosphere, futuristic",
        negative_prompt="bright, cheerful, medieval, historical",
        ideogram_style_preset="futuristic"
    )
}