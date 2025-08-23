#!/usr/bin/env python3
"""
Example: Full Showrunner Pipeline with Mock Simulation Data

This example demonstrates the complete Showrunner pipeline:
1. Generate mock simulation data (skipping actual agent simulation)
2. Process through LLM EpisodeChain
3. Apply DramaEngine enhancements and arc analysis

This gives you the full system benefits without the computational cost of simulation.
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import random

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Import Showrunner components
from src.llm import LLMClient, ModelType
from src.llm.prompt_chain import EpisodeChain
from src.drama import DramaEngine


class MockSimulationGenerator:
    """Generate realistic simulation data without running actual simulation"""
    
    def __init__(self):
        self.characters = self._create_default_characters()
        
    def _create_default_characters(self) -> List[Dict]:
        """Create default character profiles"""
        return [
            {
                "name": "Alex Chen",
                "id": "alex_001",
                "backstory": "Brilliant but ethically conflicted AI researcher who left academia to start a company. Struggles with balancing innovation and responsibility.",
                "personality": {
                    "openness": 0.9,
                    "conscientiousness": 0.7,
                    "extraversion": 0.6,
                    "agreeableness": 0.5,
                    "neuroticism": 0.6
                },
                "age": 32,
                "occupation": "CEO/Founder",
                "goals": ["Launch groundbreaking AI", "Maintain ethical standards"],
                "fears": ["Losing control of the technology", "Betrayal by partners"],
                "relationships": {
                    "sam_001": {"type": "mentor", "strength": 0.8},
                    "jordan_001": {"type": "rival", "strength": -0.6}
                }
            },
            {
                "name": "Sam Rodriguez",
                "id": "sam_001",
                "backstory": "Veteran tech executive who has seen the rise and fall of many startups. Acts as a mentor but harbors regrets about past compromises.",
                "personality": {
                    "openness": 0.7,
                    "conscientiousness": 0.9,
                    "extraversion": 0.4,
                    "agreeableness": 0.8,
                    "neuroticism": 0.5
                },
                "age": 48,
                "occupation": "Board Advisor",
                "goals": ["Guide the next generation", "Redeem past mistakes"],
                "fears": ["Repeating history", "Being irrelevant"],
                "relationships": {
                    "alex_001": {"type": "mentee", "strength": 0.8},
                    "jordan_001": {"type": "cautious", "strength": -0.3}
                }
            },
            {
                "name": "Jordan Park",
                "id": "jordan_001",
                "backstory": "Ambitious competitor who believes the end justifies the means. Former colleague of Alex who now runs a rival company.",
                "personality": {
                    "openness": 0.6,
                    "conscientiousness": 0.8,
                    "extraversion": 0.8,
                    "agreeableness": 0.3,
                    "neuroticism": 0.4
                },
                "age": 35,
                "occupation": "Rival CEO",
                "goals": ["Dominate the market", "Prove superiority over Alex"],
                "fears": ["Being second best", "Exposure of methods"],
                "relationships": {
                    "alex_001": {"type": "rival", "strength": -0.6},
                    "sam_001": {"type": "adversary", "strength": -0.3}
                }
            }
        ]
    
    def generate_simulation_data(self, 
                                theme: str = "ethics vs ambition",
                                duration_hours: float = 3.0) -> Dict[str, Any]:
        """
        Generate mock simulation data that mimics what would come from agent simulation
        
        Returns:
            Dictionary containing all simulation data needed for episode generation
        """
        
        # Generate timeline of events
        events = self._generate_events(duration_hours)
        
        # Identify dramatic peaks from events
        dramatic_peaks = self._identify_dramatic_peaks(events)
        
        # Generate character trajectories
        agent_trajectories = self._generate_trajectories(events)
        
        # Extract narrative arc
        narrative_arc = self._extract_narrative_arc(events, dramatic_peaks)
        
        # Establish world facts from early events
        established_facts = self._establish_facts(events[:10])
        
        # Compile complete simulation data
        simulation_data = {
            "metadata": {
                "duration_hours": duration_hours,
                "time_steps": int(duration_hours * 4),  # 15-minute intervals
                "theme": theme,
                "generated_at": datetime.now().isoformat()
            },
            "characters": self.characters,
            "events": events,
            "dramatic_peaks": dramatic_peaks,
            "narrative_arc": narrative_arc,
            "agent_trajectories": agent_trajectories,
            "world_rules": [
                "Technology shapes moral choices",
                "Past actions have present consequences",
                "Trust once broken is hard to rebuild",
                "Innovation requires sacrifice",
                "Success comes at a personal cost"
            ],
            "established_facts": established_facts,
            "emergent_themes": [
                "The price of ambition",
                "Loyalty versus opportunity",
                "The weight of mentorship",
                "Ethics in innovation"
            ],
            "relationship_dynamics": self._generate_relationship_dynamics()
        }
        
        return simulation_data
    
    def _generate_events(self, duration_hours: float) -> List[Dict]:
        """Generate a sequence of simulated events"""
        events = []
        time_steps = int(duration_hours * 4)  # 15-minute intervals
        
        # Event templates based on typical dramatic progression
        event_templates = [
            # Early establishment
            {"type": "discovery", "tension": 0.3, "description": "Alex discovers a breakthrough in the AI algorithm"},
            {"type": "meeting", "tension": 0.2, "description": "Team meeting reveals differing visions"},
            {"type": "revelation", "tension": 0.4, "description": "Sam shares a cautionary tale from the past"},
            
            # Rising tension
            {"type": "conflict", "tension": 0.5, "description": "Jordan makes a competitive move"},
            {"type": "dilemma", "tension": 0.6, "description": "Alex faces pressure to compromise ethics"},
            {"type": "confrontation", "tension": 0.7, "description": "Sam confronts Alex about dangerous choices"},
            
            # Peak moments
            {"type": "betrayal", "tension": 0.8, "description": "Jordan attempts to poach key team members"},
            {"type": "crisis", "tension": 0.9, "description": "The algorithm shows unintended consequences"},
            {"type": "ultimatum", "tension": 0.85, "description": "Investors demand immediate deployment"},
            
            # Resolution attempts
            {"type": "reconciliation", "tension": 0.6, "description": "Alex seeks Sam's guidance"},
            {"type": "decision", "tension": 0.7, "description": "Alex makes a crucial choice"},
            {"type": "consequence", "tension": 0.5, "description": "The impact of choices becomes clear"}
        ]
        
        # Generate events with timestamps
        for i in range(min(time_steps, len(event_templates) * 2)):
            template = event_templates[i % len(event_templates)]
            
            # Add variation to the template
            event = {
                "timestamp": i * 15,  # minutes
                "type": template["type"],
                "description": template["description"],
                "tension_level": template["tension"] + random.uniform(-0.1, 0.1),
                "participants": self._select_participants(template["type"]),
                "location": self._select_location(i),
                "emotional_valence": random.uniform(-1, 1),
                "plot_relevance": random.uniform(0.5, 1.0)
            }
            
            # Add specific details based on event type
            if event["type"] == "conflict":
                event["conflict_type"] = random.choice(["ideological", "personal", "professional"])
            elif event["type"] == "revelation":
                event["revelation_impact"] = random.choice(["changes everything", "confirms suspicions", "opens new path"])
            
            events.append(event)
        
        return events
    
    def _identify_dramatic_peaks(self, events: List[Dict]) -> List[Dict]:
        """Identify dramatic peaks from events"""
        peaks = []
        
        for i, event in enumerate(events):
            if event["tension_level"] > 0.7:
                peak = {
                    "event_index": i,
                    "timestamp": event["timestamp"],
                    "type": event["type"],
                    "tension": event["tension_level"],
                    "description": f"Dramatic peak: {event['description']}",
                    "participants": event["participants"],
                    "narrative_impact": "high" if event["tension_level"] > 0.8 else "medium"
                }
                peaks.append(peak)
        
        return peaks
    
    def _generate_trajectories(self, events: List[Dict]) -> Dict[str, List]:
        """Generate character trajectories through the simulation"""
        trajectories = {}
        
        for char in self.characters:
            char_events = [e for e in events if char["id"] in e.get("participants", [])]
            
            trajectory = {
                "character_id": char["id"],
                "character_name": char["name"],
                "emotional_arc": self._generate_emotional_arc(char_events),
                "relationship_changes": self._track_relationship_changes(char, events),
                "key_decisions": self._extract_key_decisions(char, char_events),
                "growth_moments": self._identify_growth_moments(char, char_events)
            }
            
            trajectories[char["id"]] = trajectory
        
        return trajectories
    
    def _generate_emotional_arc(self, events: List[Dict]) -> List[Dict]:
        """Generate emotional arc for a character"""
        arc = []
        current_emotion = 0.5  # Neutral start
        
        for event in events:
            # Emotional impact based on event type
            if event["type"] in ["conflict", "betrayal", "crisis"]:
                current_emotion -= random.uniform(0.1, 0.3)
            elif event["type"] in ["reconciliation", "discovery"]:
                current_emotion += random.uniform(0.1, 0.2)
            
            # Keep within bounds
            current_emotion = max(0, min(1, current_emotion))
            
            arc.append({
                "timestamp": event["timestamp"],
                "emotional_state": current_emotion,
                "trigger": event["type"]
            })
        
        return arc
    
    def _track_relationship_changes(self, character: Dict, events: List[Dict]) -> List[Dict]:
        """Track how relationships change over time"""
        changes = []
        
        for other_char in self.characters:
            if other_char["id"] != character["id"]:
                # Simulate relationship evolution
                change = {
                    "with": other_char["name"],
                    "start": character["relationships"].get(other_char["id"], {}).get("strength", 0),
                    "end": character["relationships"].get(other_char["id"], {}).get("strength", 0) + random.uniform(-0.3, 0.3),
                    "key_moment": random.choice(events)["description"] if events else "No significant moment"
                }
                changes.append(change)
        
        return changes
    
    def _extract_key_decisions(self, character: Dict, events: List[Dict]) -> List[Dict]:
        """Extract key decisions made by character"""
        decisions = []
        
        decision_events = [e for e in events if e["type"] in ["decision", "dilemma", "ultimatum"]]
        
        for event in decision_events[:3]:  # Limit to 3 key decisions
            decision = {
                "timestamp": event["timestamp"],
                "description": f"{character['name']} decides on {event['description']}",
                "stakes": "high" if event["tension_level"] > 0.7 else "medium",
                "outcome": random.choice(["success", "mixed", "failure"])
            }
            decisions.append(decision)
        
        return decisions
    
    def _identify_growth_moments(self, character: Dict, events: List[Dict]) -> List[str]:
        """Identify character growth moments"""
        growth_moments = []
        
        for event in events:
            if event["type"] in ["revelation", "reconciliation", "consequence"]:
                if random.random() > 0.6:  # 40% chance of growth moment
                    growth_moments.append(f"{character['name']} learns from {event['description']}")
        
        return growth_moments[:2]  # Limit to 2 growth moments
    
    def _extract_narrative_arc(self, events: List[Dict], peaks: List[Dict]) -> Dict:
        """Extract overall narrative arc from events"""
        
        # Divide events into acts
        act1_end = len(events) // 3
        act2_end = (len(events) * 2) // 3
        
        return {
            "structure": "three-act",
            "act1": {
                "description": "Setup and introduction of conflict",
                "events": events[:act1_end],
                "tension_range": [0.2, 0.5],
                "key_moments": [e["description"] for e in events[:act1_end] if e["tension_level"] > 0.4][:2]
            },
            "act2": {
                "description": "Escalation and complications",
                "events": events[act1_end:act2_end],
                "tension_range": [0.4, 0.8],
                "key_moments": [e["description"] for e in events[act1_end:act2_end] if e["tension_level"] > 0.6][:3]
            },
            "act3": {
                "description": "Climax and resolution",
                "events": events[act2_end:],
                "tension_range": [0.6, 0.9],
                "key_moments": [e["description"] for e in events[act2_end:] if e["tension_level"] > 0.7][:2]
            },
            "climax": peaks[-1] if peaks else None,
            "resolution_type": random.choice(["hopeful", "bittersweet", "ambiguous"])
        }
    
    def _establish_facts(self, early_events: List[Dict]) -> List[str]:
        """Establish world facts from early events"""
        facts = []
        
        fact_templates = [
            "The AI algorithm can predict human behavior with 94% accuracy",
            "Jordan's company has been secretly collecting user data",
            "Sam once faced a similar ethical dilemma and chose wrongly",
            "The investor deadline is non-negotiable",
            "Alex's family is growing concerned about their obsession",
            "The team is divided on the ethical implications",
            "A whistleblower is threatening to expose the project",
            "The government is interested in the technology",
            "Competitors are closing in fast",
            "Trust within the team is fragile"
        ]
        
        # Select facts based on events
        for i, event in enumerate(early_events[:5]):
            if i < len(fact_templates):
                facts.append(fact_templates[i])
        
        return facts
    
    def _generate_relationship_dynamics(self) -> Dict:
        """Generate relationship dynamics between characters"""
        dynamics = {}
        
        for char1 in self.characters:
            for char2 in self.characters:
                if char1["id"] != char2["id"]:
                    key = f"{char1['id']}_{char2['id']}"
                    dynamics[key] = {
                        "characters": [char1["name"], char2["name"]],
                        "relationship_type": char1["relationships"].get(char2["id"], {}).get("type", "neutral"),
                        "tension": abs(char1["relationships"].get(char2["id"], {}).get("strength", 0)),
                        "evolution": random.choice(["strengthening", "weakening", "complicated", "stable"]),
                        "key_conflict": self._generate_conflict_point(char1, char2)
                    }
        
        return dynamics
    
    def _generate_conflict_point(self, char1: Dict, char2: Dict) -> str:
        """Generate a conflict point between two characters"""
        conflicts = [
            f"{char1['name']} and {char2['name']} disagree on the ethical implications",
            f"{char1['name']} feels betrayed by {char2['name']}'s actions",
            f"{char2['name']} challenges {char1['name']}'s leadership",
            f"Past history between {char1['name']} and {char2['name']} resurfaces",
            f"{char1['name']} discovers {char2['name']}'s hidden agenda"
        ]
        return random.choice(conflicts)
    
    def _select_participants(self, event_type: str) -> List[str]:
        """Select participants based on event type"""
        char_ids = [c["id"] for c in self.characters]
        
        if event_type in ["meeting", "crisis"]:
            return char_ids  # All characters
        elif event_type in ["conflict", "confrontation"]:
            return random.sample(char_ids, 2)  # Two characters
        else:
            return random.sample(char_ids, random.randint(1, 2))  # 1-2 characters
    
    def _select_location(self, time_index: int) -> str:
        """Select location based on time in narrative"""
        locations = [
            "Conference Room A",
            "Alex's Office",
            "The Lab",
            "Rooftop Garden",
            "Coffee Shop",
            "Sam's Study",
            "Jordan's Headquarters",
            "The Server Room"
        ]
        
        # Tend toward more dramatic locations later
        if time_index < 5:
            return random.choice(locations[:4])
        else:
            return random.choice(locations)


async def run_full_pipeline_with_mock_data():
    """
    Run the complete Showrunner pipeline with mock simulation data
    This demonstrates the full system architecture without actual simulation
    """
    
    print("=" * 60)
    print("🎬 SHOWRUNNER PIPELINE - MOCK SIMULATION MODE")
    print("=" * 60)
    
    # Configuration
    episode_config = {
        "title": "The Algorithm's Edge",
        "synopsis": "A tech startup faces an ethical dilemma when their AI breakthrough could either save or exploit millions",
        "themes": ["ethics vs ambition", "mentor and protégé", "the cost of innovation"],
        "genre": "techno-thriller",
        "tone": "tense",
        "target_runtime": 22  # minutes
    }
    
    print(f"\n📋 Episode Configuration:")
    print(f"   Title: {episode_config['title']}")
    print(f"   Genre: {episode_config['genre']}")
    print(f"   Themes: {', '.join(episode_config['themes'])}")
    
    # Step 1: Generate Mock Simulation Data
    print("\n" + "="*50)
    print("STEP 1: GENERATING MOCK SIMULATION DATA")
    print("="*50)
    
    mock_generator = MockSimulationGenerator()
    simulation_data = mock_generator.generate_simulation_data(
        theme=episode_config["themes"][0],
        duration_hours=3.0
    )
    
    print(f"✅ Generated simulation data:")
    print(f"   - {len(simulation_data['characters'])} characters")
    print(f"   - {len(simulation_data['events'])} events")
    print(f"   - {len(simulation_data['dramatic_peaks'])} dramatic peaks")
    print(f"   - {len(simulation_data['established_facts'])} established facts")
    
    # Save simulation data
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    with open(output_dir / "mock_simulation_data.json", "w") as f:
        json.dump(simulation_data, f, indent=2)
    print(f"\n📁 Saved simulation data to: output/mock_simulation_data.json")
    
    # Step 2: Initialize LLM Client and Episode Chain
    print("\n" + "="*50)
    print("STEP 2: INITIALIZING LLM PIPELINE")
    print("="*50)
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ Error: OPENAI_API_KEY not set")
        return
    
    # Initialize LLM client with GPT-4.1
    model = os.getenv("DEFAULT_MODEL", "gpt-4.1")
    print(f"🤖 Using model: {model}")
    
    llm_client = LLMClient(
        api_key=api_key,
        model=ModelType.GPT4_1 if "4.1" in model else ModelType.GPT4
    )
    
    # Initialize Episode Chain
    episode_chain = EpisodeChain(llm_client)
    
    # Step 3: Generate Episode through LLM Chain
    print("\n" + "="*50)
    print("STEP 3: GENERATING EPISODE VIA LLM CHAIN")
    print("="*50)
    
    print("Processing through chain stages:")
    print("  1️⃣ Concept Generation")
    print("  2️⃣ Structure Development")
    print("  3️⃣ Scene Breakdown")
    print("  4️⃣ Dialogue Generation")
    print("  5️⃣ Polish & Refinement")
    
    episode_data = await episode_chain.generate_full_episode(
        title=episode_config["title"],
        synopsis=episode_config["synopsis"],
        themes=episode_config["themes"],
        genre=episode_config["genre"],
        tone=episode_config["tone"],
        simulation_data=simulation_data  # Pass our mock data
    )
    
    print(f"\n✅ Generated episode with {len(episode_data.get('scenes', []))} scenes")
    
    # Step 4: Apply Drama Engine Enhancements
    print("\n" + "="*50)
    print("STEP 4: APPLYING DRAMA ENGINE")
    print("="*50)
    
    drama_engine = DramaEngine()
    
    # Enhance each scene with dramatic operators
    enhanced_scenes = []
    for i, scene in enumerate(episode_data.get("scenes", [])):
        print(f"  🎭 Enhancing scene {i+1}...")
        
        # Apply dramatic enhancements
        enhanced_scene = drama_engine.enhance_scene(
            scene,
            max_operators=3  # Maximum dramatic operators per scene
        )
        
        # Add enhancement details
        if "dramatic_operators" in enhanced_scene:
            operators = enhanced_scene["dramatic_operators"]
            print(f"     Added: {', '.join(operators) if operators else 'none'}")
        
        enhanced_scenes.append(enhanced_scene)
    
    episode_data["scenes"] = enhanced_scenes
    
    # Step 5: Analyze Dramatic Arc
    print("\n" + "="*50)
    print("STEP 5: ANALYZING DRAMATIC ARC")
    print("="*50)
    
    arc_analysis = drama_engine.analyze_dramatic_arc(enhanced_scenes)
    episode_data["dramatic_arc"] = arc_analysis
    
    print(f"📈 Dramatic Arc Analysis:")
    print(f"   - Average Tension: {arc_analysis.get('average_tension', 0):.2f}")
    print(f"   - Peak Count: {arc_analysis.get('num_peaks', 0)}")
    print(f"   - Has Rising Action: {arc_analysis.get('has_rising_action', False)}")
    print(f"   - Has Climax: {arc_analysis.get('has_climax', False)}")
    print(f"   - Has Resolution: {arc_analysis.get('has_resolution', False)}")
    print(f"   - Arc Quality: {arc_analysis.get('arc_quality', 'unknown')}")
    
    # Step 6: Add Metadata
    episode_data["metadata"] = {
        "generated_at": datetime.now().isoformat(),
        "pipeline_mode": "mock_simulation",
        "model_used": model,
        "simulation_type": "mock",
        "drama_enhancements": True,
        "arc_analysis": True
    }
    
    # Step 7: Save Final Output
    print("\n" + "="*50)
    print("STEP 6: SAVING OUTPUT")
    print("="*50)
    
    # Save JSON
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = output_dir / f"episode_mock_{timestamp}.json"
    with open(json_path, "w") as f:
        json.dump(episode_data, f, indent=2)
    
    # Also save as latest
    with open(output_dir / "latest_episode_mock.json", "w") as f:
        json.dump(episode_data, f, indent=2)
    
    print(f"📁 Saved episode to:")
    print(f"   - {json_path}")
    print(f"   - output/latest_episode_mock.json")
    
    # Step 8: Generate Summary Report
    print("\n" + "="*60)
    print("📊 GENERATION SUMMARY")
    print("="*60)
    
    print(f"\n🎬 Episode: {episode_data.get('title', 'Untitled')}")
    print(f"📝 Genre: {episode_data.get('genre', 'Unknown')}")
    print(f"🎭 Total Scenes: {len(episode_data.get('scenes', []))}")
    
    if episode_data.get("scenes"):
        print(f"\n📍 Scene Locations:")
        for i, scene in enumerate(episode_data["scenes"][:3], 1):
            print(f"   {i}. {scene.get('location', 'Unknown')}")
        if len(episode_data["scenes"]) > 3:
            print(f"   ... and {len(episode_data['scenes']) - 3} more")
    
    print(f"\n🎯 Dramatic Elements Applied:")
    all_operators = []
    for scene in episode_data.get("scenes", []):
        all_operators.extend(scene.get("dramatic_operators", []))
    
    from collections import Counter
    operator_counts = Counter(all_operators)
    for op, count in operator_counts.most_common():
        print(f"   - {op}: {count} times")
    
    print(f"\n✨ Quality Metrics:")
    if arc_analysis:
        print(f"   - Tension Curve: {'✅ Good' if arc_analysis.get('has_rising_action') else '⚠️ Needs work'}")
        print(f"   - Climax: {'✅ Present' if arc_analysis.get('has_climax') else '❌ Missing'}")
        print(f"   - Resolution: {'✅ Complete' if arc_analysis.get('has_resolution') else '⚠️ Incomplete'}")
    
    print("\n" + "="*60)
    print("✅ PIPELINE COMPLETE!")
    print("="*60)
    
    # Close LLM client
    await llm_client.close()
    
    return episode_data


def main():
    """Main entry point"""
    print("\n🎬 Showrunner Pipeline - Mock Simulation Example")
    print("This demonstrates the full pipeline with mock simulation data")
    print("Perfect for testing the LLM chain and drama engine without simulation cost\n")
    
    # Run the pipeline
    episode = asyncio.run(run_full_pipeline_with_mock_data())
    
    print("\n💡 Next Steps:")
    print("1. Check output/mock_simulation_data.json for the simulation data")
    print("2. Check output/latest_episode_mock.json for the final episode")
    print("3. Modify the mock data generator for different scenarios")
    print("4. Adjust drama engine parameters for different effects")


if __name__ == "__main__":
    main()