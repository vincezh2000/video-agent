"""Updated video generation pipeline using fal.ai models with correct API."""

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
    
    # Ideogram V3 specific settings
    ideogram_model: str = "ideogram/v3"
    rendering_speed: str = "BALANCED"  # TURBO, BALANCED, QUALITY
    style_type: str = "REALISTIC"  # AUTO, GENERAL, REALISTIC, DESIGN
    expand_prompt: bool = True
    
    # Style reference images (optional)
    style_references: List[str] = field(default_factory=list)
    
    def get_full_prompt(self, base_prompt: str) -> str:
        """Combine base prompt with style prompt."""
        return f"{base_prompt}, {self.style_prompt}"
    
    def get_ideogram_size(self) -> str:
        """Convert aspect ratio to Ideogram image size."""
        size_map = {
            "16:9": "landscape_16_9",
            "9:16": "portrait_16_9",
            "4:3": "landscape_4_3",
            "3:4": "portrait_4_3",
            "1:1": "square_hd"
        }
        return size_map.get(self.aspect_ratio, "square_hd")


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
    background_image_url: Optional[str] = None
    characters_in_scene: List[str] = field(default_factory=list)
    composite_images: Dict[str, str] = field(default_factory=dict)  # character -> image_path
    composite_urls: Dict[str, str] = field(default_factory=dict)  # character -> image_url


