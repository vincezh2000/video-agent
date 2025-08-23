#!/usr/bin/env python3
"""
Example: Generate Episode Without Simulation
This example demonstrates how to generate a full episode using only the LLM prompt chain,
bypassing the multi-agent simulation phase.
"""

import asyncio
import json
from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

@dataclass
class Character:
    """Simple character definition without agent simulation"""
    name: str
    role: str
    personality: str
    backstory: str
    goals: List[str]
    
@dataclass
class Scene:
    """Scene structure for episode generation"""
    scene_number: int
    location: str
    characters: List[str]
    description: str
    dialogue: List[Dict[str, str]]
    dramatic_elements: List[str]
    
class DirectEpisodeGenerator:
    """Generate episodes directly through prompt chains without simulation"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key required")
        self.client = OpenAI(api_key=self.api_key)
        
        # Define main characters (normally from simulation)
        self.characters = [
            Character(
                name="Alex Chen",
                role="protagonist",
                personality="Ambitious, tech-savvy, but struggling with work-life balance",
                backstory="Former startup founder who lost everything, now rebuilding",
                goals=["Launch new AI product", "Reconnect with family"]
            ),
            Character(
                name="Sam Rodriguez", 
                role="mentor",
                personality="Wise, experienced, slightly cynical but caring",
                backstory="Veteran entrepreneur with multiple exits, seeking meaning",
                goals=["Guide next generation", "Find personal fulfillment"]
            ),
            Character(
                name="Jordan Park",
                role="rival",
                personality="Competitive, brilliant, morally flexible",
                backstory="Prodigy who never experienced failure, ruthlessly ambitious",
                goals=["Dominate the market", "Prove superiority"]
            )
        ]
        
    async def generate_episode(self, 
                              episode_title: str,
                              episode_theme: str = "ambition vs ethics",
                              target_scenes: int = 8) -> Dict[str, Any]:
        """Main pipeline for episode generation without simulation
        
        Args:
            episode_title: Title of the episode
            episode_theme: Central theme to explore
            target_scenes: Number of scenes to generate (default 8 for 22-minute episode)
        """
        
        print(f"🎬 Generating Episode: {episode_title}")
        print(f"📝 Target: {target_scenes} scenes")
        print("=" * 50)
        
        # Step 1: Concept Generation (replaces simulation data)
        print("\n📝 Step 1: Generating Core Concept...")
        concept = await self._generate_concept(episode_title, episode_theme)
        
        # Step 2: Plot Structure
        print("\n📊 Step 2: Creating Plot Structure...")
        plot = await self._generate_plot_structure(concept, target_scenes)
        
        # Step 3: Scene Breakdown
        print("\n🎭 Step 3: Breaking Down Scenes...")
        scenes = await self._generate_scenes(plot)
        
        # Step 4: Dialogue Generation
        print("\n💬 Step 4: Generating Dialogue...")
        scenes_with_dialogue = await self._generate_dialogue(scenes)
        
        # Step 5: Drama Enhancement
        print("\n✨ Step 5: Enhancing Drama...")
        enhanced_scenes = await self._enhance_drama(scenes_with_dialogue)
        
        # Step 6: Final Polish
        print("\n🎨 Step 6: Final Polish...")
        final_episode = await self._polish_episode(enhanced_scenes)
        
        return {
            "title": episode_title,
            "theme": episode_theme,
            "concept": concept,
            "plot": plot,
            "scenes": final_episode,
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "total_scenes": len(final_episode),
                "characters": [c.name for c in self.characters]
            }
        }
    
    async def _generate_concept(self, title: str, theme: str) -> Dict[str, Any]:
        """Generate core concept using predefined characters instead of simulation"""
        
        prompt = f"""
        Generate a compelling episode concept for: "{title}"
        Theme: {theme}
        
        Characters:
        {self._format_characters()}
        
        Create a concept that:
        1. Centers on the theme of {theme}
        2. Creates natural conflict between characters
        3. Has clear stakes and urgency
        4. Fits within a 22-minute episode
        
        Return as JSON with: central_conflict, stakes, urgency_driver, subplot
        """
        
        response = await self._call_llm(prompt, temperature=0.8)
        return json.loads(response)
    
    async def _generate_plot_structure(self, concept: Dict, target_scenes: int = 8) -> Dict[str, Any]:
        """Create three-act structure with flexible scene count"""
        
        # Calculate scene distribution based on target
        act1_scenes = max(2, target_scenes // 3)
        act2_scenes = max(2, target_scenes // 3)
        act3_scenes = target_scenes - act1_scenes - act2_scenes
        
        prompt = f"""
        Given this concept: {json.dumps(concept, indent=2)}
        
        Create a three-act structure with exactly {target_scenes} scenes:
        - Act 1: Setup ({act1_scenes} scenes)
        - Act 2: Escalation ({act2_scenes} scenes) 
        - Act 3: Resolution ({act3_scenes} scenes)
        
        Use the ABABC pattern where:
        A = Main plot with protagonist
        B = Subplot or rival's perspective
        C = Convergence of all threads
        
        Return as JSON with: act1, act2, act3 (each containing scene_beats array)
        Each scene_beat should have a clear dramatic purpose.
        """
        
        response = await self._call_llm(prompt, temperature=0.7)
        return json.loads(response)
    
    async def _generate_scenes(self, plot: Dict) -> List[Scene]:
        """Generate detailed scene breakdowns"""
        scenes = []
        scene_num = 1
        
        for act_name, act_content in plot.items():
            for beat in act_content.get("scene_beats", []):
                prompt = f"""
                Generate scene {scene_num} details:
                Beat: {beat}
                
                Include:
                - Location (specific and visual)
                - Characters present (from: {[c.name for c in self.characters]})
                - Scene description (2-3 sentences)
                - Key dramatic moments
                
                Return as JSON with: location, characters, description, dramatic_elements
                """
                
                response = await self._call_llm(prompt, temperature=0.7)
                try:
                    scene_data = json.loads(response)
                except json.JSONDecodeError:
                    # Fallback if JSON parsing fails
                    scene_data = {
                        "location": f"Location {scene_num}",
                        "characters": ["Alex Chen", "Sam Rodriguez"],
                        "description": f"Scene {scene_num} description",
                        "dramatic_elements": ["tension"]
                    }
                
                scenes.append(Scene(
                    scene_number=scene_num,
                    location=scene_data.get("location", f"Location {scene_num}"),
                    characters=scene_data.get("characters", ["Alex Chen"]),
                    description=scene_data.get("description", f"Scene {scene_num}"),
                    dialogue=[],  # Will be filled in next step
                    dramatic_elements=scene_data.get("dramatic_elements", [])
                ))
                scene_num += 1
                
        return scenes
    
    async def _generate_dialogue(self, scenes: List[Scene]) -> List[Scene]:
        """Generate dialogue for each scene"""
        
        for scene in scenes:
            character_context = self._get_character_context(scene.characters)
            
            prompt = f"""
            Scene {scene.scene_number} - {scene.location}
            
            Context: {scene.description}
            
            Characters speaking:
            {character_context}
            
            Dramatic beats: {', '.join(scene.dramatic_elements[:2]) if scene.dramatic_elements else 'tension building'}
            
            Write 6-8 lines of natural dialogue between these characters.
            Each line should reveal character and advance the plot.
            
            Output as a JSON array with exactly this format:
            [
                {{"speaker": "{scene.characters[0] if scene.characters else 'Alex Chen'}", "line": "actual dialogue here"}},
                {{"speaker": "{scene.characters[1] if len(scene.characters) > 1 else 'Sam Rodriguez'}", "line": "response dialogue"}}
            ]
            
            Return ONLY the JSON array, no other text.
            """
            
            response = await self._call_llm(prompt, temperature=0.8, expect_array=True)
            try:
                # Try to parse the response
                dialogue_data = json.loads(response)
                if isinstance(dialogue_data, list) and len(dialogue_data) > 0:
                    # Validate each dialogue entry
                    valid_dialogue = []
                    for entry in dialogue_data:
                        if isinstance(entry, dict) and "speaker" in entry and "line" in entry:
                            valid_dialogue.append({
                                "speaker": entry["speaker"],
                                "line": entry["line"]
                            })
                    
                    if valid_dialogue:
                        scene.dialogue = valid_dialogue
                    else:
                        # Generate better fallback dialogue
                        scene.dialogue = self._generate_fallback_dialogue(scene)
                else:
                    scene.dialogue = self._generate_fallback_dialogue(scene)
            except (json.JSONDecodeError, TypeError) as e:
                print(f"Warning: Dialogue generation failed for scene {scene.scene_number}: {e}")
                scene.dialogue = self._generate_fallback_dialogue(scene)
            
        return scenes
    
    async def _enhance_drama(self, scenes: List[Scene]) -> List[Scene]:
        """Apply dramatic operators"""
        
        operators = ["reversal", "foreshadowing", "callback", "escalation", "cliffhanger"]
        
        # Apply cliffhanger to act breaks
        for i, scene in enumerate(scenes):
            if scene.scene_number in [3, 6]:  # End of Act 1 and 2
                scene.dramatic_elements.append("cliffhanger")
                
                # Enhance last dialogue line
                if scene.dialogue:
                    last_line = scene.dialogue[-1]
                    prompt = f"""
                    Rewrite this line to create a cliffhanger:
                    Original: "{last_line['line']}"
                    Speaker: {last_line['speaker']}
                    
                    Make it more dramatic while keeping it natural.
                    Return just the new line text.
                    """
                    
                    new_line = await self._call_llm(prompt, temperature=0.9)
                    if new_line and new_line != "{}":
                        scene.dialogue[-1]["line"] = new_line.strip('"')
                    
        return scenes
    
    async def _polish_episode(self, scenes: List[Scene]) -> List[Dict]:
        """Final polish and formatting"""
        
        polished = []
        for scene in scenes:
            polished.append({
                "scene_number": scene.scene_number,
                "location": scene.location,
                "time_of_day": self._infer_time_of_day(scene.scene_number),
                "characters": scene.characters,
                "description": scene.description,
                "dialogue": scene.dialogue,
                "dramatic_elements": scene.dramatic_elements,
                "estimated_duration": len(scene.dialogue) * 5  # Rough estimate in seconds
            })
            
        return polished
    
    async def _call_llm(self, prompt: str, temperature: float = 0.7, expect_array: bool = False) -> str:
        """Make LLM API call with better JSON handling"""
        try:
            # Use GPT-4.1 from environment or default
            model = os.getenv("DEFAULT_MODEL", "gpt-4.1")
            
            response = self.client.chat.completions.create(
                model=model,  # Using GPT-4.1 for superior performance
                messages=[
                    {"role": "system", "content": "You are a TV writer. Output only valid JSON without any markdown or extra text."},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=2000  # Increased for GPT-4.1's better output capacity
            )
            content = response.choices[0].message.content
            
            if content:
                # Clean up the response
                content = content.strip()
                
                # Remove markdown code blocks if present
                if content.startswith("```json"):
                    content = content[7:]
                if content.startswith("```"):
                    content = content[3:]
                if content.endswith("```"):
                    content = content[:-3]
                content = content.strip()
                
                # Try to extract JSON based on expected format
                import re
                if expect_array:
                    # Look for array
                    json_match = re.search(r'\[.*\]', content, re.DOTALL)
                    if json_match:
                        return json_match.group()
                else:
                    # Look for object
                    json_match = re.search(r'\{.*\}', content, re.DOTALL)
                    if json_match:
                        return json_match.group()
                
                # Return cleaned content as fallback
                return content
            
            return "[]" if expect_array else "{}"
            
        except Exception as e:
            print(f"LLM call failed: {e}")
            return "[]" if expect_array else "{}"
    
    def _format_characters(self) -> str:
        """Format character info for prompts"""
        return "\n".join([
            f"- {c.name} ({c.role}): {c.personality}"
            for c in self.characters
        ])
    
    def _get_character_context(self, character_names: List[str]) -> str:
        """Get detailed context for specific characters"""
        context = []
        for name in character_names:
            for char in self.characters:
                if char.name == name:
                    context.append(f"{name}:\n  Personality: {char.personality}\n  Goals: {', '.join(char.goals)}")
        return "\n".join(context)
    
    def _infer_time_of_day(self, scene_number: int) -> str:
        """Simple time progression"""
        times = ["MORNING", "LATE MORNING", "NOON", "AFTERNOON", 
                "LATE AFTERNOON", "EVENING", "NIGHT", "LATE NIGHT"]
        return times[min(scene_number - 1, len(times) - 1)]
    
    def _generate_fallback_dialogue(self, scene: Scene) -> List[Dict[str, str]]:
        """Generate contextual fallback dialogue when API fails"""
        fallback_lines = {
            "Alex Chen": [
                "We need to make a decision now.",
                "This isn't just about the code anymore.",
                "I've worked too hard to let this fail.",
                "There has to be another way."
            ],
            "Sam Rodriguez": [
                "Think about what you're doing, Alex.",
                "This is bigger than just winning.",
                "You know what the right choice is.",
                "I'm here to support you, whatever you decide."
            ],
            "Jordan Park": [
                "You know my terms.",
                "Time's running out.",
                "This is how the game is played.",
                "Make your choice."
            ]
        }
        
        dialogue = []
        for i, char in enumerate(scene.characters[:4]):  # Max 4 exchanges
            if char in fallback_lines:
                line = fallback_lines[char][min(i, len(fallback_lines[char])-1)]
            else:
                line = f"We need to discuss this."
            dialogue.append({"speaker": char, "line": line})
        
        return dialogue

def format_episode_output(episode_data: Dict) -> str:
    """Format episode for readable output"""
    output = []
    output.append(f"\n{'='*60}")
    output.append(f"EPISODE: {episode_data['title']}")
    output.append(f"THEME: {episode_data['theme']}")
    output.append(f"{'='*60}\n")
    
    current_act = 1
    for scene in episode_data['scenes']:
        # Mark act breaks
        if scene['scene_number'] == 4:
            output.append(f"\n{'='*30} ACT 2 {'='*30}\n")
            current_act = 2
        elif scene['scene_number'] == 7:
            output.append(f"\n{'='*30} ACT 3 {'='*30}\n")
            current_act = 3
            
        output.append(f"SCENE {scene['scene_number']}")
        output.append(f"INT. {scene['location']} - {scene['time_of_day']}")
        output.append(f"\n{scene['description']}\n")
        
        for dialogue in scene['dialogue']:
            output.append(f"  {dialogue['speaker'].upper()}")
            output.append(f"    {dialogue['line']}\n")
            
        if scene['dramatic_elements']:
            output.append(f"  [Dramatic elements: {', '.join(scene['dramatic_elements'])}]\n")
            
    output.append(f"\n{'='*60}")
    output.append(f"Total Runtime: ~22 minutes")
    output.append(f"Total Scenes: {len(episode_data['scenes'])}")
    output.append(f"{'='*60}\n")
    
    return "\n".join(output)

async def main():
    """Run example episode generation"""
    
    # Create output directory if it doesn't exist
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  Warning: OPENAI_API_KEY not set")
        print("To run this example with real LLM:")
        print("  export OPENAI_API_KEY='your-key-here'")
        print("\nContinuing with mock generation...\n")
        
        # Create mock episode for demonstration
        mock_episode = create_mock_episode()
        
        # Save to output folder
        output_path = os.path.join(output_dir, "generated_episode_mock.txt")
        with open(output_path, "w") as f:
            f.write(format_episode_output(mock_episode))
        
        json_path = os.path.join(output_dir, "generated_episode_mock.json")
        with open(json_path, "w") as f:
            json.dump(mock_episode, f, indent=2)
            
        print(f"✅ Mock episode saved to:")
        print(f"   - {output_path} (formatted text)")
        print(f"   - {json_path} (JSON data)")
        return
    
    # Generate real episode
    generator = DirectEpisodeGenerator(api_key)
    
    # Example episode generation
    episode = await generator.generate_episode(
        episode_title="The Algorithm's Edge",
        episode_theme="Innovation vs Ethics in AI"
    )
    
    # Save formatted output to text file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    text_output_path = os.path.join(output_dir, f"episode_{timestamp}.txt")
    with open(text_output_path, "w") as f:
        f.write(format_episode_output(episode))
    
    # Save JSON data
    json_output_path = os.path.join(output_dir, f"episode_{timestamp}.json")
    with open(json_output_path, "w") as f:
        json.dump(episode, f, indent=2)
    
    # Also save as latest for easy access
    latest_text_path = os.path.join(output_dir, "latest_episode.txt")
    with open(latest_text_path, "w") as f:
        f.write(format_episode_output(episode))
        
    latest_json_path = os.path.join(output_dir, "latest_episode.json")
    with open(latest_json_path, "w") as f:
        json.dump(episode, f, indent=2)
    
    print(f"\n✅ Episode successfully generated using {os.getenv('DEFAULT_MODEL', 'gpt-4.1')}")
    print(f"\n📁 Files saved to output folder:")
    print(f"   - {text_output_path} (formatted screenplay)")
    print(f"   - {json_output_path} (structured data)")
    print(f"   - {latest_text_path} (latest copy)")
    print(f"   - {latest_json_path} (latest JSON)")
    print(f"\n📊 Episode Statistics:")
    print(f"   - Title: {episode['title']}")
    print(f"   - Total Scenes: {len(episode['scenes'])}")
    print(f"   - Characters: {', '.join(episode['metadata']['characters'])}")
    print(f"   - Runtime: ~22 minutes")

def create_mock_episode() -> Dict:
    """Create a mock episode for demonstration without API"""
    return {
        "title": "The Algorithm's Edge",
        "theme": "Innovation vs Ethics in AI",
        "concept": {
            "central_conflict": "Alex must choose between launching an AI that could save lives but has privacy concerns",
            "stakes": "Company survival vs user trust",
            "urgency_driver": "Competitor launching in 48 hours",
            "subplot": "Sam questions if mentoring is enabling harmful tech"
        },
        "plot": {
            "act1": {"scene_beats": ["Setup: Alex's struggling startup", "The breakthrough discovery", "Jordan's threat"]},
            "act2": {"scene_beats": ["Ethical dilemma revealed", "Sam's warning", "Betrayal"]},
            "act3": {"scene_beats": ["The choice", "Resolution"]}
        },
        "scenes": [
            {
                "scene_number": 1,
                "location": "STARTUP OFFICE - CRAMPED WORKSPACE",
                "time_of_day": "MORNING",
                "characters": ["Alex Chen", "Sam Rodriguez"],
                "description": "Alex frantically codes while empty coffee cups pile up. Sam enters with concern.",
                "dialogue": [
                    {"speaker": "Sam Rodriguez", "line": "You look like hell. When's the last time you went home?"},
                    {"speaker": "Alex Chen", "line": "Home? Sam, we're 48 hours from Jordan's launch. I can't stop now."},
                    {"speaker": "Sam Rodriguez", "line": "Sometimes the best move is knowing when not to play."},
                    {"speaker": "Alex Chen", "line": "Easy for you to say. You already won your games."}
                ],
                "dramatic_elements": ["tension", "foreshadowing"],
                "estimated_duration": 20
            },
            {
                "scene_number": 2,
                "location": "ALEX'S OFFICE - PRIVATE",
                "time_of_day": "LATE MORNING",
                "characters": ["Alex Chen"],
                "description": "Alex discovers something unexpected in the algorithm's behavior patterns.",
                "dialogue": [
                    {"speaker": "Alex Chen", "line": "Wait... that's not possible. The algorithm is..."},
                    {"speaker": "Alex Chen", "line": "It's learning from private user data without permission."},
                    {"speaker": "Alex Chen", "line": "But it's also predicting health crises with 97% accuracy."},
                    {"speaker": "Alex Chen", "line": "Oh god. What have I created?"}
                ],
                "dramatic_elements": ["revelation", "moral dilemma"],
                "estimated_duration": 20
            },
            {
                "scene_number": 3,
                "location": "COFFEE SHOP",
                "time_of_day": "NOON",
                "characters": ["Alex Chen", "Jordan Park"],
                "description": "Jordan ambushes Alex at their usual coffee spot with an ultimatum.",
                "dialogue": [
                    {"speaker": "Jordan Park", "line": "I know about your breakthrough, Alex."},
                    {"speaker": "Alex Chen", "line": "How could you possibly—"},
                    {"speaker": "Jordan Park", "line": "Same way I know you're conflicted about using it."},
                    {"speaker": "Jordan Park", "line": "Here's my offer: Join me, or I'll bury your company."},
                    {"speaker": "Alex Chen", "line": "You're bluffing."},
                    {"speaker": "Jordan Park", "line": "I already have your lead engineer's resignation letter. Want to bet who's next?"}
                ],
                "dramatic_elements": ["confrontation", "cliffhanger"],
                "estimated_duration": 30
            }
        ],
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "total_scenes": 3,
            "characters": ["Alex Chen", "Sam Rodriguez", "Jordan Park"]
        }
    }

if __name__ == "__main__":
    print("🎬 Showrunner Episode Generator (No Simulation Mode)")
    print("=" * 60)
    asyncio.run(main())