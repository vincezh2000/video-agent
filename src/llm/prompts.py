"""Prompt templates for the Showrunner system."""

from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class PromptTemplate:
    """A single prompt template."""
    name: str
    system: str
    user: str
    requires_json: bool = False
    temperature: float = 0.8


class PromptTemplates:
    """Collection of all prompt templates used in the system."""
    
    # Stage 1: Concept Generation
    CONCEPT_GENERATION = PromptTemplate(
        name="concept_generation",
        system="""You are a creative TV writer specializing in generating compelling story concepts.
Your task is to create original, engaging scene concepts that emerge naturally from character interactions and simulation data.""",
        user="""## Creative Concept Generation

Simulation context:
- Characters involved: {characters}
- Location: {location}
- Time: {time}
- Recent events: {recent_events}
- Character emotional states: {character_states}

Story requirements:
- Genre: {genre}
- Tone: {tone}
- Episode themes: {themes}

Generate 3 different creative concepts for the next scene.
Each concept should:
1. Emerge naturally from the simulation context
2. Advance character arcs
3. Create dramatic tension
4. Be surprising yet inevitable

Output as JSON:
{{
    "concepts": [
        {{
            "id": "concept_1",
            "one_line_pitch": "Brief, compelling description",
            "key_conflict": "Central tension or problem",
            "character_dynamics": "How characters interact",
            "dramatic_potential": 0.0-1.0,
            "justification": "Why this works"
        }}
    ]
}}""",
        requires_json=True,
        temperature=0.9
    )
    
    # Stage 2: Discriminative Refinement
    DISCRIMINATIVE_REFINEMENT = PromptTemplate(
        name="discriminative_refinement",
        system="""You are a story editor with a critical eye for narrative quality.
Evaluate story concepts for authenticity, coherence, and dramatic effectiveness.""",
        user="""## Discriminative Refinement

Acting as a story editor, evaluate these concepts:
{concepts}

Previous scene context:
{previous_scene}

Evaluation criteria:
1. Character authenticity (do actions match established personalities?)
2. Narrative coherence (does it flow from previous events?)
3. Dramatic effectiveness (tension, pacing, engagement)
4. Thematic resonance (connection to episode themes)
5. Production feasibility (can this be rendered?)

Select the best concept and refine it.

Output as JSON:
{{
    "selected_concept_id": "concept_X",
    "evaluation_scores": {{
        "authenticity": 0.0-1.0,
        "coherence": 0.0-1.0,
        "drama": 0.0-1.0,
        "theme": 0.0-1.0,
        "feasibility": 0.0-1.0
    }},
    "refinements": {{
        "enhanced_motivations": "Deeper character reasons",
        "clarified_conflict": "Specific tension points",
        "added_details": ["detail1", "detail2"],
        "potential_issues": ["issue1", "issue2"]
    }},
    "refined_concept": {{
        "scene_description": "Full scene outline",
        "character_objectives": {{"character": "objective"}},
        "turning_points": ["point1", "point2"],
        "emotional_arc": "start → middle → end"
    }}
}}""",
        requires_json=True,
        temperature=0.3
    )
    
    # Stage 3: Dramatic Enhancement
    DRAMATIC_ENHANCEMENT = PromptTemplate(
        name="dramatic_enhancement",
        system="""You are a master of dramatic storytelling techniques.
Apply dramatic operators to enhance scenes while maintaining organic storytelling.""",
        user="""## Dramatic Enhancement

Current scene concept:
{refined_concept}

Episode context:
- Current act: {act_number}
- Plot threads: {plot_threads}
- Foreshadowed elements: {foreshadowing}

Available dramatic operators:
- Reversal: Subvert expectations
- Foreshadowing: Plant seeds for future events
- Callback: Reference earlier moments
- Escalation: Raise stakes
- Irony: Create meaningful contrasts
- Parallel: Mirror other storylines
- Cliffhanger: Create suspense

Select and apply 2-3 dramatic operators that best serve this scene.

Output as JSON:
{{
    "selected_operators": [
        {{
            "type": "operator_name",
            "justification": "Why this works here",
            "implementation": "Specific application details",
            "impact": "Expected dramatic effect"
        }}
    ],
    "enhanced_scene": {{
        "description": "Scene with operators applied",
        "new_elements": ["element1", "element2"],
        "tension_curve": "How tension builds and releases",
        "hooks": ["hook for next scene"]
    }}
}}""",
        requires_json=True,
        temperature=0.7
    )
    
    # Stage 4: Dialogue Generation
    DIALOGUE_GENERATION = PromptTemplate(
        name="dialogue_generation",
        system="""You are a dialogue writer who creates authentic, character-driven conversations.
Each line should reveal character, advance plot, and contain subtext.""",
        user="""## Dialogue Generation

Scene: {scene_description}
Characters in scene: {characters}
Scene objective: {objective}
Emotional trajectory: {emotional_trajectory}

Character profiles:
{character_profiles}

Generate dialogue that:
1. Each character pursues their objective
2. Subtext differs from text
3. Conflict escalates naturally
4. Reveals character through speech patterns
5. Advances the plot

Output as JSON:
{{
    "dialogue": [
        {{
            "character": "name",
            "line": "what they say",
            "subtext": "what they really mean",
            "emotion": "emotional state",
            "action": "physical action or gesture"
        }}
    ],
    "turning_point": {{
        "line_index": number,
        "description": "what shifts"
    }},
    "scene_outcome": "how scene resolves"
}}""",
        requires_json=True,
        temperature=0.8
    )
    
    # Stage 5: Coherence Check
    COHERENCE_CHECK = PromptTemplate(
        name="coherence_check",
        system="""You are a continuity supervisor ensuring narrative consistency.
Check for plot holes, character inconsistencies, and world rule violations.""",
        user="""## Coherence Check

Enhanced scene:
{enhanced_scene}

Series bible:
- Established facts: {established_facts}
- Character relationships: {relationships}
- World rules: {world_rules}
- Ongoing plotlines: {plotlines}

Verify coherence:
1. Check for continuity errors
2. Ensure character consistency
3. Validate world rules aren't broken
4. Confirm plot threads align
5. Check dialogue authenticity

Output as JSON:
{{
    "coherence_report": {{
        "continuity": {{"status": "pass/fail", "issues": []}},
        "characters": {{"status": "pass/fail", "issues": []}},
        "world_rules": {{"status": "pass/fail", "issues": []}},
        "plot_alignment": {{"status": "pass/fail", "issues": []}}
    }},
    "required_corrections": [
        {{
            "issue": "description",
            "severity": "minor/major/critical",
            "suggested_fix": "how to fix"
        }}
    ],
    "final_check": "pass/fail"
}}""",
        requires_json=True,
        temperature=0.2
    )
    
    # Character voice calibration
    CHARACTER_VOICE = PromptTemplate(
        name="character_voice",
        system="""You are an expert in character voice and dialogue authenticity.
Create unique, consistent character voices based on personality and background.""",
        user="""## Character Voice Calibration

Character: {character_name}
Personality: {personality}
Background: {backstory}
Current emotional state: {emotional_state}
Relationship to other characters: {relationships}

Generate voice profile:

Output as JSON:
{{
    "voice_profile": {{
        "vocabulary": "simple/moderate/complex",
        "formality": "casual/balanced/formal",
        "speech_patterns": ["pattern1", "pattern2"],
        "catchphrases": ["phrase1", "phrase2"],
        "verbal_tics": ["tic1", "tic2"]
    }},
    "sample_lines": {{
        "greeting": "how they say hello",
        "angry": "how they express anger",
        "happy": "how they express joy",
        "nervous": "how they show nervousness"
    }}
}}""",
        requires_json=True,
        temperature=0.7
    )
    
    # Episode outline
    EPISODE_OUTLINE = PromptTemplate(
        name="episode_outline",
        system="""You are a showrunner creating compelling episode structures.
Design episode outlines that balance multiple storylines and maintain engagement.""",
        user="""## Episode Outline Generation

Episode concept:
- Title: {title}
- Synopsis: {synopsis}
- Themes: {themes}
- Genre: {genre}

Simulation data:
{simulation_summary}

Create a 14-scene episode outline following a {plot_pattern} pattern.

Requirements:
- Total runtime: ~22 minutes
- 3-4 storylines (A, B, C plots)
- Natural act breaks
- Satisfying conclusion

Output as JSON:
{{
    "episode": {{
        "title": "episode title",
        "logline": "one sentence summary",
        "acts": [
            {{
                "act_number": 1,
                "scenes": [
                    {{
                        "scene_number": 1,
                        "plot_line": "A/B/C",
                        "location": "where",
                        "characters": ["who"],
                        "summary": "what happens",
                        "duration_seconds": 90
                    }}
                ]
            }}
        ],
        "total_duration_seconds": 1320
    }}
}}""",
        requires_json=True,
        temperature=0.8
    )
    
    @classmethod
    def get_template(cls, name: str) -> PromptTemplate:
        """Get a prompt template by name.
        
        Args:
            name: Template name
            
        Returns:
            PromptTemplate object
            
        Raises:
            ValueError: If template not found
        """
        templates = {
            "concept_generation": cls.CONCEPT_GENERATION,
            "discriminative_refinement": cls.DISCRIMINATIVE_REFINEMENT,
            "dramatic_enhancement": cls.DRAMATIC_ENHANCEMENT,
            "dialogue_generation": cls.DIALOGUE_GENERATION,
            "coherence_check": cls.COHERENCE_CHECK,
            "character_voice": cls.CHARACTER_VOICE,
            "episode_outline": cls.EPISODE_OUTLINE,
        }
        
        if name not in templates:
            raise ValueError(f"Template '{name}' not found. Available: {list(templates.keys())}")
            
        return templates[name]
    
    @classmethod
    def list_templates(cls) -> List[str]:
        """Get list of available template names."""
        return [
            "concept_generation",
            "discriminative_refinement", 
            "dramatic_enhancement",
            "dialogue_generation",
            "coherence_check",
            "character_voice",
            "episode_outline"
        ]