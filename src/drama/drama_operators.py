"""Dramatic operators for enhancing narrative tension and engagement."""

import random
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from loguru import logger


class DramaticOperatorType(Enum):
    """Types of dramatic operators available."""
    REVERSAL = "reversal"  # Subvert expectations
    FORESHADOWING = "foreshadowing"  # Plant seeds for future events
    CALLBACK = "callback"  # Reference earlier moments
    ESCALATION = "escalation"  # Raise stakes
    IRONY = "irony"  # Create meaningful contrasts
    PARALLEL = "parallel"  # Mirror other storylines
    CLIFFHANGER = "cliffhanger"  # Create suspense
    REVELATION = "revelation"  # Reveal hidden information
    CONFLICT = "conflict"  # Introduce opposition
    COMPLICATION = "complication"  # Add obstacles


@dataclass
class DramaticOperator:
    """A single dramatic operator."""
    type: DramaticOperatorType
    name: str
    description: str
    intensity: float  # 0.0 to 1.0
    prerequisites: List[str] = field(default_factory=list)
    consequences: List[str] = field(default_factory=list)
    emotional_impact: Dict[str, float] = field(default_factory=dict)
    
    def apply(self, scene_data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply this operator to a scene.
        
        Args:
            scene_data: Current scene data
            
        Returns:
            Modified scene data
        """
        modified = scene_data.copy()
        
        # Add operator metadata
        if "dramatic_operators" not in modified:
            modified["dramatic_operators"] = []
        modified["dramatic_operators"].append({
            "type": self.type.value,
            "name": self.name,
            "intensity": self.intensity
        })
        
        # Modify tension
        current_tension = modified.get("tension", 0.5)
        modified["tension"] = min(1.0, current_tension + self.intensity * 0.3)
        
        # Add consequences to scene
        if "consequences" not in modified:
            modified["consequences"] = []
        modified["consequences"].extend(self.consequences)
        
        return modified


class DramaOperatorLibrary:
    """Library of dramatic operators."""
    
    def __init__(self):
        """Initialize the operator library."""
        self.operators = self._create_operators()
        logger.info(f"Initialized drama library with {len(self.operators)} operators")
        
    def _create_operators(self) -> Dict[str, DramaticOperator]:
        """Create the standard set of dramatic operators."""
        operators = {}
        
        # Reversals
        operators["sudden_betrayal"] = DramaticOperator(
            type=DramaticOperatorType.REVERSAL,
            name="Sudden Betrayal",
            description="A trusted character reveals their true antagonistic nature",
            intensity=0.9,
            prerequisites=["established_trust"],
            consequences=["broken_trust", "new_antagonist"],
            emotional_impact={"shock": 0.8, "anger": 0.6, "sadness": 0.4}
        )
        
        operators["false_victory"] = DramaticOperator(
            type=DramaticOperatorType.REVERSAL,
            name="False Victory",
            description="What seems like success turns into failure",
            intensity=0.7,
            prerequisites=["apparent_success"],
            consequences=["setback", "new_challenge"],
            emotional_impact={"disappointment": 0.7, "frustration": 0.5}
        )
        
        # Foreshadowing
        operators["ominous_warning"] = DramaticOperator(
            type=DramaticOperatorType.FORESHADOWING,
            name="Ominous Warning",
            description="A subtle hint about future danger",
            intensity=0.4,
            prerequisites=[],
            consequences=["future_threat"],
            emotional_impact={"anxiety": 0.3, "curiosity": 0.4}
        )
        
        operators["symbolic_object"] = DramaticOperator(
            type=DramaticOperatorType.FORESHADOWING,
            name="Symbolic Object",
            description="An object that will become important later",
            intensity=0.3,
            prerequisites=[],
            consequences=["chekhov_gun"],
            emotional_impact={"curiosity": 0.2}
        )
        
        # Callbacks
        operators["echo_moment"] = DramaticOperator(
            type=DramaticOperatorType.CALLBACK,
            name="Echo Moment",
            description="A situation that mirrors an earlier scene",
            intensity=0.5,
            prerequisites=["previous_similar_scene"],
            consequences=["thematic_resonance"],
            emotional_impact={"recognition": 0.4, "satisfaction": 0.3}
        )
        
        operators["promise_fulfilled"] = DramaticOperator(
            type=DramaticOperatorType.CALLBACK,
            name="Promise Fulfilled",
            description="A character keeps or breaks an earlier promise",
            intensity=0.6,
            prerequisites=["earlier_promise"],
            consequences=["character_growth", "trust_change"],
            emotional_impact={"satisfaction": 0.5, "respect": 0.4}
        )
        
        # Escalations
        operators["raising_stakes"] = DramaticOperator(
            type=DramaticOperatorType.ESCALATION,
            name="Raising Stakes",
            description="The consequences of failure become more severe",
            intensity=0.7,
            prerequisites=["existing_conflict"],
            consequences=["increased_pressure", "urgent_action"],
            emotional_impact={"tension": 0.6, "urgency": 0.7}
        )
        
        operators["ticking_clock"] = DramaticOperator(
            type=DramaticOperatorType.ESCALATION,
            name="Ticking Clock",
            description="A deadline creates time pressure",
            intensity=0.8,
            prerequisites=[],
            consequences=["time_limit", "forced_decision"],
            emotional_impact={"urgency": 0.8, "stress": 0.6}
        )
        
        # Irony
        operators["dramatic_irony"] = DramaticOperator(
            type=DramaticOperatorType.IRONY,
            name="Dramatic Irony",
            description="The audience knows something characters don't",
            intensity=0.5,
            prerequisites=["hidden_information"],
            consequences=["tension_from_knowledge"],
            emotional_impact={"anticipation": 0.6, "frustration": 0.3}
        )
        
        operators["situational_irony"] = DramaticOperator(
            type=DramaticOperatorType.IRONY,
            name="Situational Irony",
            description="The outcome is opposite of what's expected",
            intensity=0.6,
            prerequisites=["clear_expectation"],
            consequences=["subverted_expectation"],
            emotional_impact={"surprise": 0.5, "amusement": 0.3}
        )
        
        # Cliffhangers
        operators["unresolved_danger"] = DramaticOperator(
            type=DramaticOperatorType.CLIFFHANGER,
            name="Unresolved Danger",
            description="Scene ends with character in peril",
            intensity=0.9,
            prerequisites=["immediate_threat"],
            consequences=["must_resolve_next"],
            emotional_impact={"anxiety": 0.8, "excitement": 0.6}
        )
        
        operators["shocking_revelation"] = DramaticOperator(
            type=DramaticOperatorType.CLIFFHANGER,
            name="Shocking Revelation",
            description="Scene ends with game-changing information",
            intensity=0.85,
            prerequisites=["hidden_truth"],
            consequences=["paradigm_shift"],
            emotional_impact={"shock": 0.9, "curiosity": 0.7}
        )
        
        # Revelations
        operators["hidden_connection"] = DramaticOperator(
            type=DramaticOperatorType.REVELATION,
            name="Hidden Connection",
            description="Two seemingly unrelated things are connected",
            intensity=0.7,
            prerequisites=["multiple_plot_threads"],
            consequences=["plot_convergence"],
            emotional_impact={"surprise": 0.6, "satisfaction": 0.5}
        )
        
        operators["true_identity"] = DramaticOperator(
            type=DramaticOperatorType.REVELATION,
            name="True Identity",
            description="A character's real identity is revealed",
            intensity=0.8,
            prerequisites=["disguised_character"],
            consequences=["relationship_change", "new_dynamics"],
            emotional_impact={"shock": 0.7, "betrayal": 0.5}
        )
        
        return operators
        
    def get_operator(self, name: str) -> Optional[DramaticOperator]:
        """Get a specific operator by name.
        
        Args:
            name: Operator name
            
        Returns:
            DramaticOperator or None if not found
        """
        return self.operators.get(name)
        
    def get_operators_by_type(self, op_type: DramaticOperatorType) -> List[DramaticOperator]:
        """Get all operators of a specific type.
        
        Args:
            op_type: Type of operator
            
        Returns:
            List of matching operators
        """
        return [op for op in self.operators.values() if op.type == op_type]
        
    def suggest_operators(
        self,
        scene_context: Dict[str, Any],
        max_operators: int = 3
    ) -> List[DramaticOperator]:
        """Suggest appropriate operators for a scene.
        
        Args:
            scene_context: Current scene context
            max_operators: Maximum operators to suggest
            
        Returns:
            List of suggested operators
        """
        suggestions = []
        available_prerequisites = set(scene_context.get("available_prerequisites", []))
        current_tension = scene_context.get("tension", 0.5)
        
        # Filter operators by prerequisites
        eligible = []
        for operator in self.operators.values():
            if not operator.prerequisites or \
               any(prereq in available_prerequisites for prereq in operator.prerequisites):
                eligible.append(operator)
                
        # Score operators based on context
        scored = []
        for operator in eligible:
            score = self._score_operator(operator, scene_context, current_tension)
            scored.append((score, operator))
            
        # Sort by score and return top operators
        scored.sort(reverse=True, key=lambda x: x[0])
        
        for score, operator in scored[:max_operators]:
            if score > 0.3:  # Minimum threshold
                suggestions.append(operator)
                logger.debug(f"Suggested {operator.name} with score {score:.2f}")
                
        return suggestions
        
    def _score_operator(
        self,
        operator: DramaticOperator,
        context: Dict[str, Any],
        current_tension: float
    ) -> float:
        """Score an operator's appropriateness.
        
        Args:
            operator: Operator to score
            context: Scene context
            current_tension: Current narrative tension
            
        Returns:
            Score (0.0 to 1.0)
        """
        score = 0.0
        
        # Tension-based scoring
        if current_tension < 0.3:
            # Low tension - prefer escalation and conflict
            if operator.type in [DramaticOperatorType.ESCALATION, DramaticOperatorType.CONFLICT]:
                score += 0.4
        elif current_tension > 0.7:
            # High tension - prefer revelations and reversals
            if operator.type in [DramaticOperatorType.REVELATION, DramaticOperatorType.REVERSAL]:
                score += 0.4
        else:
            # Medium tension - variety is good
            score += 0.2
            
        # Act-based scoring
        act_number = context.get("act_number", 1)
        if act_number == 1:
            # Act 1 - setup and foreshadowing
            if operator.type == DramaticOperatorType.FORESHADOWING:
                score += 0.3
        elif act_number == 2:
            # Act 2 - complications and escalation
            if operator.type in [DramaticOperatorType.COMPLICATION, DramaticOperatorType.ESCALATION]:
                score += 0.3
        else:
            # Act 3 - revelations and resolution
            if operator.type in [DramaticOperatorType.REVELATION, DramaticOperatorType.CALLBACK]:
                score += 0.3
                
        # Scene position scoring
        scene_number = context.get("scene_number", 1)
        total_scenes = context.get("total_scenes", 14)
        position_ratio = scene_number / total_scenes
        
        if position_ratio > 0.9:
            # Near end - cliffhangers good
            if operator.type == DramaticOperatorType.CLIFFHANGER:
                score += 0.5
                
        # Prerequisite satisfaction bonus
        if operator.prerequisites:
            available = set(context.get("available_prerequisites", []))
            satisfaction = len(available & set(operator.prerequisites)) / len(operator.prerequisites)
            score += satisfaction * 0.2
            
        # Add some randomness for variety
        score += random.uniform(-0.1, 0.1)
        
        return max(0.0, min(1.0, score))


class PlotPatternManager:
    """Manages plot pattern interweaving (e.g., ABABCAB pattern)."""
    
    def __init__(self, pattern: str = "ABABCAB"):
        """Initialize plot pattern manager.
        
        Args:
            pattern: Plot interweaving pattern
        """
        self.pattern = pattern
        self.current_index = 0
        self.plot_lines = self._extract_plot_lines(pattern)
        logger.info(f"Initialized plot pattern: {pattern}")
        
    def _extract_plot_lines(self, pattern: str) -> List[str]:
        """Extract unique plot lines from pattern."""
        return sorted(list(set(pattern)))
        
    def get_current_plot_line(self) -> str:
        """Get the current plot line in the pattern."""
        if self.current_index >= len(self.pattern):
            self.current_index = 0
        return self.pattern[self.current_index]
        
    def advance(self) -> str:
        """Advance to next plot line in pattern.
        
        Returns:
            Next plot line
        """
        plot_line = self.get_current_plot_line()
        self.current_index += 1
        return plot_line
        
    def get_plot_distribution(self) -> Dict[str, float]:
        """Get the distribution of plot lines in the pattern.
        
        Returns:
            Dictionary mapping plot lines to their frequency
        """
        distribution = {}
        for plot in self.plot_lines:
            distribution[plot] = self.pattern.count(plot) / len(self.pattern)
        return distribution
        
    def suggest_next_scenes(self, num_scenes: int = 3) -> List[str]:
        """Suggest the next N plot lines.
        
        Args:
            num_scenes: Number of scenes to suggest
            
        Returns:
            List of plot lines
        """
        suggestions = []
        temp_index = self.current_index
        
        for _ in range(num_scenes):
            if temp_index >= len(self.pattern):
                temp_index = 0
            suggestions.append(self.pattern[temp_index])
            temp_index += 1
            
        return suggestions
        
    def is_balanced(self) -> bool:
        """Check if the pattern is well-balanced.
        
        Returns:
            True if no plot line dominates too heavily
        """
        distribution = self.get_plot_distribution()
        max_freq = max(distribution.values())
        min_freq = min(distribution.values())
        
        # Pattern is balanced if no plot line is more than 3x another
        return max_freq / min_freq <= 3.0 if min_freq > 0 else False


class DramaEngine:
    """Main engine for applying dramatic enhancements."""
    
    def __init__(self):
        """Initialize the drama engine."""
        self.operator_library = DramaOperatorLibrary()
        self.pattern_manager = PlotPatternManager()
        self.applied_operators: List[Tuple[str, DramaticOperator]] = []
        
    def enhance_scene(
        self,
        scene_data: Dict[str, Any],
        max_operators: int = 3
    ) -> Dict[str, Any]:
        """Enhance a scene with dramatic operators.
        
        Args:
            scene_data: Original scene data
            max_operators: Maximum operators to apply
            
        Returns:
            Enhanced scene data
        """
        enhanced = scene_data.copy()
        
        # Get appropriate plot line
        plot_line = self.pattern_manager.advance()
        enhanced["plot_line"] = plot_line
        
        # Build context for operator selection
        context = {
            "tension": enhanced.get("tension", 0.5),
            "act_number": enhanced.get("act_number", 1),
            "scene_number": enhanced.get("scene_number", 1),
            "total_scenes": enhanced.get("total_scenes", 14),
            "available_prerequisites": self._get_available_prerequisites()
        }
        
        # Get operator suggestions
        suggested_operators = self.operator_library.suggest_operators(context, max_operators)
        
        # Apply operators
        for operator in suggested_operators:
            enhanced = operator.apply(enhanced)
            self.applied_operators.append((enhanced.get("scene_id", "unknown"), operator))
            logger.info(f"Applied {operator.name} to scene")
            
        # Update emotional trajectory
        if suggested_operators:
            emotional_impacts = {}
            for operator in suggested_operators:
                for emotion, impact in operator.emotional_impact.items():
                    emotional_impacts[emotion] = emotional_impacts.get(emotion, 0) + impact
            enhanced["emotional_impacts"] = emotional_impacts
            
        return enhanced
        
    def _get_available_prerequisites(self) -> List[str]:
        """Get prerequisites established by previous operators."""
        prerequisites = []
        for _, operator in self.applied_operators:
            prerequisites.extend(operator.consequences)
        return prerequisites
        
    def analyze_dramatic_arc(self, scenes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze the dramatic arc of a sequence of scenes.
        
        Args:
            scenes: List of scene data
            
        Returns:
            Analysis of dramatic arc
        """
        tensions = [s.get("tension", 0.5) for s in scenes]
        
        # Find peaks and valleys
        peaks = []
        valleys = []
        
        for i in range(1, len(tensions) - 1):
            if tensions[i] > tensions[i-1] and tensions[i] > tensions[i+1]:
                peaks.append((i, tensions[i]))
            elif tensions[i] < tensions[i-1] and tensions[i] < tensions[i+1]:
                valleys.append((i, tensions[i]))
                
        # Calculate arc metrics
        average_tension = sum(tensions) / len(tensions) if tensions else 0
        tension_variance = sum((t - average_tension) ** 2 for t in tensions) / len(tensions) if tensions else 0
        
        # Check for three-act structure
        act_boundaries = [len(scenes) // 3, 2 * len(scenes) // 3]
        act1_tension = sum(tensions[:act_boundaries[0]]) / act_boundaries[0] if act_boundaries[0] > 0 else 0
        act2_tension = sum(tensions[act_boundaries[0]:act_boundaries[1]]) / (act_boundaries[1] - act_boundaries[0]) if act_boundaries[1] > act_boundaries[0] else 0
        act3_tension = sum(tensions[act_boundaries[1]:]) / (len(tensions) - act_boundaries[1]) if len(tensions) > act_boundaries[1] else 0
        
        return {
            "average_tension": average_tension,
            "tension_variance": tension_variance,
            "peaks": peaks,
            "valleys": valleys,
            "num_peaks": len(peaks),
            "num_valleys": len(valleys),
            "act_tensions": {
                "act1": act1_tension,
                "act2": act2_tension,
                "act3": act3_tension
            },
            "has_rising_action": act2_tension > act1_tension,
            "has_climax": len(peaks) > 0 and max(peaks, key=lambda x: x[1])[0] > len(scenes) * 0.6,
            "operator_distribution": self._get_operator_distribution()
        }
        
    def _get_operator_distribution(self) -> Dict[str, int]:
        """Get distribution of applied operators by type."""
        distribution = {}
        for _, operator in self.applied_operators:
            op_type = operator.type.value
            distribution[op_type] = distribution.get(op_type, 0) + 1
        return distribution