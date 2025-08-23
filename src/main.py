#!/usr/bin/env python3
"""Main entry point for Showrunner Agents episode generation."""

import asyncio
import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from loguru import logger

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    logger.warning("python-dotenv not installed. Using system environment variables only.")

from src.agents import CharacterAgent
from src.simulation import SimulationEngine
from src.llm import LLMClient, ModelType
from src.llm.prompt_chain import EpisodeChain, ChainContext
from src.drama import DramaEngine


class ShowrunnerSystem:
    """Main system orchestrator for episode generation."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the Showrunner system.
        
        Args:
            config_path: Path to configuration file
        """
        self.config = self._load_config(config_path)
        self.llm_client = None
        self.simulation_engine = None
        self.drama_engine = DramaEngine()
        self.episode_chain = None
        
        # Initialize components
        self._initialize_components()
        
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load system configuration."""
        default_config = {
            "simulation": {
                "time_step_minutes": 15,
                "default_duration_hours": 3,
                "max_agents": 10
            },
            "generation": {
                "llm_model": "gpt-4",
                "temperature": 0.8,
                "max_scenes": 14,
                "scene_duration_seconds": 90
            },
            "dramatic_operators": {
                "max_per_scene": 3,
                "min_tension": 0.3,
                "max_tension": 0.9
            },
            "output": {
                "format": "json",
                "include_metadata": True,
                "save_intermediate": True
            }
        }
        
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                user_config = json.load(f)
                # Merge with defaults
                for key in user_config:
                    if key in default_config:
                        default_config[key].update(user_config[key])
                    else:
                        default_config[key] = user_config[key]
                        
        return default_config
        
    def _initialize_components(self):
        """Initialize system components."""
        # Initialize LLM client
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.warning("OPENAI_API_KEY not set. LLM features will be limited.")
        else:
            model_name = self.config["generation"]["llm_model"]
            # Use GPT-4.1 by default for maximum capability
            if "gpt-4.1" in model_name:
                model = ModelType.GPT4_1
            elif "gpt-4" in model_name:
                model = ModelType.GPT4
            else:
                model = ModelType.GPT35_TURBO
            self.llm_client = LLMClient(api_key=api_key, model=model)
            self.episode_chain = EpisodeChain(self.llm_client)
            
        # Initialize simulation engine
        self.simulation_engine = SimulationEngine(
            time_step_minutes=self.config["simulation"]["time_step_minutes"]
        )
        
        logger.info("Showrunner system initialized")
        
    def create_characters_from_config(self, characters_config: list) -> list:
        """Create character agents from configuration.
        
        Args:
            characters_config: List of character configurations
            
        Returns:
            List of CharacterAgent instances
        """
        characters = []
        
        for char_config in characters_config:
            agent = CharacterAgent(
                name=char_config["name"],
                backstory=char_config.get("backstory", ""),
                personality=char_config.get("personality", {
                    "openness": 0.5,
                    "conscientiousness": 0.5,
                    "extraversion": 0.5,
                    "agreeableness": 0.5,
                    "neuroticism": 0.5
                }),
                age=char_config.get("age"),
                occupation=char_config.get("occupation")
            )
            characters.append(agent)
            
        return characters
        
    async def generate_episode(
        self,
        title: str,
        synopsis: str,
        themes: list,
        genre: str = "drama",
        tone: str = "balanced",
        characters: Optional[list] = None,
        simulation_hours: float = 3.0,
        plot_pattern: str = "ABABCAB"
    ) -> Dict[str, Any]:
        """Generate a complete episode.
        
        Args:
            title: Episode title
            synopsis: Episode synopsis
            themes: List of themes
            genre: Genre
            tone: Tone
            characters: Optional list of character configs
            simulation_hours: Hours to simulate
            plot_pattern: Plot interweaving pattern
            
        Returns:
            Complete episode data
        """
        logger.info(f"Generating episode: {title}")
        episode_start = datetime.now()
        
        # Step 1: Run simulation if characters provided
        simulation_data = None
        if characters:
            logger.info("Step 1: Running agent simulation...")
            simulation_data = await self._run_simulation(characters, simulation_hours)
            
            if self.config["output"]["save_intermediate"]:
                self._save_intermediate(simulation_data, "simulation_data.json")
                
        # Step 2: Generate episode with LLM chain
        if self.episode_chain:
            logger.info("Step 2: Generating episode structure...")
            episode = await self.episode_chain.generate_full_episode(
                title=title,
                synopsis=synopsis,
                themes=themes,
                genre=genre,
                tone=tone,
                simulation_data=simulation_data
            )
            
            # Step 3: Apply dramatic enhancements
            logger.info("Step 3: Applying dramatic enhancements...")
            if episode.get("scenes"):
                enhanced_scenes = []
                for scene in episode["scenes"]:
                    enhanced = self.drama_engine.enhance_scene(
                        scene,
                        max_operators=self.config["dramatic_operators"]["max_per_scene"]
                    )
                    enhanced_scenes.append(enhanced)
                episode["scenes"] = enhanced_scenes
                
                # Analyze dramatic arc
                arc_analysis = self.drama_engine.analyze_dramatic_arc(enhanced_scenes)
                episode["dramatic_arc"] = arc_analysis
                
        else:
            # Fallback: Create basic episode structure without LLM
            logger.warning("LLM not available. Creating basic episode structure.")
            episode = self._create_basic_episode(
                title, synopsis, themes, genre, tone, simulation_data
            )
            
        # Add metadata
        episode["metadata"] = {
            "generated_at": datetime.now().isoformat(),
            "generation_time_seconds": (datetime.now() - episode_start).total_seconds(),
            "system_version": "1.0.0",
            "config": self.config
        }
        
        logger.info(f"Episode generation complete in {episode['metadata']['generation_time_seconds']:.1f} seconds")
        return episode
        
    async def _run_simulation(
        self,
        characters_config: list,
        duration_hours: float
    ) -> Dict[str, Any]:
        """Run agent simulation.
        
        Args:
            characters_config: Character configurations
            duration_hours: Simulation duration
            
        Returns:
            Simulation data
        """
        # Create character agents
        agents = self.create_characters_from_config(characters_config)
        
        # Add agents to simulation
        for agent in agents:
            self.simulation_engine.add_agent(agent)
            
        # Run simulation
        results = await self.simulation_engine.run_simulation(
            duration_hours=duration_hours
        )
        
        # Extract relevant data for episode generation
        simulation_data = {
            "characters": [agent.to_dict() for agent in agents],
            "events": results.get("events", []),
            "dramatic_peaks": results.get("dramatic_peaks", []),
            "narrative_arc": results.get("narrative_arc", []),
            "agent_trajectories": results.get("agent_trajectories", {}),
            "world_rules": self.simulation_engine.world_config.get("global_rules", []),
            "established_facts": self._extract_facts_from_events(results.get("events", []))
        }
        
        return simulation_data
        
    def _extract_facts_from_events(self, events: list) -> list:
        """Extract established facts from simulation events."""
        facts = []
        
        for event in events[:20]:  # First 20 events establish facts
            if event.get("type") == "interaction":
                facts.append(f"{event.get('description', '')}")
            elif event.get("type") == "revelation":
                facts.append(f"It was revealed that {event.get('description', '')}")
                
        return facts[:10]  # Limit to 10 facts
        
    def _create_basic_episode(
        self,
        title: str,
        synopsis: str,
        themes: list,
        genre: str,
        tone: str,
        simulation_data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Create a basic episode structure without LLM."""
        scenes = []
        
        # Create 14 basic scenes
        for i in range(14):
            act = 1 if i < 5 else (2 if i < 10 else 3)
            plot_line = "A" if i % 2 == 0 else "B"
            
            scene = {
                "scene_number": i + 1,
                "act_number": act,
                "plot_line": plot_line,
                "location": f"Location_{i + 1}",
                "duration_seconds": 90,
                "description": f"Scene {i + 1} of the episode",
                "dialogue": [],
                "tension": 0.3 + (i / 14) * 0.4  # Rising tension
            }
            
            # Apply drama enhancement
            enhanced = self.drama_engine.enhance_scene(scene)
            scenes.append(enhanced)
            
        return {
            "title": title,
            "synopsis": synopsis,
            "themes": themes,
            "genre": genre,
            "tone": tone,
            "scenes": scenes,
            "total_scenes": len(scenes),
            "simulation_data": simulation_data
        }
        
    def _save_intermediate(self, data: Dict[str, Any], filename: str):
        """Save intermediate data to file."""
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        
        filepath = output_dir / filename
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
            
        logger.debug(f"Saved intermediate data to {filepath}")
        
    async def close(self):
        """Clean up resources."""
        if self.llm_client:
            await self.llm_client.close()


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate TV episodes using Showrunner Agents system"
    )
    
    # Required arguments
    parser.add_argument(
        "--title",
        required=True,
        help="Episode title"
    )
    parser.add_argument(
        "--synopsis",
        required=True,
        help="Episode synopsis"
    )
    
    # Optional arguments
    parser.add_argument(
        "--themes",
        nargs="+",
        default=["drama", "conflict", "resolution"],
        help="Episode themes"
    )
    parser.add_argument(
        "--genre",
        default="drama",
        choices=["drama", "comedy", "thriller", "sci-fi", "mystery"],
        help="Episode genre"
    )
    parser.add_argument(
        "--tone",
        default="balanced",
        choices=["light", "balanced", "dark", "tense", "comedic"],
        help="Episode tone"
    )
    parser.add_argument(
        "--simulation-hours",
        type=float,
        default=3.0,
        help="Hours to simulate"
    )
    parser.add_argument(
        "--characters-file",
        help="JSON file with character definitions"
    )
    parser.add_argument(
        "--config",
        help="Path to configuration file"
    )
    parser.add_argument(
        "--output",
        default="episode_output.json",
        help="Output file path"
    )
    parser.add_argument(
        "--plot-pattern",
        default="ABABCAB",
        help="Plot interweaving pattern"
    )
    
    args = parser.parse_args()
    
    # Configure logging
    logger.add("showrunner.log", rotation="10 MB")
    
    # Load characters if provided
    characters = None
    if args.characters_file:
        with open(args.characters_file, 'r') as f:
            characters = json.load(f)
    else:
        # Use default test characters
        characters = [
            {
                "name": "Alex Chen",
                "backstory": "Brilliant but conflicted tech founder",
                "personality": {
                    "openness": 0.9,
                    "conscientiousness": 0.7,
                    "extraversion": 0.6,
                    "agreeableness": 0.5,
                    "neuroticism": 0.6
                },
                "age": 32,
                "occupation": "CEO"
            },
            {
                "name": "Jordan Kim",
                "backstory": "Ethical AI researcher with strong principles",
                "personality": {
                    "openness": 0.8,
                    "conscientiousness": 0.9,
                    "extraversion": 0.4,
                    "agreeableness": 0.8,
                    "neuroticism": 0.5
                },
                "age": 29,
                "occupation": "Head of Ethics"
            },
            {
                "name": "Sam Rodriguez",
                "backstory": "Ambitious product manager focused on growth",
                "personality": {
                    "openness": 0.6,
                    "conscientiousness": 0.8,
                    "extraversion": 0.8,
                    "agreeableness": 0.6,
                    "neuroticism": 0.4
                },
                "age": 27,
                "occupation": "Product Manager"
            }
        ]
    
    # Initialize system
    system = ShowrunnerSystem(config_path=args.config)
    
    try:
        # Generate episode
        episode = await system.generate_episode(
            title=args.title,
            synopsis=args.synopsis,
            themes=args.themes,
            genre=args.genre,
            tone=args.tone,
            characters=characters,
            simulation_hours=args.simulation_hours,
            plot_pattern=args.plot_pattern
        )
        
        # Save output
        with open(args.output, 'w') as f:
            json.dump(episode, f, indent=2)
            
        logger.info(f"Episode saved to {args.output}")
        
        # Print summary
        print("\n" + "="*50)
        print("EPISODE GENERATION COMPLETE")
        print("="*50)
        print(f"Title: {episode.get('title')}")
        print(f"Genre: {episode.get('genre')}")
        print(f"Total Scenes: {episode.get('total_scenes', 0)}")
        
        if episode.get("dramatic_arc"):
            arc = episode["dramatic_arc"]
            print(f"\nDramatic Arc:")
            print(f"  Average Tension: {arc.get('average_tension', 0):.2f}")
            print(f"  Number of Peaks: {arc.get('num_peaks', 0)}")
            print(f"  Has Rising Action: {arc.get('has_rising_action', False)}")
            print(f"  Has Climax: {arc.get('has_climax', False)}")
            
        if episode.get("scenes"):
            print(f"\nFirst Scene:")
            first_scene = episode["scenes"][0]
            print(f"  Location: {first_scene.get('location', 'Unknown')}")
            print(f"  Description: {first_scene.get('description', 'No description')[:100]}...")
            
        print(f"\nGeneration Time: {episode.get('metadata', {}).get('generation_time_seconds', 0):.1f} seconds")
        print(f"Output saved to: {args.output}")
        
    finally:
        await system.close()


if __name__ == "__main__":
    asyncio.run(main())