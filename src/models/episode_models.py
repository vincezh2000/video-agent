"""Data models for episode structure."""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, validator


class Genre(str, Enum):
    """Episode genres."""
    DRAMA = "drama"
    COMEDY = "comedy"
    THRILLER = "thriller"
    SCIFI = "sci-fi"
    MYSTERY = "mystery"
    ROMANCE = "romance"
    ACTION = "action"
    HORROR = "horror"


class Tone(str, Enum):
    """Episode tones."""
    LIGHT = "light"
    BALANCED = "balanced"
    DARK = "dark"
    TENSE = "tense"
    COMEDIC = "comedic"
    SERIOUS = "serious"
    SUSPENSEFUL = "suspenseful"


class PlotLine(str, Enum):
    """Plot line identifiers."""
    A = "A"
    B = "B"
    C = "C"
    D = "D"


class CharacterModel(BaseModel):
    """Character data model."""
    id: str
    name: str
    backstory: str
    personality: Dict[str, float] = Field(default_factory=dict)
    age: Optional[int] = None
    occupation: Optional[str] = None
    relationships: Dict[str, str] = Field(default_factory=dict)
    goals: List[Dict[str, Any]] = Field(default_factory=list)
    
    @validator('personality')
    def validate_personality(cls, v):
        """Ensure personality traits are in valid range."""
        for trait, value in v.items():
            if not 0 <= value <= 1:
                raise ValueError(f"Personality trait {trait} must be between 0 and 1")
        return v


class DialogueModel(BaseModel):
    """Dialogue line model."""
    character: str
    line: str
    emotion: str = "neutral"
    subtext: Optional[str] = None
    action: Optional[str] = None
    timing_seconds: float = 2.0
    
    @validator('timing_seconds')
    def validate_timing(cls, v):
        """Ensure timing is positive."""
        if v <= 0:
            raise ValueError("Timing must be positive")
        return v


class SceneModel(BaseModel):
    """Scene data model."""
    scene_id: str
    scene_number: int = Field(ge=1)
    act_number: int = Field(ge=1, le=3)
    location: str
    time: str
    duration_seconds: int = Field(default=90, ge=30, le=300)
    plot_line: PlotLine = PlotLine.A
    
    description: str
    dialogue: List[DialogueModel] = Field(default_factory=list)
    stage_directions: List[str] = Field(default_factory=list)
    
    tension_level: float = Field(default=0.5, ge=0, le=1)
    quality_score: float = Field(default=0.0, ge=0, le=1)
    
    dramatic_operators: List[str] = Field(default_factory=list)
    transitions: Dict[str, str] = Field(default_factory=dict)
    
    characters_present: List[str] = Field(default_factory=list)
    emotional_trajectory: Optional[str] = None
    
    generated_at: Optional[datetime] = None
    
    class Config:
        use_enum_values = True


class ActModel(BaseModel):
    """Act structure model."""
    act_number: int = Field(ge=1, le=3)
    scenes: List[SceneModel] = Field(default_factory=list)
    duration_seconds: int = Field(ge=0)
    
    @validator('duration_seconds', always=True)
    def calculate_duration(cls, v, values):
        """Calculate act duration from scenes."""
        if 'scenes' in values:
            return sum(scene.duration_seconds for scene in values['scenes'])
        return v


