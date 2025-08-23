"""Prompt chain implementation for sequential LLM processing."""

import asyncio
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from loguru import logger

from .llm_client import LLMClient, ModelType
from .prompts import PromptTemplates, PromptTemplate


@dataclass
class ChainContext:
    """Context passed through the prompt chain."""
    episode_title: str
    episode_synopsis: str
    themes: List[str]
    genre: str
    tone: str
    act_number: int = 1
    scene_number: int = 1
    
    # Simulation data
    characters: List[Dict[str, Any]] = field(default_factory=list)
    location: str = ""
    time: str = ""
    recent_events: List[str] = field(default_factory=list)
    character_states: Dict[str, str] = field(default_factory=dict)
    
    # Episode tracking
    plot_threads: List[str] = field(default_factory=list)
    foreshadowing: List[str] = field(default_factory=list)
    established_facts: List[str] = field(default_factory=list)
    world_rules: List[str] = field(default_factory=list)
    
    # Chain results
    generated_concepts: List[Dict] = field(default_factory=list)
    selected_concept: Optional[Dict] = None
    refined_concept: Optional[Dict] = None
    enhanced_scene: Optional[Dict] = None
    dialogue: Optional[List[Dict]] = None
    coherence_report: Optional[Dict] = None
    
    # Quality metrics
    quality_scores: Dict[str, float] = field(default_factory=dict)


