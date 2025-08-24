"""Script extractor for video generation pipeline."""

import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from pathlib import Path
from loguru import logger


@dataclass
class DialogueLine:
    """Single dialogue line with all metadata."""
    character: str
    line: str
    emotion: str
    action: str
    subtext: str
    order: int
    duration_estimate: float = 3.0  # seconds


@dataclass
class SceneData:
    """Extracted scene data for video generation."""
    scene_number: int
    act_number: int
    location: str
    time: str
    description: str
    characters: List[str]
    dialogues: List[DialogueLine]
    environment_description: str
    dramatic_elements: List[Dict[str, Any]] = field(default_factory=list)
    
    def get_character_dialogues(self, character: str) -> List[DialogueLine]:
        """Get all dialogues for a specific character."""
        return [d for d in self.dialogues if d.character == character]
    
    def get_dialogue_sequence(self) -> List[Dict[str, Any]]:
        """Get dialogue sequence for video generation."""
        sequence = []
        for dialogue in self.dialogues:
            sequence.append({
                "character": dialogue.character,
                "line": dialogue.line,
                "emotion": dialogue.emotion,
                "action": dialogue.action,
                "subtext": dialogue.subtext,
                "order": dialogue.order,
                "duration": dialogue.duration_estimate
            })
        return sequence


@dataclass
class CharacterProfile:
    """Character profile for consistent visual generation."""
    name: str
    description: str
    personality_traits: Dict[str, float]
    age: Optional[int]
    occupation: Optional[str]
    visual_description: str = ""
    appearance_keywords: List[str] = field(default_factory=list)
    
    def generate_visual_prompt(self) -> str:
        """Generate prompt for character image generation."""
        # Build visual description from available data
        parts = []
        
        if self.visual_description:
            parts.append(self.visual_description)
        else:
            # Generate from attributes
            if self.age:
                age_range = "young" if self.age < 30 else "middle-aged" if self.age < 50 else "senior"
                parts.append(f"{age_range} person")
            
            if self.occupation:
                parts.append(f"dressed as a {self.occupation}")
            
            # Add personality-based visual cues
            if self.personality_traits.get("conscientiousness", 0) > 0.7:
                parts.append("well-groomed, professional appearance")
            if self.personality_traits.get("openness", 0) > 0.7:
                parts.append("creative, unique style")
            
        if self.appearance_keywords:
            parts.extend(self.appearance_keywords)
        
        return ", ".join(parts) if parts else f"professional portrait of {self.name}"


