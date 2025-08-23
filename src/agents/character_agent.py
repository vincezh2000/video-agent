"""Character agent implementation for multi-agent simulation."""

import random
import uuid
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json
from loguru import logger


class AgentState(Enum):
    """Possible states for an agent."""
    IDLE = "idle"
    PERCEIVING = "perceiving"
    DECIDING = "deciding"
    ACTING = "acting"
    REFLECTING = "reflecting"


class PersonalityTrait(Enum):
    """Core personality traits (Big Five model)."""
    OPENNESS = "openness"
    CONSCIENTIOUSNESS = "conscientiousness"
    EXTRAVERSION = "extraversion"
    AGREEABLENESS = "agreeableness"
    NEUROTICISM = "neuroticism"


@dataclass
class Memory:
    """A single memory entry."""
    id: str
    timestamp: datetime
    type: str  # "event", "interaction", "emotion", "reflection"
    content: str
    participants: List[str]
    location: str
    emotional_valence: float  # -1.0 to 1.0
    importance: float  # 0.0 to 1.0
    tags: List[str] = field(default_factory=list)
    
    def decay(self, current_time: datetime, decay_rate: float = 0.01) -> float:
        """Calculate memory strength with decay over time.
        
        Args:
            current_time: Current simulation time
            decay_rate: Rate of memory decay
            
        Returns:
            Memory strength (0.0 to 1.0)
        """
        time_delta = (current_time - self.timestamp).total_seconds() / 3600  # Hours
        decay_factor = max(0, 1.0 - (decay_rate * time_delta))
        return self.importance * decay_factor


@dataclass
class Goal:
    """Character goal or objective."""
    id: str
    description: str
    priority: float  # 0.0 to 1.0
    deadline: Optional[datetime]
    prerequisites: List[str] = field(default_factory=list)
    progress: float = 0.0
    completed: bool = False
    
    def is_urgent(self, current_time: datetime) -> bool:
        """Check if goal is urgent based on deadline."""
        if not self.deadline:
            return False
        time_remaining = (self.deadline - current_time).total_seconds() / 3600
        return time_remaining < 24  # Urgent if less than 24 hours


@dataclass
class Relationship:
    """Relationship with another character."""
    character_id: str
    character_name: str
    affinity: float  # -1.0 to 1.0
    trust: float  # 0.0 to 1.0
    history: List[str] = field(default_factory=list)
    last_interaction: Optional[datetime] = None
    relationship_type: str = "acquaintance"  # friend, rival, romantic, family, etc.


