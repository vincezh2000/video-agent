"""Voice profiles configuration for celebrity voices."""

from dataclasses import dataclass
from typing import Dict, List, Optional, Callable
from elevenlabs import VoiceSettings


@dataclass
class CelebrityProfile:
    """Profile for a celebrity voice."""
    name: str
    display_name: str
    voice_ids: List[str]  # Multiple voice IDs for variation
    primary_voice_id: str  # Primary voice to use
    voice_settings: VoiceSettings
    text_processor: Optional[Callable[[str], str]] = None
    speaking_patterns: Dict[str, str] = None
    
    def __post_init__(self):
        if self.speaking_patterns is None:
            self.speaking_patterns = {}


def process_elon_text(text: str) -> str:
    """Process text to match Elon Musk's speaking patterns."""
    processed = text
    
    # Add occasional "um" and "uh" for natural hesitation
    words = processed.split()
    if len(words) > 8:
        # Insert hesitation words occasionally
        for i in range(7, len(words), 12):
            if i < len(words):
                words.insert(i, "um,")
    
    # Elon often emphasizes technical terms
    tech_words = {
        "AI": "A.I.",
        "neural": "neural",
        "Mars": "Mars",
        "rocket": "rocket",
        "sustainable": "sustainable",
        "autopilot": "Autopilot",
        "Tesla": "Tesla",
        "SpaceX": "SpaceX"
    }
    
    for old, new in tech_words.items():
        processed = processed.replace(old, new)
    
    # Add slight pauses before important statements
    if "important" in processed.lower() or "critical" in processed.lower():
        processed = processed.replace("important", "... important")
        processed = processed.replace("critical", "... critical")
    
    return processed


def process_trump_text(text: str) -> str:
    """Process text to match Trump's speaking patterns."""
    processed = text
    
    # Add Trump's common phrases and emphasis
    trump_phrases = {
        "great": "tremendous",
        "very good": "fantastic",
        "bad": "terrible, just terrible",
        "believe": "believe me",
    }
    
    # Apply some replacements (not all, to keep it natural)
    for old, new in list(trump_phrases.items())[:2]:  # Only apply first 2
        if old in processed.lower():
            processed = processed.replace(old, new)
    
    # Add emphasis to superlatives
    superlatives = ["best", "worst", "greatest", "tremendous", "fantastic", "perfect"]
    for word in superlatives:
        if word in processed.lower():
            # Add slight pause before superlatives
            processed = processed.replace(word, f"... {word}")
            break  # Only emphasize one per text
    
    # Add "believe me" occasionally at the end
    if len(processed.split()) > 10 and not processed.endswith(("!", "?", "...")):
        processed += ", believe me."
    
    return processed


# Celebrity voice profiles configuration
CELEBRITY_PROFILES = {
    "elon_musk": CelebrityProfile(
        name="elon_musk",
        display_name="Elon Musk (Custom)",
        voice_ids=[
            "rJ4KGss9TSKfyhkSuCRh",  # Custom Elon Musk voice - working
        ],
        primary_voice_id="rJ4KGss9TSKfyhkSuCRh",
        voice_settings=VoiceSettings(
            stability=0.85,       # Deep, stable voice as default
            similarity_boost=1.0, # Maximum similarity for rich tone
            style=0.0,            # Minimal variation for deep, magnetic quality
            use_speaker_boost=True
        ),
        text_processor=process_elon_text,
        speaking_patterns={
            "hesitation": ["um", "uh", "well"],
            "emphasis": ["obviously", "clearly", "fundamentally"],
            "technical": ["neural network", "artificial intelligence", "sustainable energy"]
        }
    ),
    
    "trump": CelebrityProfile(
        name="trump",
        display_name="Donald Trump", 
        voice_ids=[
            "VR6AewLTigWG4xSOukaG",  # Josh - deeper voice
            "2EiwWnXFnvU5JabPnv8n",  # Clyde - alternative
            "onwK4e9ZLuTAKqWW03F9",  # Daniel - backup
        ],
        primary_voice_id="VR6AewLTigWG4xSOukaG",
        voice_settings=VoiceSettings(
            stability=0.6,        # More stable, confident delivery
            similarity_boost=0.9,  # Very high similarity
            style=0.5,            # More expressive
            use_speaker_boost=True
        ),
        text_processor=process_trump_text,
        speaking_patterns={
            "superlatives": ["tremendous", "fantastic", "incredible", "perfect"],
            "catchphrases": ["believe me", "let me tell you", "nobody knows more than me"],
            "emphasis": ["very", "so", "totally"]
        }
    ),
    
    # Additional profiles can be added here
    "joe_biden": CelebrityProfile(
        name="joe_biden",
        display_name="Joe Biden",
        voice_ids=[
            "AZnzlk1XvdvUeBnXmlld",  # Domi - softer voice
            "EXAVITQu4vr4xnSDxMaL",  # Bella - alternative
        ],
        primary_voice_id="AZnzlk1XvdvUeBnXmlld",
        voice_settings=VoiceSettings(
            stability=0.5,
            similarity_boost=0.7,
            style=0.2,
            use_speaker_boost=True
        ),
        speaking_patterns={
            "phrases": ["folks", "come on", "here's the deal"],
            "emphasis": ["important", "critical", "fundamental"]
        }
    ),
    
    "obama": CelebrityProfile(
        name="obama",
        display_name="Barack Obama",
        voice_ids=[
            "29vD33N1CtxCmqQRPOHJ",  # Drew - smooth delivery
            "21m00Tcm4TlvDq8ikWAM",  # Rachel - alternative
        ],
        primary_voice_id="29vD33N1CtxCmqQRPOHJ", 
        voice_settings=VoiceSettings(
            stability=0.7,        # Very stable, presidential
            similarity_boost=0.8,
            style=0.4,            # Moderate style variation
            use_speaker_boost=True
        ),
        speaking_patterns={
            "pauses": ["let me be clear", "now", "look"],
            "emphasis": ["folks", "America", "together"]
        }
    )
}


def get_profile(celebrity: str) -> Optional[CelebrityProfile]:
    """Get celebrity profile by name.
    
    Args:
        celebrity: Celebrity name
        
    Returns:
        Celebrity profile or None if not found
    """
    return CELEBRITY_PROFILES.get(celebrity.lower())


def list_celebrities() -> List[str]:
    """List all available celebrities.
    
    Returns:
        List of celebrity names
    """
    return list(CELEBRITY_PROFILES.keys())


def get_display_names() -> Dict[str, str]:
    """Get mapping of celebrity names to display names.
    
    Returns:
        Dictionary mapping names to display names
    """
    return {name: profile.display_name for name, profile in CELEBRITY_PROFILES.items()}