class ScriptExtractor:
    """Extracts and processes script data for video generation."""
    
    def __init__(self):
        """Initialize script extractor."""
        self.scenes: List[SceneData] = []
        self.characters: Dict[str, CharacterProfile] = {}
        self.episode_metadata: Dict[str, Any] = {}
        
    def extract_from_json(self, json_path: str) -> Dict[str, Any]:
        """Extract all necessary data from episode JSON.
        
        Args:
            json_path: Path to episode JSON file
            
        Returns:
            Extracted data structure for video generation
        """
        with open(json_path, 'r', encoding='utf-8') as f:
            episode_data = json.load(f)
        
        # Extract metadata
        self.episode_metadata = {
            "title": episode_data.get("title", "Untitled"),
            "synopsis": episode_data.get("synopsis", ""),
            "genre": episode_data.get("genre", "drama"),
            "tone": episode_data.get("tone", "neutral"),
            "themes": episode_data.get("themes", [])
        }
        
        # Extract characters
        self._extract_characters(episode_data)
        
        # Extract scenes
        self._extract_scenes(episode_data)
        
        # Generate extraction summary
        extraction = {
            "metadata": self.episode_metadata,
            "characters": {name: self._character_to_dict(char) 
                          for name, char in self.characters.items()},
            "scenes": [self._scene_to_dict(scene) for scene in self.scenes],
            "statistics": self._generate_statistics()
        }
        
        logger.info(f"Extracted {len(self.scenes)} scenes with {len(self.characters)} characters")
        return extraction
    
    def _extract_characters(self, episode_data: Dict[str, Any]):
        """Extract character profiles from episode data."""
        # Get characters from simulation data if available
        if "simulation_data" in episode_data:
            for char_data in episode_data["simulation_data"].get("characters", []):
                character = CharacterProfile(
                    name=char_data.get("name", "Unknown"),
                    description=char_data.get("backstory", ""),
                    personality_traits=char_data.get("personality", {}),
                    age=char_data.get("age"),
                    occupation=char_data.get("occupation")
                )
                self.characters[character.name] = character
        
        # Also extract from characters list if present
        if "characters" in episode_data:
            for char_data in episode_data["characters"]:
                name = char_data.get("name", "Unknown")
                if name not in self.characters:
                    character = CharacterProfile(
                        name=name,
                        description=char_data.get("backstory", ""),
                        personality_traits=char_data.get("personality", {}),
                        age=char_data.get("age"),
                        occupation=char_data.get("occupation")
                    )
                    self.characters[name] = character
        
        # Extract any characters mentioned in scenes but not defined
        for scene in episode_data.get("scenes", []):
            for char_name in scene.get("characters", []):
                if char_name not in self.characters and not self._is_special_character(char_name):
                    # Create basic profile for undefined characters
                    self.characters[char_name] = CharacterProfile(
                        name=char_name,
                        description=f"Character in {self.episode_metadata['title']}",
                        personality_traits={}
                    )
    
    def _extract_scenes(self, episode_data: Dict[str, Any]):
        """Extract scene data from episode."""
        for scene_data in episode_data.get("scenes", []):
            # Extract dialogues
            dialogues = []
            for i, dialogue_data in enumerate(scene_data.get("dialogue", [])):
                dialogue = DialogueLine(
                    character=dialogue_data.get("character", "Unknown"),
                    line=dialogue_data.get("line", ""),
                    emotion=dialogue_data.get("emotion", "neutral"),
                    action=dialogue_data.get("action", ""),
                    subtext=dialogue_data.get("subtext", ""),
                    order=i,
                    duration_estimate=self._estimate_dialogue_duration(dialogue_data.get("line", ""))
                )
                dialogues.append(dialogue)
            
            # Extract environment description
            env_description = self._extract_environment_description(scene_data)
            
            # Create scene
            scene = SceneData(
                scene_number=scene_data.get("scene_number", 0),
                act_number=scene_data.get("act_number", 1),
                location=scene_data.get("location", "Unknown Location"),
                time=scene_data.get("time", "Day"),
                description=scene_data.get("description", ""),
                characters=scene_data.get("characters", []),
                dialogues=dialogues,
                environment_description=env_description,
                dramatic_elements=scene_data.get("dramatic_operators", [])
            )
            
            self.scenes.append(scene)
    
    def _extract_environment_description(self, scene_data: Dict[str, Any]) -> str:
        """Extract environment description from scene."""
        description = scene_data.get("description", "")
        location = scene_data.get("location", "")
        time = scene_data.get("time", "")
        
        # Parse key environmental details from description
        env_parts = []
        
        # Location
        if location:
            env_parts.append(f"Location: {location}")
        
        # Time of day
        if time:
            env_parts.append(f"Time: {time}")
        
        # Extract visual elements from description
        if description:
            # Look for environmental keywords
            env_keywords = ["light", "room", "office", "building", "street", "outdoor", 
                          "indoor", "dark", "bright", "cold", "warm", "sterile", "cozy"]
            
            for keyword in env_keywords:
                if keyword in description.lower():
                    env_parts.append(f"Atmosphere: {keyword}")
                    break
        
        return ". ".join(env_parts) if env_parts else "Modern indoor setting"
    
    def _estimate_dialogue_duration(self, text: str) -> float:
        """Estimate duration of dialogue in seconds."""
        # Rough estimate: 150 words per minute
        words = len(text.split())
        return max(2.0, (words / 150) * 60 + 1.0)  # Add 1 second buffer, minimum 2 seconds
    
    def _is_special_character(self, name: str) -> bool:
        """Check if character name is a special/system character."""
        special = ["AI System", "System", "Narrator", "off-screen", "Family", "Investors"]
        return any(s in name for s in special)
    
    def _character_to_dict(self, character: CharacterProfile) -> Dict[str, Any]:
        """Convert character to dictionary."""
        return {
            "name": character.name,
            "description": character.description,
            "personality_traits": character.personality_traits,
            "age": character.age,
            "occupation": character.occupation,
            "visual_prompt": character.generate_visual_prompt()
        }
    
    def _scene_to_dict(self, scene: SceneData) -> Dict[str, Any]:
        """Convert scene to dictionary."""
        return {
            "scene_number": scene.scene_number,
            "act_number": scene.act_number,
            "location": scene.location,
            "time": scene.time,
            "description": scene.description,
            "environment_description": scene.environment_description,
            "characters": scene.characters,
            "dialogue_sequence": scene.get_dialogue_sequence(),
            "total_duration": sum(d.duration_estimate for d in scene.dialogues)
        }
    
    def _generate_statistics(self) -> Dict[str, Any]:
        """Generate extraction statistics."""
        total_dialogues = sum(len(scene.dialogues) for scene in self.scenes)
        total_duration = sum(
            sum(d.duration_estimate for d in scene.dialogues) 
            for scene in self.scenes
        )
        
        return {
            "total_scenes": len(self.scenes),
            "total_characters": len(self.characters),
            "total_dialogues": total_dialogues,
            "estimated_duration_seconds": total_duration,
            "estimated_duration_minutes": total_duration / 60
        }
    
    def save_extraction(self, output_path: str):
        """Save extracted data to file."""
        extraction = {
            "metadata": self.episode_metadata,
            "characters": {name: self._character_to_dict(char) 
                          for name, char in self.characters.items()},
            "scenes": [self._scene_to_dict(scene) for scene in self.scenes],
            "statistics": self._generate_statistics()
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(extraction, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved extraction to {output_path}")


def extract_episode_for_video(json_path: str, output_path: Optional[str] = None) -> Dict[str, Any]:
    """Convenience function to extract episode data for video generation.
    
    Args:
        json_path: Path to episode JSON
        output_path: Optional path to save extraction
        
    Returns:
        Extracted data
    """
    extractor = ScriptExtractor()
    extraction = extractor.extract_from_json(json_path)
    
    if output_path:
        extractor.save_extraction(output_path)
    
    return extraction