"""Simulation engine for multi-agent interactions."""

import asyncio
import random
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import json
from loguru import logger

from src.agents import CharacterAgent, AgentState


@dataclass
class Location:
    """A location in the simulation world."""
    name: str
    description: str
    capacity: int = 10
    location_type: str = "generic"  # office, home, public, etc.
    connected_to: List[str] = field(default_factory=list)
    objects: List[str] = field(default_factory=list)
    current_agents: List[str] = field(default_factory=list)


@dataclass 
class Event:
    """An event in the simulation."""
    timestamp: datetime
    event_type: str
    description: str
    participants: List[str]
    location: str
    impact: float = 0.5  # 0-1 scale of narrative importance
    consequences: List[str] = field(default_factory=list)


@dataclass
class SimulationState:
    """Current state of the simulation."""
    current_time: datetime
    time_step: int
    agents: Dict[str, CharacterAgent]
    locations: Dict[str, Location]
    events: List[Event]
    global_state: Dict[str, Any]
    narrative_tension: float = 0.5
    

class SimulationEngine:
    """Engine for running multi-agent simulations."""
    
    def __init__(
        self,
        world_config: Optional[Dict[str, Any]] = None,
        time_step_minutes: int = 15
    ):
        """Initialize the simulation engine.
        
        Args:
            world_config: Configuration for the simulation world
            time_step_minutes: Minutes per simulation step
        """
        self.time_step_minutes = time_step_minutes
        self.world_config = world_config or self._default_world_config()
        
        # Simulation state
        self.agents: Dict[str, CharacterAgent] = {}
        self.locations: Dict[str, Location] = {}
        self.events: List[Event] = []
        self.current_time = datetime.now()
        self.time_step_count = 0
        
        # Narrative tracking
        self.narrative_tension = 0.5
        self.plot_threads: List[str] = []
        self.dramatic_peaks: List[Tuple[datetime, float]] = []
        
        # Performance tracking
        self.step_durations: List[float] = []
        self.agent_action_counts: Dict[str, int] = {}
        
        # Initialize world
        self._initialize_world()
        
        logger.info(f"Simulation engine initialized with {len(self.locations)} locations")
        
    def _default_world_config(self) -> Dict[str, Any]:
        """Create default world configuration."""
        return {
            "locations": [
                {
                    "name": "Office",
                    "description": "A modern open-plan office with glass walls",
                    "type": "office",
                    "capacity": 20
                },
                {
                    "name": "Conference Room",
                    "description": "A meeting room with a large table and projector",
                    "type": "office",
                    "capacity": 10
                },
                {
                    "name": "Cafeteria", 
                    "description": "A bright cafeteria with coffee and snacks",
                    "type": "public",
                    "capacity": 30
                },
                {
                    "name": "Server Room",
                    "description": "A cold room filled with humming servers",
                    "type": "restricted",
                    "capacity": 5
                }
            ],
            "connections": [
                ("Office", "Conference Room"),
                ("Office", "Cafeteria"),
                ("Conference Room", "Cafeteria"),
                ("Office", "Server Room")
            ],
            "global_rules": [
                "Agents need rest after 8 hours of activity",
                "Conflict increases narrative tension",
                "Collaboration decreases tension but builds relationships"
            ]
        }
        
    def _initialize_world(self):
        """Initialize the simulation world from config."""
        # Create locations
        for loc_config in self.world_config.get("locations", []):
            location = Location(
                name=loc_config["name"],
                description=loc_config["description"],
                capacity=loc_config.get("capacity", 10),
                location_type=loc_config.get("type", "generic")
            )
            self.locations[location.name] = location
            
        # Set up connections
        for conn in self.world_config.get("connections", []):
            if len(conn) == 2 and conn[0] in self.locations and conn[1] in self.locations:
                self.locations[conn[0]].connected_to.append(conn[1])
                self.locations[conn[1]].connected_to.append(conn[0])
                
    def add_agent(self, agent: CharacterAgent, initial_location: Optional[str] = None):
        """Add an agent to the simulation.
        
        Args:
            agent: Character agent to add
            initial_location: Starting location (random if not specified)
        """
        self.agents[agent.id] = agent
        self.agent_action_counts[agent.id] = 0
        
        # Place agent in location
        if initial_location and initial_location in self.locations:
            agent.location = initial_location
        else:
            # Random location
            agent.location = random.choice(list(self.locations.keys()))
            
        self.locations[agent.location].current_agents.append(agent.id)
        
        logger.info(f"Added agent {agent.name} to {agent.location}")
        
    def remove_agent(self, agent_id: str):
        """Remove an agent from the simulation.
        
        Args:
            agent_id: ID of agent to remove
        """
        if agent_id in self.agents:
            agent = self.agents[agent_id]
            
            # Remove from location
            if agent.location in self.locations:
                self.locations[agent.location].current_agents.remove(agent_id)
                
            del self.agents[agent_id]
            logger.info(f"Removed agent {agent.name}")
            
    async def run_simulation(
        self,
        duration_hours: float,
        callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """Run the simulation for a specified duration.
        
        Args:
            duration_hours: How long to run the simulation
            callback: Optional callback for each step
            
        Returns:
            Simulation results and generated data
        """
        logger.info(f"Starting simulation for {duration_hours} hours")
        
        start_time = self.current_time
        end_time = start_time + timedelta(hours=duration_hours)
        total_steps = int(duration_hours * 60 / self.time_step_minutes)
        
        results = {
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "total_steps": total_steps,
            "events": [],
            "agent_trajectories": {agent_id: [] for agent_id in self.agents},
            "narrative_arc": [],
            "dramatic_peaks": []
        }
        
        # Main simulation loop
        for step in range(total_steps):
            step_start = asyncio.get_event_loop().time()
            
            # Advance time
            self.current_time += timedelta(minutes=self.time_step_minutes)
            self.time_step_count += 1
            
            # Run simulation step
            step_events = await self._simulation_step()
            
            # Track results
            results["events"].extend([self._event_to_dict(e) for e in step_events])
            results["narrative_arc"].append({
                "step": step,
                "time": self.current_time.isoformat(),
                "tension": self.narrative_tension
            })
            
            # Track agent states
            for agent_id, agent in self.agents.items():
                results["agent_trajectories"][agent_id].append({
                    "step": step,
                    "location": agent.location,
                    "state": agent.state.value,
                    "emotional_state": agent.emotional_state.copy()
                })
                
            # Check for dramatic peaks
            if self.narrative_tension > 0.8:
                self.dramatic_peaks.append((self.current_time, self.narrative_tension))
                results["dramatic_peaks"].append({
                    "time": self.current_time.isoformat(),
                    "tension": self.narrative_tension
                })
                
            # Callback for progress updates
            if callback:
                await callback(step, total_steps, step_events)
                
            # Track performance
            step_duration = asyncio.get_event_loop().time() - step_start
            self.step_durations.append(step_duration)
            
            # Log progress
            if step % 10 == 0:
                logger.info(f"Simulation step {step}/{total_steps} - Tension: {self.narrative_tension:.2f}")
                
        # Final summary
        results["summary"] = self._generate_summary()
        
        logger.info(f"Simulation complete. Generated {len(results['events'])} events")
        return results
        
    async def _simulation_step(self) -> List[Event]:
        """Execute a single simulation step.
        
        Returns:
            List of events that occurred
        """
        step_events = []
        environment = self._get_environment_state()
        
        # Randomly order agents to avoid bias
        agent_order = list(self.agents.values())
        random.shuffle(agent_order)
        
        # Each agent takes their turn
        for agent in agent_order:
            # Perception phase
            observations = agent.perceive(environment, self.current_time)
            
            # Decision phase
            decision = agent.decide(observations, self.current_time)
            
            # Action phase
            action_result = agent.act(decision, environment, self.current_time)
            
            # Track action
            self.agent_action_counts[agent.id] += 1
            
            # Generate event if action is significant
            if action_result["action_type"] != "idle":
                event = self._create_event_from_action(agent, action_result)
                if event:
                    step_events.append(event)
                    self.events.append(event)
                    
            # Update environment based on action
            self._update_environment(agent, action_result)
            
            # Occasional reflection
            if random.random() < 0.1:  # 10% chance per step
                reflection = agent.reflect(self.current_time)
                if reflection:
                    logger.debug(f"{agent.name} reflects: {reflection.get('overall_reflection')}")
                    
        # Update narrative tension
        self._update_narrative_tension(step_events)
        
        # Inject dramatic events if tension is low
        if self.narrative_tension < 0.3 and random.random() < 0.2:
            dramatic_event = self._inject_dramatic_event()
            if dramatic_event:
                step_events.append(dramatic_event)
                self.events.append(dramatic_event)
                
        return step_events
        
    def _get_environment_state(self) -> Dict[str, Any]:
        """Get current environment state for agent perception."""
        # Group agents by location
        agents_at_location = {}
        for loc_name in self.locations:
            agents_at_location[loc_name] = []
            for agent_id in self.locations[loc_name].current_agents:
                if agent_id in self.agents:
                    agent = self.agents[agent_id]
                    agents_at_location[loc_name].append({
                        "id": agent.id,
                        "name": agent.name,
                        "emotional_state": self._describe_emotional_state(agent.emotional_state)
                    })
                    
        return {
            "agents_at_location": agents_at_location,
            "locations": {name: loc.__dict__ for name, loc in self.locations.items()},
            "recent_events": [self._event_to_dict(e) for e in self.events[-10:]],
            "current_time": self.current_time.isoformat(),
            "narrative_tension": self.narrative_tension
        }
        
    def _create_event_from_action(
        self,
        agent: CharacterAgent,
        action_result: Dict[str, Any]
    ) -> Optional[Event]:
        """Create an event from an agent's action."""
        action_type = action_result.get("action_type")
        
        if action_type == "speak":
            return Event(
                timestamp=self.current_time,
                event_type="dialogue",
                description=f"{agent.name} says: {action_result.get('dialogue', '...')}",
                participants=[agent.id, action_result.get("target", "")],
                location=agent.location,
                impact=0.3
            )
        elif action_type == "move":
            return Event(
                timestamp=self.current_time,
                event_type="movement",
                description=f"{agent.name} moves to {action_result.get('new_location')}",
                participants=[agent.id],
                location=agent.location,
                impact=0.1
            )
        elif action_type == "interact":
            interaction = action_result.get("interaction", {})
            return Event(
                timestamp=self.current_time,
                event_type="interaction",
                description=interaction.get("description", f"{agent.name} interacts"),
                participants=[agent.id, interaction.get("target", "")],
                location=agent.location,
                impact=0.4
            )
        elif action_type == "reflect":
            # Reflections are internal, usually don't create events
            return None
            
        return None
        
    def _update_environment(self, agent: CharacterAgent, action_result: Dict[str, Any]):
        """Update environment based on agent action."""
        action_type = action_result.get("action_type")
        
        if action_type == "move":
            old_location = agent.location
            new_location = action_result.get("new_location")
            
            if new_location and new_location in self.locations:
                # Remove from old location
                if agent.id in self.locations[old_location].current_agents:
                    self.locations[old_location].current_agents.remove(agent.id)
                    
                # Add to new location
                self.locations[new_location].current_agents.append(agent.id)
                agent.location = new_location
                
    def _update_narrative_tension(self, events: List[Event]):
        """Update narrative tension based on events."""
        if not events:
            # Tension naturally decays
            self.narrative_tension *= 0.98
        else:
            # Events increase tension based on impact
            total_impact = sum(e.impact for e in events)
            self.narrative_tension = min(1.0, self.narrative_tension + total_impact * 0.1)
            
        # Clamp between 0 and 1
        self.narrative_tension = max(0.0, min(1.0, self.narrative_tension))
        
    def _inject_dramatic_event(self) -> Optional[Event]:
        """Inject a dramatic event to increase tension."""
        dramatic_templates = [
            {
                "type": "conflict",
                "description": "A heated argument breaks out",
                "impact": 0.7
            },
            {
                "type": "revelation",
                "description": "A secret is revealed",
                "impact": 0.8
            },
            {
                "type": "crisis",
                "description": "An urgent problem arises",
                "impact": 0.9
            },
            {
                "type": "opportunity",
                "description": "An unexpected opportunity appears",
                "impact": 0.6
            }
        ]
        
        template = random.choice(dramatic_templates)
        
        # Select random participants
        if len(self.agents) >= 2:
            participants = random.sample(list(self.agents.keys()), min(2, len(self.agents)))
        else:
            participants = list(self.agents.keys())
            
        # Select location with most agents
        busiest_location = max(
            self.locations.keys(),
            key=lambda loc: len(self.locations[loc].current_agents)
        )
        
        event = Event(
            timestamp=self.current_time,
            event_type=template["type"],
            description=template["description"],
            participants=participants,
            location=busiest_location,
            impact=template["impact"]
        )
        
        logger.info(f"Injected dramatic event: {template['description']}")
        return event
        
    def _describe_emotional_state(self, emotional_state: Dict[str, float]) -> str:
        """Convert emotional state to descriptive string."""
        # Find dominant emotion
        dominant = max(emotional_state.items(), key=lambda x: x[1])
        
        if dominant[1] < 0.3:
            return "neutral"
        elif dominant[0] == "happiness":
            return "happy" if dominant[1] < 0.7 else "joyful"
        elif dominant[0] == "sadness":
            return "sad" if dominant[1] < 0.7 else "depressed"
        elif dominant[0] == "anger":
            return "annoyed" if dominant[1] < 0.7 else "angry"
        elif dominant[0] == "fear":
            return "nervous" if dominant[1] < 0.7 else "terrified"
        else:
            return dominant[0]
            
    def _event_to_dict(self, event: Event) -> Dict[str, Any]:
        """Convert event to dictionary."""
        return {
            "timestamp": event.timestamp.isoformat(),
            "type": event.event_type,
            "description": event.description,
            "participants": event.participants,
            "location": event.location,
            "impact": event.impact,
            "consequences": event.consequences
        }
        
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate simulation summary."""
        total_actions = sum(self.agent_action_counts.values())
        
        # Find most active agent
        if self.agent_action_counts:
            most_active_id = max(self.agent_action_counts.items(), key=lambda x: x[1])[0]
            most_active_name = self.agents[most_active_id].name if most_active_id in self.agents else "Unknown"
        else:
            most_active_name = "None"
            
        # Event type distribution
        event_types = {}
        for event in self.events:
            event_types[event.event_type] = event_types.get(event.event_type, 0) + 1
            
        return {
            "total_events": len(self.events),
            "total_actions": total_actions,
            "average_tension": sum(dp[1] for dp in self.dramatic_peaks) / len(self.dramatic_peaks) if self.dramatic_peaks else 0,
            "peak_tension": max(dp[1] for dp in self.dramatic_peaks) if self.dramatic_peaks else 0,
            "most_active_agent": most_active_name,
            "event_distribution": event_types,
            "average_step_duration": sum(self.step_durations) / len(self.step_durations) if self.step_durations else 0
        }
        
    def get_simulation_data(self) -> Dict[str, Any]:
        """Get current simulation data for LLM processing."""
        return {
            "agents": [agent.to_dict() for agent in self.agents.values()],
            "locations": {name: loc.__dict__ for name, loc in self.locations.items()},
            "recent_events": [self._event_to_dict(e) for e in self.events[-50:]],
            "narrative_tension": self.narrative_tension,
            "plot_threads": self.plot_threads,
            "time": self.current_time.isoformat()
        }
        
    def save_state(self, filepath: str):
        """Save simulation state to file.
        
        Args:
            filepath: Path to save state
        """
        state = {
            "current_time": self.current_time.isoformat(),
            "time_step_count": self.time_step_count,
            "agents": {id: agent.to_dict() for id, agent in self.agents.items()},
            "locations": {name: loc.__dict__ for name, loc in self.locations.items()},
            "events": [self._event_to_dict(e) for e in self.events],
            "narrative_tension": self.narrative_tension,
            "plot_threads": self.plot_threads
        }
        
        with open(filepath, 'w') as f:
            json.dump(state, f, indent=2)
            
        logger.info(f"Saved simulation state to {filepath}")
        
    def load_state(self, filepath: str):
        """Load simulation state from file.
        
        Args:
            filepath: Path to load state from
        """
        with open(filepath, 'r') as f:
            state = json.load(f)
            
        self.current_time = datetime.fromisoformat(state["current_time"])
        self.time_step_count = state["time_step_count"]
        self.narrative_tension = state["narrative_tension"]
        self.plot_threads = state["plot_threads"]
        
        # Note: Full agent restoration would require more complex serialization
        logger.info(f"Loaded simulation state from {filepath}")