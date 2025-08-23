"""Scene compilation and generation module."""

import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from loguru import logger

from src.drama import DramaEngine


@dataclass
class SceneMetadata:
    """Metadata for a generated scene."""
    scene_id: str
    scene_number: int
    act_number: int
    location: str
    time: str
    duration_seconds: int = 90
    plot_line: str = "A"
    tension_level: float = 0.5
    quality_score: float = 0.0
    generated_at: Optional[datetime] = None


@dataclass
class DialogueLine:
    """A single line of dialogue."""
    character: str
    line: str
    emotion: str = "neutral"
    subtext: Optional[str] = None
    action: Optional[str] = None
    timing_seconds: float = 2.0


@dataclass
class Scene:
    """Complete scene data structure."""
    metadata: SceneMetadata
    description: str
    dialogue: List[DialogueLine] = field(default_factory=list)
    stage_directions: List[str] = field(default_factory=list)
    dramatic_operators: List[str] = field(default_factory=list)
    transitions: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert scene to dictionary."""
        return {
            "metadata": {
                "scene_id": self.metadata.scene_id,
                "scene_number": self.metadata.scene_number,
                "act_number": self.metadata.act_number,
                "location": self.metadata.location,
                "time": self.metadata.time,
                "duration_seconds": self.metadata.duration_seconds,
                "plot_line": self.metadata.plot_line,
                "tension_level": self.metadata.tension_level,
                "quality_score": self.metadata.quality_score,
                "generated_at": self.metadata.generated_at.isoformat() if self.metadata.generated_at else None
            },
            "description": self.description,
            "dialogue": [
                {
                    "character": d.character,
                    "line": d.line,
                    "emotion": d.emotion,
                    "subtext": d.subtext,
                    "action": d.action,
                    "timing_seconds": d.timing_seconds
                } for d in self.dialogue
            ],
            "stage_directions": self.stage_directions,
            "dramatic_operators": self.dramatic_operators,
            "transitions": self.transitions
        }
        
    def to_screenplay_format(self) -> str:
        """Convert scene to screenplay format."""
        output = []
        
        # Scene heading
        output.append(f"INT. {self.metadata.location.upper()} - {self.metadata.time.upper()}")
        output.append("")
        
        # Description
        if self.description:
            output.append(self.description)
            output.append("")
        
        # Stage directions and dialogue
        for direction in self.stage_directions[:1]:  # Opening direction
            output.append(direction)
            output.append("")
            
        for line in self.dialogue:
            # Character name
            output.append(f"\t\t\t{line.character.upper()}")
            
            # Action/emotion parenthetical
            if line.action or line.emotion != "neutral":
                parenthetical = line.action or f"({line.emotion})"
                output.append(f"\t\t({parenthetical})")
                
            # Dialogue
            output.append(f"\t{line.line}")
            output.append("")
            
        # Closing directions
        for direction in self.stage_directions[1:]:
            output.append(direction)
            output.append("")
            
        # Transition
        if "out" in self.transitions:
            output.append(f"{self.transitions['out'].upper()} TO:")
            
        return "\n".join(output)


class SceneCompiler:
    """Compiles scenes from various data sources."""
    
    def __init__(self, drama_engine: Optional[DramaEngine] = None):
        """Initialize the scene compiler.
        
        Args:
            drama_engine: Optional drama engine for enhancements
        """
        self.drama_engine = drama_engine or DramaEngine()
        self.compiled_scenes: List[Scene] = []
        
    def compile_scene(
        self,
        raw_scene_data: Dict[str, Any],
        scene_number: int,
        act_number: int
    ) -> Scene:
        """Compile a scene from raw data.
        
        Args:
            raw_scene_data: Raw scene data from LLM or simulation
            scene_number: Scene number in episode
            act_number: Act number
            
        Returns:
            Compiled Scene object
        """
        # Create metadata
        metadata = SceneMetadata(
            scene_id=f"S{act_number:02d}E{scene_number:02d}",
            scene_number=scene_number,
            act_number=act_number,
            location=raw_scene_data.get("location", "Unknown"),
            time=raw_scene_data.get("time", "Day"),
            duration_seconds=raw_scene_data.get("duration_seconds", 90),
            plot_line=raw_scene_data.get("plot_line", "A"),
            tension_level=raw_scene_data.get("tension", 0.5),
            quality_score=raw_scene_data.get("quality_score", 0.0),
            generated_at=datetime.now()
        )
        
        # Extract description
        description = raw_scene_data.get("description", "")
        
        # Compile dialogue
        dialogue = []
        for line_data in raw_scene_data.get("dialogue", []):
            dialogue.append(DialogueLine(
                character=line_data.get("character", "Unknown"),
                line=line_data.get("line", "..."),
                emotion=line_data.get("emotion", "neutral"),
                subtext=line_data.get("subtext"),
                action=line_data.get("action")
            ))
            
        # Extract stage directions
        stage_directions = raw_scene_data.get("stage_directions", [])
        if not stage_directions and description:
            # Generate basic stage directions from description
            stage_directions = [description]
            
        # Extract dramatic operators
        dramatic_operators = []
        if "dramatic_operators" in raw_scene_data:
            for op in raw_scene_data["dramatic_operators"]:
                if isinstance(op, dict):
                    dramatic_operators.append(op.get("name", op.get("type", "")))
                else:
                    dramatic_operators.append(str(op))
                    
        # Define transitions
        transitions = raw_scene_data.get("transitions", {})
        if not transitions:
            # Default transitions
            if scene_number > 1:
                transitions["in"] = "CUT"
            if metadata.tension_level > 0.8:
                transitions["out"] = "SMASH CUT"
            else:
                transitions["out"] = "CUT"
                
        # Create scene object
        scene = Scene(
            metadata=metadata,
            description=description,
            dialogue=dialogue,
            stage_directions=stage_directions,
            dramatic_operators=dramatic_operators,
            transitions=transitions
        )
        
        self.compiled_scenes.append(scene)
        logger.debug(f"Compiled scene {scene.metadata.scene_id}")
        
        return scene
        
    def compile_episode(
        self,
        episode_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Compile a complete episode from raw data.
        
        Args:
            episode_data: Raw episode data
            
        Returns:
            Compiled episode with formatted scenes
        """
        compiled_episode = {
            "title": episode_data.get("title", "Untitled"),
            "synopsis": episode_data.get("synopsis", ""),
            "themes": episode_data.get("themes", []),
            "genre": episode_data.get("genre", "drama"),
            "tone": episode_data.get("tone", "balanced"),
            "compiled_scenes": [],
            "screenplay": "",
            "statistics": {}
        }
        
        # Compile each scene
        scenes = episode_data.get("scenes", [])
        for i, raw_scene in enumerate(scenes):
            act_number = raw_scene.get("act_number", 1)
            scene_number = raw_scene.get("scene_number", i + 1)
            
            compiled_scene = self.compile_scene(raw_scene, scene_number, act_number)
            compiled_episode["compiled_scenes"].append(compiled_scene.to_dict())
            
        # Generate full screenplay
        screenplay_parts = []
        screenplay_parts.append(f"TITLE: {compiled_episode['title'].upper()}")
        screenplay_parts.append(f"\n{compiled_episode['synopsis']}\n")
        screenplay_parts.append("="*50 + "\n")
        
        for scene in self.compiled_scenes:
            screenplay_parts.append(scene.to_screenplay_format())
            screenplay_parts.append("\n" + "-"*30 + "\n")
            
        screenplay_parts.append("\nFADE OUT.")
        screenplay_parts.append("\nTHE END")
        
        compiled_episode["screenplay"] = "\n".join(screenplay_parts)
        
        # Calculate statistics
        compiled_episode["statistics"] = self._calculate_statistics()
        
        logger.info(f"Compiled episode '{compiled_episode['title']}' with {len(self.compiled_scenes)} scenes")
        
        return compiled_episode
        
    def _calculate_statistics(self) -> Dict[str, Any]:
        """Calculate episode statistics."""
        if not self.compiled_scenes:
            return {}
            
        total_duration = sum(s.metadata.duration_seconds for s in self.compiled_scenes)
        total_dialogue = sum(len(s.dialogue) for s in self.compiled_scenes)
        avg_tension = sum(s.metadata.tension_level for s in self.compiled_scenes) / len(self.compiled_scenes)
        avg_quality = sum(s.metadata.quality_score for s in self.compiled_scenes) / len(self.compiled_scenes)
        
        # Character line distribution
        character_lines = {}
        for scene in self.compiled_scenes:
            for line in scene.dialogue:
                character_lines[line.character] = character_lines.get(line.character, 0) + 1
                
        # Dramatic operator usage
        operator_usage = {}
        for scene in self.compiled_scenes:
            for op in scene.dramatic_operators:
                operator_usage[op] = operator_usage.get(op, 0) + 1
                
        return {
            "total_scenes": len(self.compiled_scenes),
            "total_duration_seconds": total_duration,
            "total_duration_minutes": total_duration / 60,
            "total_dialogue_lines": total_dialogue,
            "average_tension": avg_tension,
            "average_quality": avg_quality,
            "character_line_distribution": character_lines,
            "dramatic_operator_usage": operator_usage,
            "acts": {
                1: len([s for s in self.compiled_scenes if s.metadata.act_number == 1]),
                2: len([s for s in self.compiled_scenes if s.metadata.act_number == 2]),
                3: len([s for s in self.compiled_scenes if s.metadata.act_number == 3])
            }
        }
        
    def export_to_file(
        self,
        compiled_episode: Dict[str, Any],
        filepath: str,
        format: str = "json"
    ):
        """Export compiled episode to file.
        
        Args:
            compiled_episode: Compiled episode data
            filepath: Output file path
            format: Export format (json, screenplay, both)
        """
        if format in ["json", "both"]:
            json_path = filepath if filepath.endswith(".json") else f"{filepath}.json"
            with open(json_path, 'w') as f:
                json.dump(compiled_episode, f, indent=2)
            logger.info(f"Exported JSON to {json_path}")
            
        if format in ["screenplay", "both"]:
            script_path = filepath if filepath.endswith(".txt") else f"{filepath}_screenplay.txt"
            with open(script_path, 'w') as f:
                f.write(compiled_episode["screenplay"])
            logger.info(f"Exported screenplay to {script_path}")