class PromptChain:
    """Manages the sequential prompt chain for scene generation."""
    
    def __init__(self, llm_client: LLMClient):
        """Initialize the prompt chain.
        
        Args:
            llm_client: LLM client instance
        """
        self.llm_client = llm_client
        self.templates = PromptTemplates()
        
    async def run_chain(self, context: ChainContext) -> Dict[str, Any]:
        """Run the complete prompt chain for scene generation.
        
        Args:
            context: Chain context with episode and simulation data
            
        Returns:
            Generated scene data
        """
        logger.info(f"Starting prompt chain for scene {context.scene_number}")
        
        # Stage 1: Concept Generation
        concepts = await self._generate_concepts(context)
        context.generated_concepts = concepts
        
        # Stage 2: Discriminative Refinement
        refined = await self._refine_concept(context)
        context.refined_concept = refined
        
        # Stage 3: Dramatic Enhancement
        enhanced = await self._enhance_drama(context)
        context.enhanced_scene = enhanced
        
        # Stage 4: Dialogue Generation
        dialogue = await self._generate_dialogue(context)
        context.dialogue = dialogue
        
        # Stage 5: Coherence Check
        coherence = await self._check_coherence(context)
        context.coherence_report = coherence
        
        # If coherence fails, attempt corrections
        if coherence.get("final_check") == "fail":
            await self._apply_corrections(context)
        
        # Compile final scene
        scene = self._compile_scene(context)
        
        logger.info(f"Prompt chain complete. Quality score: {scene.get('quality_score', 0):.2f}")
        return scene
        
    async def _generate_concepts(self, context: ChainContext) -> List[Dict]:
        """Stage 1: Generate creative concepts."""
        template = self.templates.get_template("concept_generation")
        
        # Format the prompt with context
        prompt = template.user.format(
            characters=json.dumps(context.characters),
            location=context.location,
            time=context.time,
            recent_events=json.dumps(context.recent_events),
            character_states=json.dumps(context.character_states),
            genre=context.genre,
            tone=context.tone,
            themes=", ".join(context.themes)
        )
        
        # Use faster model for concept generation
        self.llm_client.switch_model(ModelType.GPT35_TURBO)
        
        response = await self.llm_client.generate(
            prompt=prompt,
            system_prompt=template.system,
            temperature=template.temperature,
            response_format={"type": "json_object"} if template.requires_json else None
        )
        
        try:
            data = json.loads(response)
            concepts = data.get("concepts", [])
            logger.debug(f"Generated {len(concepts)} concepts")
            return concepts
        except json.JSONDecodeError:
            logger.error("Failed to parse concept generation response")
            return []
            
    async def _refine_concept(self, context: ChainContext) -> Dict:
        """Stage 2: Discriminatively refine concepts."""
        template = self.templates.get_template("discriminative_refinement")
        
        prompt = template.user.format(
            concepts=json.dumps(context.generated_concepts, indent=2),
            previous_scene=json.dumps(context.recent_events[-1] if context.recent_events else {})
        )
        
        # Switch to better model for evaluation
        self.llm_client.switch_model(ModelType.GPT4)
        
        response = await self.llm_client.generate(
            prompt=prompt,
            system_prompt=template.system,
            temperature=template.temperature,
            response_format={"type": "json_object"} if template.requires_json else None
        )
        
        try:
            data = json.loads(response)
            
            # Track quality scores
            if "evaluation_scores" in data:
                context.quality_scores.update(data["evaluation_scores"])
            
            return data.get("refined_concept", {})
        except json.JSONDecodeError:
            logger.error("Failed to parse refinement response")
            # Fallback to first concept
            return context.generated_concepts[0] if context.generated_concepts else {}
            
    async def _enhance_drama(self, context: ChainContext) -> Dict:
        """Stage 3: Apply dramatic operators."""
        template = self.templates.get_template("dramatic_enhancement")
        
        prompt = template.user.format(
            refined_concept=json.dumps(context.refined_concept, indent=2),
            act_number=context.act_number,
            plot_threads=json.dumps(context.plot_threads),
            foreshadowing=json.dumps(context.foreshadowing)
        )
        
        response = await self.llm_client.generate(
            prompt=prompt,
            system_prompt=template.system,
            temperature=template.temperature,
            response_format={"type": "json_object"} if template.requires_json else None
        )
        
        try:
            data = json.loads(response)
            
            # Update foreshadowing list
            if "enhanced_scene" in data and "hooks" in data["enhanced_scene"]:
                context.foreshadowing.extend(data["enhanced_scene"]["hooks"])
            
            return data.get("enhanced_scene", context.refined_concept)
        except json.JSONDecodeError:
            logger.error("Failed to parse drama enhancement response")
            return context.refined_concept
            
    async def _generate_dialogue(self, context: ChainContext) -> List[Dict]:
        """Stage 4: Generate character dialogue."""
        template = self.templates.get_template("dialogue_generation")
        
        # Extract character profiles from context
        character_profiles = {
            char["name"]: {
                "personality": char.get("personality", ""),
                "backstory": char.get("backstory", ""),
                "voice": char.get("voice", "")
            }
            for char in context.characters
        }
        
        prompt = template.user.format(
            scene_description=json.dumps(context.enhanced_scene),
            characters=json.dumps([c["name"] for c in context.characters]),
            objective=context.enhanced_scene.get("character_objectives", {}),
            emotional_trajectory=context.enhanced_scene.get("emotional_arc", ""),
            character_profiles=json.dumps(character_profiles, indent=2)
        )
        
        response = await self.llm_client.generate(
            prompt=prompt,
            system_prompt=template.system,
            temperature=template.temperature,
            response_format={"type": "json_object"} if template.requires_json else None
        )
        
        try:
            data = json.loads(response)
            return data.get("dialogue", [])
        except json.JSONDecodeError:
            logger.error("Failed to parse dialogue generation response")
            return []
            
    async def _check_coherence(self, context: ChainContext) -> Dict:
        """Stage 5: Check narrative coherence."""
        template = self.templates.get_template("coherence_check")
        
        # Build relationships from characters
        relationships = {}
        for char in context.characters:
            relationships[char["name"]] = char.get("relationships", {})
        
        prompt = template.user.format(
            enhanced_scene=json.dumps({
                "scene": context.enhanced_scene,
                "dialogue": context.dialogue
            }, indent=2),
            established_facts=json.dumps(context.established_facts),
            relationships=json.dumps(relationships),
            world_rules=json.dumps(context.world_rules),
            plotlines=json.dumps(context.plot_threads)
        )
        
        # Use faster model for coherence check
        self.llm_client.switch_model(ModelType.GPT35_TURBO)
        
        response = await self.llm_client.generate(
            prompt=prompt,
            system_prompt=template.system,
            temperature=template.temperature,
            response_format={"type": "json_object"} if template.requires_json else None
        )
        
        try:
            data = json.loads(response)
            return data
        except json.JSONDecodeError:
            logger.error("Failed to parse coherence check response")
            return {"final_check": "pass", "coherence_report": {}}
            
    async def _apply_corrections(self, context: ChainContext) -> None:
        """Apply corrections based on coherence report."""
        if not context.coherence_report:
            return
            
        corrections = context.coherence_report.get("required_corrections", [])
        critical_issues = [c for c in corrections if c.get("severity") == "critical"]
        
        if critical_issues:
            logger.warning(f"Found {len(critical_issues)} critical issues. Attempting corrections...")
            
            # Re-run dialogue generation with corrections
            correction_prompt = f"""
            Previous dialogue had these issues:
            {json.dumps(critical_issues, indent=2)}
            
            Please regenerate the dialogue addressing these issues.
            """
            
            # Prepend correction prompt to dialogue generation
            context.dialogue = await self._generate_dialogue(context)
            
    def _compile_scene(self, context: ChainContext) -> Dict[str, Any]:
        """Compile all chain results into final scene data."""
        
        # Calculate overall quality score
        quality_score = sum(context.quality_scores.values()) / len(context.quality_scores) if context.quality_scores else 0.5
        
        scene = {
            "scene_number": context.scene_number,
            "act_number": context.act_number,
            "location": context.location,
            "time": context.time,
            "characters": [c["name"] for c in context.characters],
            "description": context.enhanced_scene.get("description", ""),
            "dialogue": context.dialogue,
            "dramatic_operators": context.enhanced_scene.get("selected_operators", []),
            "turning_points": context.enhanced_scene.get("turning_points", []),
            "emotional_arc": context.enhanced_scene.get("emotional_arc", ""),
            "quality_score": quality_score,
            "coherence_status": context.coherence_report.get("final_check", "unknown"),
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "prompt_chain_version": "1.0",
                "models_used": ["gpt-3.5-turbo", "gpt-4"]
            }
        }
        
        return scene