class CharacterAgent:
    """An autonomous character agent with personality, memory, and decision-making."""
    
    def __init__(
        self,
        name: str,
        backstory: str,
        personality: Dict[str, float],
        location: str = "unknown",
        age: Optional[int] = None,
        occupation: Optional[str] = None
    ):
        """Initialize a character agent.
        
        Args:
            name: Character name
            backstory: Character backstory
            personality: Personality traits (0.0 to 1.0 for each Big Five trait)
            location: Initial location
            age: Character age
            occupation: Character occupation
        """
        self.id = str(uuid.uuid4())
        self.name = name
        self.backstory = backstory
        self.personality = self._validate_personality(personality)
        self.location = location
        self.age = age
        self.occupation = occupation
        
        # State management
        self.state = AgentState.IDLE
        self.current_action = None
        self.emotional_state = {
            "happiness": 0.5,
            "sadness": 0.0,
            "anger": 0.0,
            "fear": 0.0,
            "surprise": 0.0,
            "disgust": 0.0
        }
        
        # Memory system
        self.memories: List[Memory] = []
        self.working_memory: List[Memory] = []  # Recent, relevant memories
        self.memory_capacity = 1000
        
        # Goals and motivations
        self.goals: List[Goal] = []
        self.current_goal: Optional[Goal] = None
        
        # Relationships
        self.relationships: Dict[str, Relationship] = {}
        
        # Decision-making
        self.action_history: List[Dict] = []
        self.decision_threshold = 0.6
        
        # Reverie system (reflection patterns)
        self.reflection_patterns: List[str] = []
        self.last_reflection: Optional[datetime] = None
        
        logger.info(f"Created agent: {name} with personality {personality}")
        
    def _validate_personality(self, personality: Dict[str, float]) -> Dict[str, float]:
        """Validate and normalize personality traits.
        
        Args:
            personality: Raw personality values
            
        Returns:
            Validated personality dict
        """
        validated = {}
        for trait in PersonalityTrait:
            value = personality.get(trait.value, 0.5)
            validated[trait.value] = max(0.0, min(1.0, value))
        return validated
        
    def perceive(self, environment: Dict[str, Any], current_time: datetime) -> List[str]:
        """Perceive the environment and other agents.
        
        Args:
            environment: Environment state including other agents, objects, events
            current_time: Current simulation time
            
        Returns:
            List of observations
        """
        self.state = AgentState.PERCEIVING
        observations = []
        
        # Perceive other agents in same location
        agents_here = environment.get("agents_at_location", {}).get(self.location, [])
        for agent in agents_here:
            if agent["id"] != self.id:
                observations.append(f"Sees {agent['name']} who appears {agent.get('emotional_state', 'neutral')}")
                
        # Perceive environmental events
        events = environment.get("recent_events", [])
        for event in events:
            if self._is_relevant_event(event):
                observations.append(event["description"])
                
        # Perceive objects and context
        location_details = environment.get("locations", {}).get(self.location, {})
        if location_details:
            observations.append(f"At {self.location}: {location_details.get('description', '')}")
            
        # Store observations as memories
        for obs in observations:
            self._create_memory(
                type="event",
                content=obs,
                timestamp=current_time,
                importance=self._calculate_importance(obs)
            )
            
        return observations
        
    def decide(self, observations: List[str], current_time: datetime) -> Dict[str, Any]:
        """Make a decision based on observations and internal state.
        
        Args:
            observations: Current observations
            current_time: Current simulation time
            
        Returns:
            Decision including action type and parameters
        """
        self.state = AgentState.DECIDING
        
        # Retrieve relevant memories
        self._update_working_memory(observations, current_time)
        
        # Evaluate current goals
        self._evaluate_goals(current_time)
        
        # Generate action options
        options = self._generate_action_options(observations)
        
        # Score each option based on personality, goals, and emotions
        best_action = None
        best_score = -float('inf')
        
        for option in options:
            score = self._score_action(option, current_time)
            if score > best_score:
                best_score = score
                best_action = option
                
        # Check if action meets threshold
        if best_score < self.decision_threshold:
            best_action = {"type": "idle", "description": "Contemplates quietly"}
            
        self.current_action = best_action
        return best_action
        
    def act(self, decision: Dict[str, Any], environment: Dict[str, Any], current_time: datetime) -> Dict[str, Any]:
        """Execute the decided action.
        
        Args:
            decision: Decision from decide phase
            environment: Current environment state
            current_time: Current simulation time
            
        Returns:
            Action result including effects and output
        """
        self.state = AgentState.ACTING
        
        action_type = decision.get("type", "idle")
        result = {
            "agent_id": self.id,
            "agent_name": self.name,
            "action_type": action_type,
            "timestamp": current_time.isoformat(),
            "location": self.location,
            "success": True
        }
        
        if action_type == "speak":
            result["dialogue"] = self._generate_dialogue(decision, environment)
            result["target"] = decision.get("target")
            self._update_emotional_state("expression", 0.1)
            
        elif action_type == "move":
            new_location = decision.get("destination")
            if new_location and new_location in environment.get("locations", {}):
                self.location = new_location
                result["new_location"] = new_location
                
        elif action_type == "interact":
            target_id = decision.get("target_id")
            interaction_type = decision.get("interaction_type")
            result["interaction"] = {
                "target": target_id,
                "type": interaction_type,
                "description": decision.get("description")
            }
            self._update_relationship(target_id, interaction_type, current_time)
            
        elif action_type == "reflect":
            reflection = self._generate_reflection(current_time)
            result["reflection"] = reflection
            self.state = AgentState.REFLECTING
            
        # Store action in history
        self.action_history.append(result)
        
        # Create memory of own action
        self._create_memory(
            type="interaction",
            content=f"I {decision.get('description', 'acted')}",
            timestamp=current_time,
            importance=0.5
        )
        
        return result
        
    def reflect(self, current_time: datetime, force: bool = False) -> Optional[Dict[str, Any]]:
        """Reflect on memories and experiences (Reverie system).
        
        Args:
            current_time: Current simulation time
            force: Force reflection even if not enough time has passed
            
        Returns:
            Reflection insights if generated
        """
        # Check if it's time to reflect
        if not force and self.last_reflection:
            time_since_reflection = (current_time - self.last_reflection).total_seconds() / 3600
            if time_since_reflection < 3:  # Reflect every 3 hours minimum
                return None
                
        self.state = AgentState.REFLECTING
        
        # Analyze recent memories for patterns
        recent_memories = [m for m in self.memories[-50:]]  # Last 50 memories
        
        # Identify emotional patterns
        emotional_pattern = self._analyze_emotional_pattern(recent_memories)
        
        # Identify social patterns
        social_pattern = self._analyze_social_pattern(recent_memories)
        
        # Identify goal progress
        goal_pattern = self._analyze_goal_progress()
        
        # Generate insights
        insights = {
            "timestamp": current_time.isoformat(),
            "emotional_insight": emotional_pattern,
            "social_insight": social_pattern,
            "goal_insight": goal_pattern,
            "overall_reflection": self._synthesize_reflection(emotional_pattern, social_pattern, goal_pattern)
        }
        
        # Store as special reflection memory
        self._create_memory(
            type="reflection",
            content=insights["overall_reflection"],
            timestamp=current_time,
            importance=0.8
        )
        
        self.reflection_patterns.append(insights["overall_reflection"])
        self.last_reflection = current_time
        self.state = AgentState.IDLE
        
        return insights
        
    def _generate_action_options(self, observations: List[str]) -> List[Dict[str, Any]]:
        """Generate possible actions based on current context."""
        options = []
        
        # Always can idle
        options.append({
            "type": "idle",
            "description": "Wait and observe",
            "energy_cost": 0.0
        })
        
        # Speech options based on personality
        if self.personality["extraversion"] > 0.5:
            options.append({
                "type": "speak",
                "description": "Start a conversation",
                "energy_cost": 0.2
            })
            
        # Movement options
        options.append({
            "type": "move",
            "description": "Go to a different location",
            "destination": "random",
            "energy_cost": 0.3
        })
        
        # Interaction options if others are present
        if any("Sees" in obs for obs in observations):
            options.append({
                "type": "interact",
                "description": "Interact with someone nearby",
                "interaction_type": "friendly" if self.personality["agreeableness"] > 0.5 else "neutral",
                "energy_cost": 0.4
            })
            
        # Reflection option if enough memories
        if len(self.memories) > 20:
            options.append({
                "type": "reflect",
                "description": "Reflect on recent experiences",
                "energy_cost": 0.1
            })
            
        return options
        
    def _score_action(self, action: Dict[str, Any], current_time: datetime) -> float:
        """Score an action based on personality, goals, and state."""
        score = 0.0
        
        # Personality influence
        if action["type"] == "speak" or action["type"] == "interact":
            score += self.personality["extraversion"] * 0.3
            score += self.personality["agreeableness"] * 0.2
        elif action["type"] == "reflect":
            score += self.personality["openness"] * 0.3
            score += (1 - self.personality["extraversion"]) * 0.2
            
        # Goal alignment
        if self.current_goal:
            # Simple heuristic: active actions score higher when pursuing goals
            if action["type"] != "idle":
                score += self.current_goal.priority * 0.4
                
        # Emotional state influence
        if self.emotional_state["fear"] > 0.5 and action["type"] == "move":
            score += 0.3  # Prefer escape when afraid
        elif self.emotional_state["happiness"] > 0.6 and action["type"] == "interact":
            score += 0.2  # More social when happy
            
        # Energy consideration (conscientiousness)
        energy_cost = action.get("energy_cost", 0.0)
        score -= energy_cost * self.personality["conscientiousness"] * 0.1
        
        # Add randomness for variety
        score += random.uniform(-0.1, 0.1)
        
        return score
        
    def _create_memory(
        self,
        type: str,
        content: str,
        timestamp: datetime,
        importance: float,
        participants: List[str] = None
    ):
        """Create and store a new memory."""
        memory = Memory(
            id=str(uuid.uuid4()),
            timestamp=timestamp,
            type=type,
            content=content,
            participants=participants or [],
            location=self.location,
            emotional_valence=self._calculate_emotional_valence(),
            importance=importance
        )
        
        self.memories.append(memory)
        
        # Manage memory capacity
        if len(self.memories) > self.memory_capacity:
            # Remove least important old memories
            self.memories.sort(key=lambda m: m.importance * m.decay(timestamp))
            self.memories = self.memories[-self.memory_capacity:]
            
    def _update_working_memory(self, observations: List[str], current_time: datetime):
        """Update working memory with relevant recent memories."""
        self.working_memory = []
        
        # Add memories related to current observations
        observation_keywords = set()
        for obs in observations:
            observation_keywords.update(obs.lower().split())
            
        for memory in self.memories[-100:]:  # Check last 100 memories
            memory_keywords = set(memory.content.lower().split())
            if observation_keywords & memory_keywords:  # Intersection
                self.working_memory.append(memory)
                
        # Sort by relevance (importance * recency)
        self.working_memory.sort(
            key=lambda m: m.importance * m.decay(current_time),
            reverse=True
        )
        self.working_memory = self.working_memory[:20]  # Keep top 20
        
    def _evaluate_goals(self, current_time: datetime):
        """Evaluate and prioritize goals."""
        if not self.goals:
            return
            
        # Update goal priorities based on urgency and progress
        for goal in self.goals:
            if goal.completed:
                continue
                
            # Increase priority for urgent goals
            if goal.is_urgent(current_time):
                goal.priority = min(1.0, goal.priority * 1.2)
                
        # Select highest priority incomplete goal
        incomplete_goals = [g for g in self.goals if not g.completed]
        if incomplete_goals:
            self.current_goal = max(incomplete_goals, key=lambda g: g.priority)
            
    def _generate_dialogue(self, decision: Dict[str, Any], environment: Dict[str, Any]) -> str:
        """Generate contextual dialogue based on personality and state."""
        dialogue_templates = {
            "greeting": [
                "Hello there!",
                "Hi, how are you?",
                "Good to see you.",
                "Hey."
            ],
            "happy": [
                "This is wonderful!",
                "I'm feeling great about this.",
                "Things are looking up!",
                "Couldn't be better!"
            ],
            "sad": [
                "I'm not feeling great...",
                "This is difficult.",
                "I wish things were different.",
                "It's been tough."
            ],
            "angry": [
                "This is unacceptable!",
                "I can't believe this.",
                "That's not right!",
                "I'm frustrated."
            ]
        }
        
        # Determine dialogue type based on emotional state
        dominant_emotion = max(self.emotional_state.items(), key=lambda x: x[1])[0]
        
        if dominant_emotion == "happiness":
            dialogue_type = "happy"
        elif dominant_emotion == "sadness":
            dialogue_type = "sad"
        elif dominant_emotion == "anger":
            dialogue_type = "angry"
        else:
            dialogue_type = "greeting"
            
        # Select dialogue based on personality
        options = dialogue_templates.get(dialogue_type, ["..."])
        
        # Modify based on personality
        if self.personality["extraversion"] < 0.3:
            # Introverted: shorter responses
            return random.choice([opt for opt in options if len(opt) < 20] or options[:1])
        elif self.personality["extraversion"] > 0.7:
            # Extraverted: longer responses
            return random.choice([opt for opt in options if len(opt) > 15] or options[-1:])
        else:
            return random.choice(options)
            
    def _update_emotional_state(self, trigger: str, intensity: float):
        """Update emotional state based on triggers."""
        emotion_triggers = {
            "success": {"happiness": 0.3, "surprise": 0.1},
            "failure": {"sadness": 0.2, "anger": 0.1},
            "threat": {"fear": 0.4, "anger": 0.1},
            "loss": {"sadness": 0.4},
            "expression": {"happiness": 0.1}  # Speaking makes most people happier
        }
        
        changes = emotion_triggers.get(trigger, {})
        for emotion, change in changes.items():
            self.emotional_state[emotion] = min(1.0, self.emotional_state[emotion] + change * intensity)
            
        # Decay other emotions slightly
        for emotion in self.emotional_state:
            if emotion not in changes:
                self.emotional_state[emotion] *= 0.95
                
    def _update_relationship(self, target_id: str, interaction_type: str, current_time: datetime):
        """Update relationship based on interaction."""
        if target_id not in self.relationships:
            self.relationships[target_id] = Relationship(
                character_id=target_id,
                character_name=f"Character_{target_id[:8]}",
                affinity=0.0,
                trust=0.5
            )
            
        rel = self.relationships[target_id]
        
        # Update based on interaction type
        if interaction_type == "friendly":
            rel.affinity = min(1.0, rel.affinity + 0.1)
            rel.trust = min(1.0, rel.trust + 0.05)
        elif interaction_type == "hostile":
            rel.affinity = max(-1.0, rel.affinity - 0.2)
            rel.trust = max(0.0, rel.trust - 0.1)
        elif interaction_type == "collaborative":
            rel.affinity = min(1.0, rel.affinity + 0.15)
            rel.trust = min(1.0, rel.trust + 0.1)
            
        rel.last_interaction = current_time
        rel.history.append(f"{current_time.isoformat()}: {interaction_type} interaction")
        
    def _calculate_importance(self, content: str) -> float:
        """Calculate importance of an observation or event."""
        # Simple heuristic based on keywords
        important_keywords = ["danger", "love", "death", "success", "failure", "discovery"]
        importance = 0.3  # Base importance
        
        content_lower = content.lower()
        for keyword in important_keywords:
            if keyword in content_lower:
                importance += 0.2
                
        # Cap at 1.0
        return min(1.0, importance)
        
    def _calculate_emotional_valence(self) -> float:
        """Calculate current emotional valence (-1 to 1)."""
        positive = self.emotional_state["happiness"] + self.emotional_state["surprise"] * 0.5
        negative = self.emotional_state["sadness"] + self.emotional_state["anger"] + \
                  self.emotional_state["fear"] + self.emotional_state["disgust"]
        
        return max(-1.0, min(1.0, positive - negative))
        
    def _generate_reflection(self, current_time: datetime) -> str:
        """Generate a reflection based on recent experiences."""
        recent_memories = self.memories[-20:]
        
        # Analyze patterns
        common_locations = {}
        common_interactions = {}
        emotional_trajectory = []
        
        for memory in recent_memories:
            common_locations[memory.location] = common_locations.get(memory.location, 0) + 1
            for participant in memory.participants:
                common_interactions[participant] = common_interactions.get(participant, 0) + 1
            emotional_trajectory.append(memory.emotional_valence)
            
        # Generate reflection text
        reflection_parts = []
        
        if common_locations:
            most_common_location = max(common_locations.items(), key=lambda x: x[1])[0]
            reflection_parts.append(f"I've been spending a lot of time at {most_common_location}")
            
        if emotional_trajectory:
            avg_valence = sum(emotional_trajectory) / len(emotional_trajectory)
            if avg_valence > 0.3:
                reflection_parts.append("Things have been going well lately")
            elif avg_valence < -0.3:
                reflection_parts.append("It's been a difficult period")
            else:
                reflection_parts.append("Life has had its ups and downs")
                
        if common_interactions:
            most_common_person = max(common_interactions.items(), key=lambda x: x[1])[0]
            reflection_parts.append(f"My interactions with {most_common_person} have been significant")
            
        return ". ".join(reflection_parts) if reflection_parts else "Time passes quietly"
        
    def _analyze_emotional_pattern(self, memories: List[Memory]) -> str:
        """Analyze emotional patterns in memories."""
        if not memories:
            return "No clear emotional pattern"
            
        valences = [m.emotional_valence for m in memories]
        avg_valence = sum(valences) / len(valences)
        
        if avg_valence > 0.5:
            return "I've been predominantly happy and content"
        elif avg_valence > 0:
            return "I've maintained a generally positive outlook"
        elif avg_valence > -0.5:
            return "I've experienced mixed emotions"
        else:
            return "I've been struggling with negative emotions"
            
    def _analyze_social_pattern(self, memories: List[Memory]) -> str:
        """Analyze social patterns in memories."""
        interactions = [m for m in memories if m.type == "interaction"]
        
        if not interactions:
            return "I've been mostly alone"
            
        unique_people = set()
        for memory in interactions:
            unique_people.update(memory.participants)
            
        if len(unique_people) > 5:
            return "I've been very social, interacting with many people"
        elif len(unique_people) > 2:
            return f"I've been maintaining relationships with a small group"
        else:
            return "I've been focused on one or two key relationships"
            
    def _analyze_goal_progress(self) -> str:
        """Analyze progress toward goals."""
        if not self.goals:
            return "I'm living without clear goals"
            
        completed = sum(1 for g in self.goals if g.completed)
        total = len(self.goals)
        
        if completed == total:
            return "I've accomplished all my goals"
        elif completed > total / 2:
            return "I'm making good progress on my goals"
        elif completed > 0:
            return "I've made some progress, but have more work to do"
        else:
            return "I haven't made progress on my goals"
            
    def _synthesize_reflection(self, emotional: str, social: str, goal: str) -> str:
        """Synthesize patterns into overall reflection."""
        return f"{emotional}. {social}. {goal}. " \
               f"As someone who values {self._get_top_personality_trait()}, " \
               f"I need to {self._get_next_focus()}."
               
    def _get_top_personality_trait(self) -> str:
        """Get the dominant personality trait."""
        trait_descriptions = {
            "openness": "new experiences and ideas",
            "conscientiousness": "order and achievement",
            "extraversion": "social connection",
            "agreeableness": "harmony and cooperation",
            "neuroticism": "emotional intensity"
        }
        
        top_trait = max(self.personality.items(), key=lambda x: x[1])[0]
        return trait_descriptions.get(top_trait, "balance")
        
    def _get_next_focus(self) -> str:
        """Determine what to focus on next."""
        if self.current_goal and self.current_goal.progress < 0.5:
            return f"focus on {self.current_goal.description}"
        elif self.emotional_state["sadness"] > 0.5:
            return "find ways to improve my mood"
        elif len(self.relationships) < 2:
            return "build more connections"
        else:
            return "maintain my current path"
            
    def to_dict(self) -> Dict[str, Any]:
        """Convert agent to dictionary representation."""
        return {
            "id": self.id,
            "name": self.name,
            "backstory": self.backstory,
            "personality": self.personality,
            "location": self.location,
            "age": self.age,
            "occupation": self.occupation,
            "state": self.state.value,
            "emotional_state": self.emotional_state,
            "current_goal": self.current_goal.description if self.current_goal else None,
            "relationships": {
                k: {"affinity": v.affinity, "trust": v.trust}
                for k, v in self.relationships.items()
            },
            "memory_count": len(self.memories),
            "recent_action": self.action_history[-1] if self.action_history else None
        }