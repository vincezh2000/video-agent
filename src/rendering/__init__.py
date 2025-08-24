"""Rendering module for audio and visual output."""

from .audio_renderer import (
    AudioRenderer,
    VoiceProfile
)

# Import episode audio renderer if available
try:
    from .episode_audio_renderer import (
        EpisodeAudioRenderer,
        render_episode_with_celebrities
    )
    __all__ = [
        "AudioRenderer",
        "VoiceProfile",
        "EpisodeAudioRenderer",
        "render_episode_with_celebrities"
    ]
except ImportError:
    __all__ = [
        "AudioRenderer",
        "VoiceProfile"
    ]