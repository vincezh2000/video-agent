#!/usr/bin/env python3
"""Run a test simulation with sample agents."""

import asyncio
import argparse
import json
from datetime import datetime
from loguru import logger
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.agents import CharacterAgent
from src.agents.character_agent import Goal
from src.simulation import SimulationEngine


def create_test_agents():
    """Create test agents with diverse personalities."""
    agents = []
    
    # Agent 1: The Ambitious CEO
    alex = CharacterAgent(
        name="Alex Chen",
        backstory="Former Google engineer who left to found an AI startup. Brilliant but sometimes ruthless in pursuit of success.",
        personality={
            "openness": 0.9,
            "conscientiousness": 0.8,
            "extraversion": 0.7,
            "agreeableness": 0.4,
            "neuroticism": 0.6
        },
        age=32,
        occupation="CEO & CTO"
    )
    agents.append(alex)
    
    # Agent 2: The Cautious Ethicist
    jordan = CharacterAgent(
        name="Jordan Kim",
        backstory="Philosophy PhD who joined tech to ensure AI is developed ethically. Often clashes with profit-driven decisions.",
        personality={
            "openness": 0.8,
            "conscientiousness": 0.9,
            "extraversion": 0.4,
            "agreeableness": 0.8,
            "neuroticism": 0.5
        },
        age=29,
        occupation="Head of Ethics"
    )
    agents.append(jordan)
    
    # Agent 3: The Ambitious Investor
    marcus = CharacterAgent(
        name="Marcus Webb",
        backstory="Billionaire venture capitalist who made his fortune in early social media. Pressures for aggressive growth.",
        personality={
            "openness": 0.5,
            "conscientiousness": 0.7,
            "extraversion": 0.8,
            "agreeableness": 0.3,
            "neuroticism": 0.4
        },
        age=45,
        occupation="Venture Capitalist"
    )
    agents.append(marcus)
    
    # Agent 4: The Idealistic Engineer
    sam = CharacterAgent(
        name="Sam Rodriguez",
        backstory="Young prodigy engineer who believes AI can solve humanity's problems. Sometimes naive about business realities.",
        personality={
            "openness": 0.95,
            "conscientiousness": 0.6,
            "extraversion": 0.6,
            "agreeableness": 0.7,
            "neuroticism": 0.3
        },
        age=24,
        occupation="Lead Engineer"
    )
    agents.append(sam)
    
    # Agent 5: The Pragmatic COO
    riley = CharacterAgent(
        name="Riley Zhang",
        backstory="Stanford MBA with experience at multiple unicorns. Bridges the gap between technical and business teams.",
        personality={
            "openness": 0.6,
            "conscientiousness": 0.85,
            "extraversion": 0.65,
            "agreeableness": 0.6,
            "neuroticism": 0.4
        },
        age=35,
        occupation="COO"
    )
    agents.append(riley)
    
    return agents


async def simulation_callback(step: int, total: int, events: list):
    """Callback to report simulation progress."""
    if step % 5 == 0:  # Report every 5 steps
        progress = (step / total) * 100
        logger.info(f"Progress: {progress:.1f}% - Step {step}/{total}")
        if events:
            logger.info(f"  Recent events: {len(events)} events occurred")
            for event in events[:2]:  # Show first 2 events
                logger.info(f"    - {event.description}")


async def run_test_simulation(
    num_agents: int = 5,
    duration_hours: float = 3.0,
    output_file: str = "simulation_output.json"
):
    """Run a test simulation.
    
    Args:
        num_agents: Number of agents to simulate
        duration_hours: Duration of simulation in hours
        output_file: File to save results
    """
    logger.info("Initializing simulation engine...")
    
    # Create simulation engine
    engine = SimulationEngine(time_step_minutes=15)
    
    # Create and add agents
    logger.info(f"Creating {num_agents} test agents...")
    agents = create_test_agents()[:num_agents]
    
    for agent in agents:
        engine.add_agent(agent)
        
    # Add some initial goals for agents
    agents[0].goals.append(Goal(
        id="secure_funding",
        description="Secure Series A funding",
        priority=0.9,
        deadline=None
    ))
    
    agents[1].goals.append(Goal(
        id="ethics_framework",
        description="Implement comprehensive AI ethics framework",
        priority=0.8,
        deadline=None
    ))
    
    # Run simulation
    logger.info(f"Starting {duration_hours} hour simulation...")
    start_time = datetime.now()
    
    results = await engine.run_simulation(
        duration_hours=duration_hours,
        callback=simulation_callback
    )
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    logger.info(f"Simulation complete in {duration:.2f} seconds")
    
    # Save results
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    logger.info(f"Results saved to {output_file}")
    
    # Print summary
    summary = results.get("summary", {})
    print("\n=== SIMULATION SUMMARY ===")
    print(f"Total Events: {summary.get('total_events', 0)}")
    print(f"Total Actions: {summary.get('total_actions', 0)}")
    print(f"Average Tension: {summary.get('average_tension', 0):.2f}")
    print(f"Peak Tension: {summary.get('peak_tension', 0):.2f}")
    print(f"Most Active Agent: {summary.get('most_active_agent', 'None')}")
    
    print("\nEvent Distribution:")
    for event_type, count in summary.get('event_distribution', {}).items():
        print(f"  {event_type}: {count}")
        
    print(f"\nAverage Step Duration: {summary.get('average_step_duration', 0):.3f}s")
    
    # Show some interesting events
    if results.get("events"):
        print("\n=== SAMPLE EVENTS ===")
        for event in results["events"][:10]:
            print(f"[{event['type']}] {event['description']}")
            
    # Show narrative arc
    if results.get("dramatic_peaks"):
        print("\n=== DRAMATIC PEAKS ===")
        for peak in results["dramatic_peaks"]:
            print(f"Time: {peak['time']}, Tension: {peak['tension']:.2f}")
            
    return results


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Run multi-agent simulation")
    parser.add_argument(
        "--agents",
        type=int,
        default=5,
        help="Number of agents to simulate (max 5)"
    )
    parser.add_argument(
        "--hours",
        type=float,
        default=3.0,
        help="Duration of simulation in hours"
    )
    parser.add_argument(
        "--timestep",
        type=int,
        default=15,
        help="Minutes per timestep"
    )
    parser.add_argument(
        "--output",
        default="simulation_output.json",
        help="Output file for results"
    )
    
    args = parser.parse_args()
    
    # Configure logging
    logger.add("simulation.log", rotation="10 MB")
    
    # Import Goal here to avoid circular import
    from src.agents import Goal
    
    # Run simulation
    asyncio.run(run_test_simulation(
        num_agents=min(args.agents, 5),
        duration_hours=args.hours,
        output_file=args.output
    ))


if __name__ == "__main__":
    main()