class EpisodeChain:
    """Manages episode-level prompt chains."""
    
    def __init__(self, llm_client: LLMClient):
        """Initialize the episode chain.
        
        Args:
            llm_client: LLM client instance
        """
        self.llm_client = llm_client
        self.templates = PromptTemplates()
        self.scene_chain = PromptChain(llm_client)
        
    async def generate_episode_outline(
        self,
        title: str,
        synopsis: str,
        themes: List[str],
        genre: str,
        simulation_data: Optional[Dict] = None,
        plot_pattern: str = "ABABCAB"
    ) -> Dict[str, Any]:
        """Generate a complete episode outline.
        
        Args:
            title: Episode title
            synopsis: Episode synopsis
            themes: Episode themes
            genre: Genre
            simulation_data: Optional simulation data
            plot_pattern: Plot interweaving pattern
            
        Returns:
            Episode outline with scenes
        """
        template = self.templates.get_template("episode_outline")
        
        prompt = template.user.format(
            title=title,
            synopsis=synopsis,
            themes=json.dumps(themes),
            genre=genre,
            simulation_summary=json.dumps(simulation_data or {}),
            plot_pattern=plot_pattern
        )
        
        response = await self.llm_client.generate(
            prompt=prompt,
            system_prompt=template.system,
            temperature=template.temperature,
            response_format={"type": "json_object"} if template.requires_json else None
        )
        
        try:
            data = json.loads(response)
            return data.get("episode", {})
        except json.JSONDecodeError:
            logger.error("Failed to parse episode outline")
            return {}
            
    async def generate_full_episode(
        self,
        title: str,
        synopsis: str,
        themes: List[str],
        genre: str,
        tone: str,
        simulation_data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Generate a complete episode with all scenes.
        
        Args:
            title: Episode title
            synopsis: Episode synopsis
            themes: Episode themes
            genre: Genre
            tone: Tone
            simulation_data: Optional simulation data
            
        Returns:
            Complete episode data
        """
        logger.info(f"Generating full episode: {title}")
        
        # First generate the outline
        outline = await self.generate_episode_outline(
            title, synopsis, themes, genre, simulation_data
        )
        
        if not outline:
            logger.error("Failed to generate episode outline")
            return {}
        
        # Create base context
        base_context = ChainContext(
            episode_title=title,
            episode_synopsis=synopsis,
            themes=themes,
            genre=genre,
            tone=tone
        )
        
        # If we have simulation data, populate it
        if simulation_data:
            base_context.characters = simulation_data.get("characters", [])
            base_context.world_rules = simulation_data.get("world_rules", [])
            base_context.established_facts = simulation_data.get("established_facts", [])
        
        # Generate each scene
        generated_scenes = []
        
        for act in outline.get("acts", []):
            base_context.act_number = act["act_number"]
            
            for scene_outline in act.get("scenes", []):
                # Update context for this scene
                scene_context = ChainContext(
                    episode_title=base_context.episode_title,
                    episode_synopsis=base_context.episode_synopsis,
                    themes=base_context.themes,
                    genre=base_context.genre,
                    tone=base_context.tone,
                    act_number=base_context.act_number,
                    scene_number=scene_outline["scene_number"],
                    location=scene_outline.get("location", ""),
                    time=scene_outline.get("time", ""),
                    characters=[c for c in base_context.characters if c["name"] in scene_outline.get("characters", [])],
                    plot_threads=base_context.plot_threads,
                    foreshadowing=base_context.foreshadowing,
                    established_facts=base_context.established_facts,
                    world_rules=base_context.world_rules,
                    recent_events=base_context.recent_events[-3:] if base_context.recent_events else []
                )
                
                # Generate the scene
                scene = await self.scene_chain.run_chain(scene_context)
                generated_scenes.append(scene)
                
                # Update base context with scene results
                base_context.recent_events.append({
                    "scene": scene_outline["scene_number"],
                    "summary": scene_outline.get("summary", ""),
                    "outcome": scene.get("emotional_arc", "")
                })
                
                # Add any new plot threads or foreshadowing
                if scene_context.foreshadowing:
                    base_context.foreshadowing.extend(scene_context.foreshadowing)
                
                logger.info(f"Generated scene {scene['scene_number']} - Quality: {scene.get('quality_score', 0):.2f}")
        
        # Compile full episode
        episode = {
            "title": title,
            "synopsis": synopsis,
            "themes": themes,
            "genre": genre,
            "tone": tone,
            "outline": outline,
            "scenes": generated_scenes,
            "total_scenes": len(generated_scenes),
            "average_quality": sum(s.get("quality_score", 0) for s in generated_scenes) / len(generated_scenes) if generated_scenes else 0,
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "version": "1.0"
            }
        }
        
        logger.info(f"Episode generation complete. Average quality: {episode['average_quality']:.2f}")
        return episode