class EpisodeModel(BaseModel):
    """Complete episode model."""
    episode_id: Optional[str] = None
    title: str
    synopsis: str
    themes: List[str] = Field(default_factory=list)
    genre: Genre = Genre.DRAMA
    tone: Tone = Tone.BALANCED
    
    acts: List[ActModel] = Field(default_factory=list)
    total_duration_seconds: int = Field(ge=0)
    
    characters: List[CharacterModel] = Field(default_factory=list)
    
    # Narrative metrics
    average_tension: float = Field(default=0.0, ge=0, le=1)
    average_quality: float = Field(default=0.0, ge=0, le=1)
    dramatic_peaks: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    generation_time_seconds: Optional[float] = None
    system_version: str = "1.0.0"
    
    @validator('total_duration_seconds', always=True)
    def calculate_total_duration(cls, v, values):
        """Calculate total duration from acts."""
        if 'acts' in values:
            return sum(act.duration_seconds for act in values['acts'])
        return v
    
    @validator('average_tension', always=True)
    def calculate_average_tension(cls, v, values):
        """Calculate average tension from scenes."""
        if 'acts' in values:
            all_scenes = []
            for act in values['acts']:
                all_scenes.extend(act.scenes)
            if all_scenes:
                return sum(s.tension_level for s in all_scenes) / len(all_scenes)
        return v
    
    @validator('average_quality', always=True)
    def calculate_average_quality(cls, v, values):
        """Calculate average quality from scenes."""
        if 'acts' in values:
            all_scenes = []
            for act in values['acts']:
                all_scenes.extend(act.scenes)
            if all_scenes:
                return sum(s.quality_score for s in all_scenes) / len(all_scenes)
        return v
    
    def get_scene_count(self) -> int:
        """Get total number of scenes."""
        return sum(len(act.scenes) for act in self.acts)
    
    def get_dialogue_count(self) -> int:
        """Get total number of dialogue lines."""
        count = 0
        for act in self.acts:
            for scene in act.scenes:
                count += len(scene.dialogue)
        return count
    
    def get_character_stats(self) -> Dict[str, Dict[str, int]]:
        """Get character statistics."""
        stats = {}
        for act in self.acts:
            for scene in act.scenes:
                for dialogue in scene.dialogue:
                    char = dialogue.character
                    if char not in stats:
                        stats[char] = {"lines": 0, "scenes": 0}
                    stats[char]["lines"] += 1
                    
                for char in scene.characters_present:
                    if char not in stats:
                        stats[char] = {"lines": 0, "scenes": 0}
                    stats[char]["scenes"] += 1
                    
        return stats


class SimulationEventModel(BaseModel):
    """Simulation event model."""
    timestamp: datetime
    event_type: str
    description: str
    participants: List[str] = Field(default_factory=list)
    location: str
    impact: float = Field(default=0.5, ge=0, le=1)
    consequences: List[str] = Field(default_factory=list)


class SimulationDataModel(BaseModel):
    """Simulation data model."""
    start_time: datetime
    end_time: datetime
    duration_hours: float
    
    agents: List[CharacterModel] = Field(default_factory=list)
    events: List[SimulationEventModel] = Field(default_factory=list)
    
    narrative_tension_curve: List[float] = Field(default_factory=list)
    dramatic_peaks: List[Dict[str, Any]] = Field(default_factory=list)
    
    world_rules: List[str] = Field(default_factory=list)
    established_facts: List[str] = Field(default_factory=list)
    
    statistics: Dict[str, Any] = Field(default_factory=dict)


class QualityMetricsModel(BaseModel):
    """Quality metrics for generated content."""
    character_consistency: float = Field(ge=0, le=1)
    narrative_coherence: float = Field(ge=0, le=1)
    dialogue_naturalness: float = Field(ge=0, le=1)
    dramatic_effectiveness: float = Field(ge=0, le=1)
    
    overall_score: float = Field(ge=0, le=1)
    
    @validator('overall_score', always=True)
    def calculate_overall(cls, v, values):
        """Calculate overall score from components."""
        components = [
            values.get('character_consistency', 0),
            values.get('narrative_coherence', 0),
            values.get('dialogue_naturalness', 0),
            values.get('dramatic_effectiveness', 0)
        ]
        return sum(components) / len(components) if components else 0
    
    def meets_thresholds(self, thresholds: Dict[str, float]) -> bool:
        """Check if metrics meet quality thresholds."""
        return all([
            self.character_consistency >= thresholds.get('character_consistency', 0.8),
            self.narrative_coherence >= thresholds.get('narrative_coherence', 0.85),
            self.dialogue_naturalness >= thresholds.get('dialogue_naturalness', 0.75),
            self.overall_score >= thresholds.get('minimum_scene_quality', 0.6)
        ])


@dataclass
class GenerationConfig:
    """Configuration for episode generation."""
    # LLM settings
    llm_model: str = "gpt-4"
    temperature: float = 0.8
    max_tokens: Optional[int] = None
    
    # Episode settings
    target_duration_minutes: int = 22
    max_scenes: int = 14
    scene_duration_seconds: int = 90
    
    # Drama settings
    max_operators_per_scene: int = 3
    min_tension: float = 0.2
    max_tension: float = 0.95
    
    # Quality thresholds
    quality_thresholds: Dict[str, float] = field(default_factory=lambda: {
        "character_consistency": 0.8,
        "narrative_coherence": 0.85,
        "dialogue_naturalness": 0.75,
        "minimum_scene_quality": 0.6
    })
    
    # Simulation settings
    simulation_hours: float = 3.0
    simulation_time_step_minutes: int = 15
    max_agents: int = 10
    
    # Output settings
    output_format: str = "json"
    include_screenplay: bool = True
    include_metadata: bool = True
    save_intermediate: bool = True