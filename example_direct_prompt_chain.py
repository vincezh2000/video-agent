#!/usr/bin/env python3
"""
Direct Prompt Chain Implementation
This shows how to use the prompt chain system without agent simulation data
"""

import asyncio
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import yaml
import os

@dataclass
class PromptStage:
    """Single stage in the prompt chain"""
    name: str
    prompt_template: str
    temperature: float
    validator: Optional[callable] = None
    discriminator: Optional[str] = None  # Next stage acts as discriminator
    
class DirectPromptChain:
    """
    Prompt chain that works without simulation data
    Uses predefined context instead of agent-generated data
    """
    
    def __init__(self, config_path: str = "config_direct_mode.yaml"):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
            
        self.stages = self._initialize_stages()
        self.context = {}  # Accumulates context through the chain
        
    def _initialize_stages(self) -> List[PromptStage]:
        """Define the prompt chain stages"""
        return [
            PromptStage(
                name="concept_generation",
                prompt_template="""
                Create an episode concept for a 22-minute show.
                
                Context:
                - Setting: Modern tech startup world
                - Tone: Drama with comedic elements
                - Core themes: {themes}
                
                Requirements:
                1. Central conflict that can resolve in 22 minutes
                2. B-plot that complements the main story
                3. Character growth opportunity
                4. Unexpected but logical twist
                
                Output format:
                {{
                    "logline": "One sentence episode summary",
                    "central_conflict": "Main problem to solve",
                    "b_plot": "Secondary storyline", 
                    "themes": ["theme1", "theme2"],
                    "twist": "Unexpected element",
                    "stakes": "What happens if they fail"
                }}
                """,
                temperature=0.8,
                discriminator="concept_discrimination"
            ),
            
            PromptStage(
                name="concept_discrimination",
                prompt_template="""
                Evaluate this episode concept for quality and producibility:
                {previous_output}
                
                Score on:
                1. Originality (1-10)
                2. Character potential (1-10)
                3. Dramatic tension (1-10)
                4. Producibility (1-10)
                5. Theme integration (1-10)
                
                If average score < 7, suggest improvements.
                
                Output format:
                {{
                    "scores": {{"originality": N, "character": N, "drama": N, "producible": N, "theme": N}},
                    "average": N,
                    "improvements": ["suggestion1", "suggestion2"] or null,
                    "proceed": true/false
                }}
                """,
                temperature=0.3,
                validator=lambda x: json.loads(x).get("proceed", False)
            ),
            
            PromptStage(
                name="structure_generation",
                prompt_template="""
                Create a detailed story structure from this concept:
                {concept}
                
                Use the three-act structure:
                - Act 1 (25%): Setup - Scenes 1-2
                - Act 2 (50%): Confrontation - Scenes 3-5
                - Act 3 (25%): Resolution - Scenes 6-8
                
                Apply the {plot_pattern} pattern for scene flow.
                
                For each scene include:
                - Location
                - Key characters (2-3)
                - Core conflict/goal
                - How it advances the plot
                - Emotional tone
                
                Output as structured JSON with acts and scenes.
                """,
                temperature=0.7,
                discriminator="structure_validation"
            ),
            
            PromptStage(
                name="structure_validation", 
                prompt_template="""
                Validate this story structure for narrative coherence:
                {previous_output}
                
                Check for:
                1. Logical flow between scenes
                2. Proper escalation of conflict
                3. Character arc progression
                4. Pacing issues
                5. Setup and payoff alignment
                
                Output format:
                {{
                    "coherence_score": N (1-10),
                    "issues": ["issue1", "issue2"] or [],
                    "suggestions": ["fix1", "fix2"] or [],
                    "approved": true/false
                }}
                """,
                temperature=0.3,
                validator=lambda x: json.loads(x).get("approved", False)
            ),
            
            PromptStage(
                name="scene_expansion",
                prompt_template="""
                Expand scene {scene_number} with full details:
                
                Scene outline: {scene_outline}
                Previous scene: {previous_scene}
                Episode themes: {themes}
                
                Create:
                1. Detailed scene description (3-4 sentences)
                2. Character motivations and goals
                3. Key dialogue beats (not full dialogue yet)
                4. Visual elements and atmosphere
                5. Transition to next scene
                
                Include at least one of these dramatic elements:
                - Reversal
                - Revelation  
                - Escalation
                - Callback
                - Foreshadowing
                
                Output as detailed JSON.
                """,
                temperature=0.75,
                discriminator=None  # No discrimination for individual scenes
            ),
            
            PromptStage(
                name="dialogue_generation",
                prompt_template="""
                Write natural dialogue for this scene:
                
                Scene: {scene_details}
                Characters involved: {characters}
                Dialogue beats to hit: {dialogue_beats}
                
                Character voices:
                {character_voices}
                
                Requirements:
                - 8-12 exchanges
                - Subtext and conflict
                - Natural speech patterns
                - Advance the plot
                - Reveal character
                
                Format each line as:
                {{"speaker": "Name", "line": "Dialogue", "subtext": "Hidden meaning"}}
                """,
                temperature=0.8,
                discriminator="dialogue_polish"
            ),
            
            PromptStage(
                name="dialogue_polish",
                prompt_template="""
                Polish this dialogue for maximum impact:
                {previous_output}
                
                Improve:
                1. Remove exposition dumps
                2. Add more subtext
                3. Sharpen conflict
                4. Make voices more distinct
                5. Trim unnecessary words
                
                Keep the same structure but enhance quality.
                Mark changes with "ENHANCED" tag.
                """,
                temperature=0.6,
                validator=None
            ),
            
            PromptStage(
                name="drama_injection",
                prompt_template="""
                Enhance dramatic impact of this scene:
                {scene_with_dialogue}
                
                Available operators: {drama_operators}
                Current act: {act_number}
                
                Add 1-2 dramatic operators without making it melodramatic.
                For act breaks, consider adding cliffhangers.
                
                Output the enhanced scene with drama_elements array.
                """,
                temperature=0.7,
                discriminator=None
            ),
            
            PromptStage(
                name="final_coherence",
                prompt_template="""
                Final coherence check for the complete episode:
                {full_episode}
                
                Verify:
                1. All setups have payoffs
                2. Character arcs complete
                3. Themes are integrated
                4. Pacing works for 22 minutes
                5. Ending satisfies but leaves room for future
                
                Make minimal adjustments for coherence.
                Output the final polished episode.
                """,
                temperature=0.5,
                validator=None
            )
        ]
        
    async def run_chain(self, initial_context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the full prompt chain"""
        
        self.context = initial_context
        results = {}
        
        print("🔗 Starting Direct Prompt Chain")
        print("=" * 50)
        
        # Stage 1-2: Concept Generation & Discrimination
        concept = await self._run_concept_stages()
        results['concept'] = concept
        
        # Stage 3-4: Structure Generation & Validation
        structure = await self._run_structure_stages(concept)
        results['structure'] = structure
        
        # Stage 5-7: Scene Expansion & Dialogue
        scenes = await self._run_scene_stages(structure)
        results['scenes'] = scenes
        
        # Stage 8: Drama Enhancement
        enhanced_scenes = await self._run_drama_stage(scenes)
        results['enhanced_scenes'] = enhanced_scenes
        
        # Stage 9: Final Coherence
        final_episode = await self._run_final_stage(enhanced_scenes)
        results['final_episode'] = final_episode
        
        return results
        
    async def _run_concept_stages(self) -> Dict:
        """Run concept generation with discrimination loop"""
        
        max_attempts = 3
        for attempt in range(max_attempts):
            print(f"\n📝 Concept Generation (Attempt {attempt + 1})")
            
            # Generate concept
            concept_prompt = self.stages[0].prompt_template.format(
                themes=self.context.get('themes', 'ambition, ethics, human connection')
            )
            concept = await self._mock_llm_call(concept_prompt, self.stages[0].temperature)
            
            # Discriminate
            print("   🔍 Discriminating concept quality...")
            discrimination_prompt = self.stages[1].prompt_template.format(
                previous_output=concept
            )
            evaluation = await self._mock_llm_call(discrimination_prompt, self.stages[1].temperature)
            
            eval_data = json.loads(evaluation)
            if eval_data['proceed']:
                print(f"   ✅ Concept approved (score: {eval_data['average']}/10)")
                return json.loads(concept)
            else:
                print(f"   ❌ Concept rejected (score: {eval_data['average']}/10)")
                print(f"   💡 Improvements: {eval_data['improvements']}")
                
        # Fallback if no good concept
        print("   ⚠️  Using fallback concept template")
        return self._get_fallback_concept()
        
    async def _run_structure_stages(self, concept: Dict) -> Dict:
        """Generate and validate story structure"""
        
        print("\n📊 Structure Generation")
        
        structure_prompt = self.stages[2].prompt_template.format(
            concept=json.dumps(concept, indent=2),
            plot_pattern=self.context.get('plot_pattern', 'ABABC')
        )
        structure = await self._mock_llm_call(structure_prompt, self.stages[2].temperature)
        
        # Validate structure
        print("   🔍 Validating narrative coherence...")
        validation_prompt = self.stages[3].prompt_template.format(
            previous_output=structure
        )
        validation = await self._mock_llm_call(validation_prompt, self.stages[3].temperature)
        
        val_data = json.loads(validation)
        if val_data['approved']:
            print(f"   ✅ Structure approved (coherence: {val_data['coherence_score']}/10)")
            return json.loads(structure)
        else:
            print(f"   ⚠️  Structure has issues: {val_data['issues']}")
            # In production, would retry or apply fixes
            return json.loads(structure)
            
    async def _run_scene_stages(self, structure: Dict) -> List[Dict]:
        """Expand scenes and generate dialogue"""
        
        print("\n🎭 Scene Expansion & Dialogue")
        
        scenes = []
        scene_num = 1
        
        for act_name, act_data in structure.items():
            if not act_name.startswith('act'):
                continue
                
            for scene_beat in act_data.get('scenes', []):
                print(f"   Scene {scene_num}...")
                
                # Expand scene
                expansion_prompt = self.stages[4].prompt_template.format(
                    scene_number=scene_num,
                    scene_outline=scene_beat,
                    previous_scene=scenes[-1] if scenes else "None",
                    themes=self.context.get('themes', '')
                )
                expanded = await self._mock_llm_call(expansion_prompt, self.stages[4].temperature)
                scene_data = json.loads(expanded)
                
                # Generate dialogue
                dialogue_prompt = self.stages[5].prompt_template.format(
                    scene_details=json.dumps(scene_data),
                    characters=scene_data.get('characters', []),
                    dialogue_beats=scene_data.get('dialogue_beats', []),
                    character_voices=self._get_character_voices()
                )
                dialogue = await self._mock_llm_call(dialogue_prompt, self.stages[5].temperature)
                
                # Polish dialogue
                polish_prompt = self.stages[6].prompt_template.format(
                    previous_output=dialogue
                )
                polished = await self._mock_llm_call(polish_prompt, self.stages[6].temperature)
                
                scene_data['dialogue'] = json.loads(polished)
                scenes.append(scene_data)
                scene_num += 1
                
        print(f"   ✅ Generated {len(scenes)} scenes")
        return scenes
        
    async def _run_drama_stage(self, scenes: List[Dict]) -> List[Dict]:
        """Enhance scenes with dramatic operators"""
        
        print("\n✨ Drama Enhancement")
        
        enhanced = []
        for i, scene in enumerate(scenes):
            act_number = 1 if i < 2 else (2 if i < 5 else 3)
            
            drama_prompt = self.stages[7].prompt_template.format(
                scene_with_dialogue=json.dumps(scene),
                drama_operators=['reversal', 'revelation', 'escalation', 'callback', 'cliffhanger'],
                act_number=act_number
            )
            enhanced_scene = await self._mock_llm_call(drama_prompt, self.stages[7].temperature)
            enhanced.append(json.loads(enhanced_scene))
            
        print("   ✅ Drama operators applied")
        return enhanced
        
    async def _run_final_stage(self, scenes: List[Dict]) -> Dict:
        """Final coherence pass"""
        
        print("\n🎨 Final Polish")
        
        episode = {
            'title': self.context.get('title', 'Untitled Episode'),
            'themes': self.context.get('themes', []),
            'scenes': scenes
        }
        
        final_prompt = self.stages[8].prompt_template.format(
            full_episode=json.dumps(episode, indent=2)
        )
        final = await self._mock_llm_call(final_prompt, self.stages[8].temperature)
        
        print("   ✅ Episode complete")
        return json.loads(final)
        
    async def _mock_llm_call(self, prompt: str, temperature: float) -> str:
        """
        Mock LLM call for demonstration
        In production, replace with actual OpenAI/Anthropic API call
        """
        
        # Simulate API delay
        await asyncio.sleep(0.5)
        
        # Return mock responses based on prompt content
        if "episode concept" in prompt.lower():
            return json.dumps({
                "logline": "A startup founder must choose between groundbreaking AI and user privacy",
                "central_conflict": "Launch revolutionary AI or protect user data",
                "b_plot": "Mentor questions their role in enabling harmful tech",
                "themes": ["innovation vs ethics", "ambition vs integrity"],
                "twist": "The rival secretly wants to collaborate, not compete",
                "stakes": "Company failure and loss of user trust"
            })
            
        elif "evaluate this episode concept" in prompt.lower():
            return json.dumps({
                "scores": {"originality": 8, "character": 9, "drama": 8, "producible": 9, "theme": 9},
                "average": 8.6,
                "improvements": None,
                "proceed": True
            })
            
        elif "story structure" in prompt.lower():
            return json.dumps({
                "act1": {
                    "scenes": [
                        {"location": "Startup Office", "conflict": "Discovery of AI capability"},
                        {"location": "Coffee Shop", "conflict": "Rival's threat"}
                    ]
                },
                "act2": {
                    "scenes": [
                        {"location": "Board Room", "conflict": "Investor pressure"},
                        {"location": "Server Room", "conflict": "Technical crisis"},
                        {"location": "Park", "conflict": "Mentor's warning"}
                    ]
                },
                "act3": {
                    "scenes": [
                        {"location": "Office Night", "conflict": "Final decision"},
                        {"location": "Launch Event", "conflict": "Public revelation"},
                        {"location": "Rooftop", "conflict": "New beginning"}
                    ]
                }
            })
            
        elif "validate this story structure" in prompt.lower():
            return json.dumps({
                "coherence_score": 8,
                "issues": [],
                "suggestions": [],
                "approved": True
            })
            
        elif "expand scene" in prompt.lower():
            return json.dumps({
                "description": "The cramped startup office buzzes with nervous energy as Alex stares at the screen showing the AI's unprecedented capabilities.",
                "characters": ["Alex Chen", "Sam Rodriguez"],
                "motivations": {"Alex": "Save the company", "Sam": "Protect Alex from themselves"},
                "dialogue_beats": ["Discovery revelation", "Ethical concern", "Time pressure"],
                "visual_elements": ["Cluttered desks", "Multiple monitors", "Dawn light"],
                "dramatic_element": "revelation"
            })
            
        elif "natural dialogue" in prompt.lower():
            return json.dumps([
                {"speaker": "Alex", "line": "This changes everything.", "subtext": "Both excited and terrified"},
                {"speaker": "Sam", "line": "Or it changes nothing if you don't use it.", "subtext": "Testing Alex's ethics"},
                {"speaker": "Alex", "line": "We're 48 hours from bankruptcy.", "subtext": "Justifying the choice"},
                {"speaker": "Sam", "line": "Some things are worth more than money.", "subtext": "Disappointed"}
            ])
            
        elif "polish this dialogue" in prompt.lower():
            return json.dumps([
                {"speaker": "Alex", "line": "This changes everything.", "subtext": "Both excited and terrified", "ENHANCED": True},
                {"speaker": "Sam", "line": "Does it? Or does it change you?", "subtext": "Challenging directly", "ENHANCED": True},
                {"speaker": "Alex", "line": "48 hours, Sam. That's all we have.", "subtext": "Desperate", "ENHANCED": True},
                {"speaker": "Sam", "line": "Then make them count.", "subtext": "Final wisdom", "ENHANCED": True}
            ])
            
        elif "enhance dramatic impact" in prompt.lower():
            return json.dumps({
                "description": "The cramped startup office buzzes with nervous energy",
                "dialogue": [{"speaker": "Alex", "line": "This changes everything."}],
                "drama_elements": ["revelation", "ticking_clock"],
                "enhanced": True
            })
            
        elif "final coherence check" in prompt.lower():
            return json.dumps({
                "title": "The Algorithm's Edge",
                "complete": True,
                "runtime_estimate": "22 minutes",
                "coherence_verified": True,
                "scenes": []  # Would include full scenes
            })
            
        return "{}"  # Default empty response
        
    def _get_character_voices(self) -> str:
        """Get character voice descriptions"""
        return """
        Alex Chen: Direct, technical, occasionally sarcastic under pressure
        Sam Rodriguez: Thoughtful, uses metaphors, asks probing questions
        Jordan Park: Confident, slightly condescending, precise language
        """
        
    def _get_fallback_concept(self) -> Dict:
        """Fallback concept if generation fails"""
        return {
            "logline": "A founder faces an impossible choice between success and ethics",
            "central_conflict": "Save company vs preserve integrity",
            "b_plot": "Team loyalty tested",
            "themes": ["ambition", "ethics"],
            "twist": "Solution comes from unexpected source",
            "stakes": "Everything they've built"
        }

async def main():
    """Demo the direct prompt chain"""
    
    print("🎬 Direct Prompt Chain Demo")
    print("=" * 60)
    
    # Initialize chain
    chain = DirectPromptChain()
    
    # Set initial context
    context = {
        'title': 'The Algorithm\'s Edge',
        'themes': ['innovation vs ethics', 'human connection in tech'],
        'plot_pattern': 'ABABC'
    }
    
    # Run the chain
    results = await chain.run_chain(context)
    
    print("\n" + "=" * 60)
    print("📺 Episode Generation Complete!")
    print("=" * 60)
    
    # Save results
    output_file = "direct_chain_output.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✅ Results saved to {output_file}")
    
    # Display summary
    if 'final_episode' in results:
        episode = results['final_episode']
        print(f"\nEpisode: {episode.get('title', 'Untitled')}")
        print(f"Themes: {', '.join(episode.get('themes', []))}")
        print(f"Scenes: {len(episode.get('scenes', []))}")
        print(f"Runtime: {episode.get('runtime_estimate', '~22 minutes')}")

if __name__ == "__main__":
    asyncio.run(main())