class VideoGeneratorV2:
    """Updated video generation pipeline using fal.ai models with correct API."""
    
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
        
        logger.info("Video generator V2 initialized with fal.ai")
    
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
        """Generate character image using Ideogram V3.
        
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
        full_prompt = f"portrait of {character_name}, {full_prompt}, centered, professional photography"
        
        logger.info(f"Generating character image for {character_name}")
        logger.debug(f"Prompt: {full_prompt}")
        
        try:
            # Submit request to Ideogram V3
            import fal_client
            
            # Submit the request
            request_data = {
                "prompt": full_prompt,
                "negative_prompt": self.visual_style.negative_prompt,
                "image_size": "square_hd",  # Portrait for characters
                "rendering_speed": self.visual_style.rendering_speed,
                "style": self.visual_style.style_type,
                "expand_prompt": self.visual_style.expand_prompt,
                "num_images": 1
            }
            
            # Add style references if available
            if self.visual_style.style_references:
                request_data["image_urls"] = self.visual_style.style_references[:3]  # Max 3 references
            
            # Submit and wait for result
            result = await fal_client.submit_async(
                "fal-ai/ideogram/v3",
                arguments=request_data
            )
            
            # Get the image URL
            if result and "images" in result and len(result["images"]) > 0:
                image_url = result["images"][0]["url"]
                
                # Save image
                if not save_path:
                    save_path = str(self.cache_dir / "characters" / f"{character_name.replace(' ', '_')}.png")
                
                Path(save_path).parent.mkdir(parents=True, exist_ok=True)
                
                # Download and save image
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
                raise ValueError("No image generated")
                
        except Exception as e:
            logger.error(f"Failed to generate character image: {e}")
            raise
    
    async def generate_scene_background(
        self,
        scene_number: int,
        environment_prompt: str,
        save_path: Optional[str] = None
    ) -> str:
        """Generate scene background using Ideogram V3.
        
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
        full_prompt = f"wide shot, environment, empty scene, no people, {full_prompt}"
        
        logger.info(f"Generating background for scene {scene_number}")
        logger.debug(f"Prompt: {full_prompt}")
        
        try:
            import fal_client
            
            # Submit request
            request_data = {
                "prompt": full_prompt,
                "negative_prompt": f"people, characters, humans, figures, {self.visual_style.negative_prompt}",
                "image_size": self.visual_style.get_ideogram_size(),
                "rendering_speed": self.visual_style.rendering_speed,
                "style": self.visual_style.style_type,
                "expand_prompt": self.visual_style.expand_prompt,
                "num_images": 1
            }
            
            # Submit and wait for result
            result = await fal_client.submit_async(
                "fal-ai/ideogram/v3",
                arguments=request_data
            )
            
            # Get the image URL
            if result and "images" in result and len(result["images"]) > 0:
                image_url = result["images"][0]["url"]
                
                # Save image
                if not save_path:
                    save_path = str(self.cache_dir / "scenes" / f"scene_{scene_number:03d}_bg.png")
                
                Path(save_path).parent.mkdir(parents=True, exist_ok=True)
                
                # Download and save
                await self._download_image(image_url, save_path)
                
                # Store scene visual
                if scene_number not in self.scene_visuals:
                    self.scene_visuals[scene_number] = SceneVisual(
                        scene_number=scene_number,
                        environment_prompt=full_prompt
                    )
                self.scene_visuals[scene_number].background_image_path = save_path
                self.scene_visuals[scene_number].background_image_url = image_url
                
                logger.info(f"Scene background saved: {save_path}")
                return save_path
            else:
                raise ValueError("No image generated")
                
        except Exception as e:
            logger.error(f"Failed to generate scene background: {e}")
            raise
    
    async def composite_character_in_scene(
        self,
        scene_number: int,
        character_name: str,
        position_prompt: Optional[str] = None,
        save_path: Optional[str] = None
    ) -> str:
        """Composite character into scene using Flux Kontext Multi.
        
        Args:
            scene_number: Scene number
            character_name: Character to composite
            position_prompt: Optional prompt for positioning
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
        
        if not character_visual.image_url or not scene_visual.background_image_url:
            raise ValueError("Image URLs not available for compositing")
        
        logger.info(f"Compositing {character_name} into scene {scene_number}")
        
        try:
            import fal_client
            
            # Prepare prompt
            if not position_prompt:
                position_prompt = f"Place {character_name} naturally in the scene, maintaining proper scale and lighting"
            
            # Submit request to Flux Kontext Multi
            request_data = {
                "prompt": position_prompt,
                "image_urls": [
                    scene_visual.background_image_url,  # Background first
                    character_visual.image_url           # Character second
                ],
                "guidance_scale": 3.5,
                "num_images": 1,
                "output_format": "png",
                "aspect_ratio": self.visual_style.aspect_ratio.replace(":", "_")  # Convert 16:9 to 16_9
            }
            
            # Submit and wait for result
            result = await fal_client.submit_async(
                "fal-ai/flux-pro/kontext/multi",
                arguments=request_data
            )
            
            # Get the composite image URL
            if result and "images" in result and len(result["images"]) > 0:
                image_url = result["images"][0]["url"]
                
                # Save composite
                if not save_path:
                    save_path = str(self.cache_dir / "composites" / 
                                  f"scene_{scene_number:03d}_{character_name.replace(' ', '_')}.png")
                
                Path(save_path).parent.mkdir(parents=True, exist_ok=True)
                
                # Download and save
                await self._download_image(image_url, save_path)
                
                # Store in scene visual
                self.scene_visuals[scene_number].composite_images[character_name] = save_path
                self.scene_visuals[scene_number].composite_urls[character_name] = image_url
                
                logger.info(f"Composite saved: {save_path}")
                return save_path
            else:
                raise ValueError("No composite generated")
                
        except Exception as e:
            logger.error(f"Failed to composite character: {e}")
            raise
    
    async def generate_talking_video_with_hedra(
        self,
        character_name: str,
        scene_number: int,
        audio_path: str,
        save_path: Optional[str] = None
    ) -> str:
        """Generate talking video using Hedra Character-2.
        
        Note: Hedra is a better alternative to Stable Avatar for lip-sync.
        
        Args:
            character_name: Character name
            scene_number: Scene number
            audio_path: Path to audio file
            save_path: Optional save path
            
        Returns:
            Path to generated video
        """
        # Get composite image or character image
        image_url = None
        if scene_number in self.scene_visuals:
            image_url = self.scene_visuals[scene_number].composite_urls.get(character_name)
        
        if not image_url and character_name in self.character_visuals:
            image_url = self.character_visuals[character_name].image_url
        
        if not image_url:
            raise ValueError(f"No image available for {character_name}")
        
        logger.info(f"Generating talking video for {character_name} in scene {scene_number}")
        
        try:
            import fal_client
            
            # Upload audio file
            with open(audio_path, 'rb') as f:
                audio_url = await fal_client.upload_async(f.read(), "audio/mpeg")
            
            # Submit request to Hedra
            request_data = {
                "image_url": image_url,
                "audio_url": audio_url,
                "aspect_ratio": self.visual_style.aspect_ratio.replace(":", "_")
            }
            
            # Submit and wait for result (Hedra can take longer)
            result = await fal_client.submit_async(
                "fal-ai/hedra-character-2",
                arguments=request_data
            )
            
            # Get the video URL
            if result and "video" in result:
                video_url = result["video"]["url"]
                
                # Save video
                if not save_path:
                    save_path = str(self.cache_dir / "videos" / 
                                  f"scene_{scene_number:03d}_{character_name.replace(' ', '_')}.mp4")
                
                Path(save_path).parent.mkdir(parents=True, exist_ok=True)
                
                # Download and save video
                await self._download_video(video_url, save_path)
                
                self.generated_videos.append(save_path)
                logger.info(f"Video saved: {save_path}")
                return save_path
            else:
                raise ValueError("No video generated")
                
        except Exception as e:
            logger.error(f"Failed to generate talking video: {e}")
            # Fallback to static image with audio
            logger.warning(f"Falling back to static image for {character_name}")
            return await self._create_static_video_fallback(
                image_url, audio_path, save_path
            )
    
    async def _create_static_video_fallback(
        self,
        image_url: str,
        audio_path: str,
        save_path: Optional[str] = None
    ) -> str:
        """Create a static video fallback when talking head generation fails."""
        # This would use FFmpeg to create a video from a static image and audio
        # Implementation depends on your FFmpeg setup
        logger.info("Creating static video fallback")
        
        if not save_path:
            save_path = str(self.cache_dir / "videos" / f"static_{hashlib.md5(image_url.encode()).hexdigest()}.mp4")
        
        # Download image first
        temp_image = str(self.cache_dir / "temp" / "temp_image.png")
        Path(temp_image).parent.mkdir(parents=True, exist_ok=True)
        await self._download_image(image_url, temp_image)
        
        # Use FFmpeg to create video
        import subprocess
        cmd = [
            'ffmpeg',
            '-loop', '1',
            '-i', temp_image,
            '-i', audio_path,
            '-c:v', 'libx264',
            '-c:a', 'aac',
            '-shortest',
            '-pix_fmt', 'yuv420p',
            '-y',
            save_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"FFmpeg failed: {result.stderr}")
        
        return save_path
    
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


# Updated preset visual styles for Ideogram V3
PRESET_STYLES_V2 = {
    "cinematic": VisualStyle(
        style_name="Cinematic",
        style_prompt="cinematic lighting, film grain, professional cinematography, depth of field, color graded, movie still",
        negative_prompt="cartoon, anime, illustration, painting, low quality, amateur",
        rendering_speed="QUALITY",
        style_type="REALISTIC"
    ),
    "realistic": VisualStyle(
        style_name="Photorealistic",
        style_prompt="photorealistic, high detail, natural lighting, professional photography, 8k resolution, sharp focus",
        negative_prompt="cartoon, anime, illustration, painting, artificial, cgi",
        rendering_speed="QUALITY",
        style_type="REALISTIC"
    ),
    "dramatic": VisualStyle(
        style_name="Dramatic",
        style_prompt="dramatic lighting, high contrast, moody atmosphere, cinematic composition, chiaroscuro",
        negative_prompt="bright, cheerful, cartoon, flat lighting, amateur",
        rendering_speed="BALANCED",
        style_type="REALISTIC"
    ),
    "tech_noir": VisualStyle(
        style_name="Tech Noir",
        style_prompt="tech noir style, neon lighting, cyberpunk aesthetic, dark atmosphere, futuristic, blade runner style",
        negative_prompt="bright, cheerful, medieval, historical, cartoon",
        rendering_speed="BALANCED",
        style_type="DESIGN"
    )
}