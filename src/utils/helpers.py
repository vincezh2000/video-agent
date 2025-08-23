"""Helper functions for the Showrunner system."""

import json
import yaml
import hashlib
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
from datetime import datetime, timedelta
import re
from loguru import logger


def load_config(config_path: Union[str, Path]) -> Dict[str, Any]:
    """Load configuration from YAML or JSON file.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Configuration dictionary
    """
    config_path = Path(config_path)
    
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
    if config_path.suffix in ['.yaml', '.yml']:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    elif config_path.suffix == '.json':
        with open(config_path, 'r') as f:
            return json.load(f)
    else:
        raise ValueError(f"Unsupported config format: {config_path.suffix}")


def save_json(data: Any, filepath: Union[str, Path], indent: int = 2):
    """Save data to JSON file.
    
    Args:
        data: Data to save
        filepath: Output file path
        indent: JSON indentation
    """
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=indent, default=str)
        
    logger.debug(f"Saved JSON to {filepath}")


def generate_id(prefix: str = "", length: int = 8) -> str:
    """Generate a unique ID.
    
    Args:
        prefix: Optional prefix for the ID
        length: Length of random part
        
    Returns:
        Generated ID
    """
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_part = hashlib.md5(timestamp.encode()).hexdigest()[:length]
    
    if prefix:
        return f"{prefix}_{random_part}"
    return random_part


def format_duration(seconds: float) -> str:
    """Format duration in seconds to readable string.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration string
    """
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"


def estimate_reading_time(text: str, wpm: int = 150) -> float:
    """Estimate reading/speaking time for text.
    
    Args:
        text: Text to estimate
        wpm: Words per minute reading speed
        
    Returns:
        Estimated time in seconds
    """
    words = len(text.split())
    return (words / wpm) * 60


def clean_text(text: str) -> str:
    """Clean text for processing.
    
    Args:
        text: Text to clean
        
    Returns:
        Cleaned text
    """
    # Remove multiple spaces
    text = re.sub(r'\s+', ' ', text)
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    # Fix common punctuation issues
    text = re.sub(r'\s+([,.!?;:])', r'\1', text)
    text = re.sub(r'([,.!?;:])\s*([,.!?;:])', r'\1\2', text)
    
    return text


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate text to maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
        
    truncate_at = max_length - len(suffix)
    
    # Try to truncate at word boundary
    if ' ' in text[:truncate_at]:
        truncate_at = text[:truncate_at].rfind(' ')
        
    return text[:truncate_at] + suffix


def merge_dicts(base: Dict, update: Dict) -> Dict:
    """Deep merge two dictionaries.
    
    Args:
        base: Base dictionary
        update: Dictionary with updates
        
    Returns:
        Merged dictionary
    """
    result = base.copy()
    
    for key, value in update.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = value
            
    return result


