"""peasy-video — Video processing made easy, powered by moviepy.

Trim, resize, extract audio, generate thumbnails, convert to GIF, and more.
Requires ffmpeg installed on the system.
"""

from __future__ import annotations

from peasy_video.engine import (
    ThumbnailResult,
    VideoInfo,
    VideoInput,
    concatenate,
    extract_audio,
    gif_to_video,
    info,
    resize,
    reverse_video,
    rotate,
    speed,
    strip_audio,
    thumbnail,
    thumbnails,
    trim,
    video_to_gif,
)

__version__ = "0.1.0"

__all__ = [
    "ThumbnailResult",
    "VideoInfo",
    "VideoInput",
    "__version__",
    "concatenate",
    "extract_audio",
    "gif_to_video",
    "info",
    "resize",
    "reverse_video",
    "rotate",
    "speed",
    "strip_audio",
    "thumbnail",
    "thumbnails",
    "trim",
    "video_to_gif",
]