def calculate_tension_curve(
    events: List[Dict[str, Any]],
    window_size: int = 5
) -> List[float]:
    """Calculate narrative tension curve from events.
    
    Args:
        events: List of events with impact values
        window_size: Rolling window size
        
    Returns:
        List of tension values
    """
    if not events:
        return []
        
    tensions = []
    
    for i in range(len(events)):
        window_start = max(0, i - window_size // 2)
        window_end = min(len(events), i + window_size // 2 + 1)
        
        window_events = events[window_start:window_end]
        avg_impact = sum(e.get("impact", 0.5) for e in window_events) / len(window_events)
        
        tensions.append(avg_impact)
        
    return tensions


def validate_episode_structure(episode_data: Dict[str, Any]) -> List[str]:
    """Validate episode structure and return issues.
    
    Args:
        episode_data: Episode data to validate
        
    Returns:
        List of validation issues (empty if valid)
    """
    issues = []
    
    # Check required fields
    required_fields = ["title", "synopsis", "scenes"]
    for field in required_fields:
        if field not in episode_data:
            issues.append(f"Missing required field: {field}")
            
    # Check scenes
    scenes = episode_data.get("scenes", [])
    if not scenes:
        issues.append("Episode has no scenes")
    else:
        for i, scene in enumerate(scenes):
            if "dialogue" not in scene:
                issues.append(f"Scene {i+1} missing dialogue")
            if "location" not in scene:
                issues.append(f"Scene {i+1} missing location")
                
    # Check duration
    total_duration = sum(s.get("duration_seconds", 0) for s in scenes)
    if total_duration < 600:  # Less than 10 minutes
        issues.append(f"Episode too short: {total_duration}s")
    elif total_duration > 2400:  # More than 40 minutes
        issues.append(f"Episode too long: {total_duration}s")
        
    return issues


def extract_characters_from_dialogue(scenes: List[Dict[str, Any]]) -> List[str]:
    """Extract unique character names from dialogue.
    
    Args:
        scenes: List of scenes with dialogue
        
    Returns:
        List of unique character names
    """
    characters = set()
    
    for scene in scenes:
        for dialogue in scene.get("dialogue", []):
            if "character" in dialogue:
                characters.add(dialogue["character"])
                
    return sorted(list(characters))


def create_episode_summary(episode_data: Dict[str, Any]) -> str:
    """Create a summary of an episode.
    
    Args:
        episode_data: Episode data
        
    Returns:
        Summary string
    """
    title = episode_data.get("title", "Untitled")
    synopsis = episode_data.get("synopsis", "No synopsis")
    scenes = episode_data.get("scenes", [])
    
    total_duration = sum(s.get("duration_seconds", 0) for s in scenes)
    characters = extract_characters_from_dialogue(scenes)
    
    summary = f"""
Episode: {title}
Synopsis: {synopsis}

Statistics:
- Scenes: {len(scenes)}
- Duration: {format_duration(total_duration)}
- Characters: {', '.join(characters[:5])}{'...' if len(characters) > 5 else ''}
- Genre: {episode_data.get('genre', 'Unknown')}
- Tone: {episode_data.get('tone', 'Unknown')}
"""
    
    if "dramatic_arc" in episode_data:
        arc = episode_data["dramatic_arc"]
        summary += f"""
Dramatic Arc:
- Average Tension: {arc.get('average_tension', 0):.2f}
- Peaks: {arc.get('num_peaks', 0)}
- Has Climax: {arc.get('has_climax', False)}
"""
    
    return summary.strip()


class ProgressTracker:
    """Track progress for long-running operations."""
    
    def __init__(self, total: int, description: str = "Processing"):
        """Initialize progress tracker.
        
        Args:
            total: Total number of items
            description: Description of operation
        """
        self.total = total
        self.current = 0
        self.description = description
        self.start_time = datetime.now()
        
    def update(self, increment: int = 1, message: Optional[str] = None):
        """Update progress.
        
        Args:
            increment: How much to increment
            message: Optional status message
        """
        self.current += increment
        progress = (self.current / self.total) * 100 if self.total > 0 else 0
        
        elapsed = (datetime.now() - self.start_time).total_seconds()
        if self.current > 0:
            rate = self.current / elapsed
            eta = (self.total - self.current) / rate if rate > 0 else 0
        else:
            eta = 0
            
        status = f"{self.description}: {progress:.1f}% ({self.current}/{self.total})"
        if message:
            status += f" - {message}"
        if eta > 0:
            status += f" - ETA: {format_duration(eta)}"
            
        logger.info(status)
        
    def complete(self):
        """Mark as complete."""
        self.current = self.total
        elapsed = (datetime.now() - self.start_time).total_seconds()
        logger.info(f"{self.description} complete in {format_duration(elapsed)}")


def create_backup(filepath: Union[str, Path]) -> Optional[Path]:
    """Create a backup of a file.
    
    Args:
        filepath: File to backup
        
    Returns:
        Path to backup file or None if file doesn't exist
    """
    filepath = Path(filepath)
    
    if not filepath.exists():
        return None
        
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = filepath.parent / f"{filepath.stem}_backup_{timestamp}{filepath.suffix}"
    
    import shutil
    shutil.copy2(filepath, backup_path)
    
    logger.debug(f"Created backup: {backup_path}")
    return backup_path