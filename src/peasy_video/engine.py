"""peasy-video engine — pure functions for video processing powered by moviepy.

All output functions accept an ``output`` path and return a :class:`~pathlib.Path`.
Internally uses moviepy 2.0+ API (``subclipped``, ``resized``, ``rotated``, etc.).
Requires ffmpeg to be installed on the system.
"""

from __future__ import annotations

import io
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from moviepy import VideoFileClip, concatenate_videoclips
from PIL import Image

VideoInput = Path | str


@dataclass(frozen=True)
class VideoInfo:
    """Metadata about a video file."""

    duration: float
    """Duration in seconds."""
    size: tuple[int, int]
    """(width, height) in pixels."""
    fps: float
    """Frames per second."""
    has_audio: bool
    """Whether the video contains an audio track."""
    n_frames: int
    """Estimated total number of frames."""
    file_size_bytes: int
    """File size on disk in bytes."""


@dataclass(frozen=True)
class ThumbnailResult:
    """A single thumbnail extracted from a video."""

    data: bytes
    """Raw PNG image bytes."""
    width: int
    """Image width in pixels."""
    height: int
    """Image height in pixels."""
    format: str
    """Image format (always ``"png"``)."""


def _to_path(source: VideoInput) -> Path:
    """Convert a source to a Path, validating it exists."""
    p = Path(source)
    if not p.exists():
        msg = f"Video file not found: {p}"
        raise FileNotFoundError(msg)
    return p


def _ensure_output_dir(output: Path | str) -> Path:
    """Ensure the output directory exists and return a Path."""
    p = Path(output)
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def info(source: VideoInput) -> VideoInfo:
    """Get metadata for a video file.

    Args:
        source: Path to the video file.

    Returns:
        A :class:`VideoInfo` with duration, size, fps, audio presence,
        frame count, and file size.
    """
    src = _to_path(source)
    clip = VideoFileClip(str(src))
    try:
        return VideoInfo(
            duration=clip.duration,
            size=(clip.w, clip.h),
            fps=clip.fps,
            has_audio=clip.audio is not None,
            n_frames=int(clip.duration * clip.fps),
            file_size_bytes=src.stat().st_size,
        )
    finally:
        clip.close()


def trim(
    source: VideoInput,
    output: Path | str,
    *,
    start: float = 0,
    end: float | None = None,
) -> Path:
    """Trim a video to a specific time range.

    Args:
        source: Path to the input video.
        output: Path for the trimmed output video.
        start: Start time in seconds (default ``0``).
        end: End time in seconds (default ``None`` = end of video).

    Returns:
        Path to the output file.
    """
    src = _to_path(source)
    out = _ensure_output_dir(output)
    clip = VideoFileClip(str(src))
    try:
        trimmed = clip.subclipped(start, end)
        trimmed.write_videofile(str(out), logger=None)
        trimmed.close()
    finally:
        clip.close()
    return out


def resize(
    source: VideoInput,
    output: Path | str,
    *,
    width: int | None = None,
    height: int | None = None,
) -> Path:
    """Resize a video, optionally maintaining aspect ratio.

    If only ``width`` is given, height is calculated to maintain aspect ratio.
    If only ``height`` is given, width is calculated to maintain aspect ratio.
    If both are given, the video is resized to the exact dimensions.

    Args:
        source: Path to the input video.
        output: Path for the resized output video.
        width: Target width in pixels.
        height: Target height in pixels.

    Returns:
        Path to the output file.

    Raises:
        ValueError: If neither ``width`` nor ``height`` is specified.
    """
    if width is None and height is None:
        msg = "At least one of width or height must be specified"
        raise ValueError(msg)

    src = _to_path(source)
    out = _ensure_output_dir(output)
    clip = VideoFileClip(str(src))
    try:
        if width and not height:
            resized_clip = clip.resized(width=width)
        elif height and not width:
            resized_clip = clip.resized(height=height)
        else:
            resized_clip = clip.resized((width, height))
        resized_clip.write_videofile(str(out), logger=None)
        resized_clip.close()
    finally:
        clip.close()
    return out


def extract_audio(
    source: VideoInput,
    output: Path | str,
    *,
    format: str = "mp3",
) -> Path:
    """Extract the audio track from a video file.

    Args:
        source: Path to the input video.
        output: Path for the extracted audio file.
        format: Audio format (default ``"mp3"``). Common values:
            ``"mp3"``, ``"wav"``, ``"ogg"``, ``"aac"``.

    Returns:
        Path to the output audio file.

    Raises:
        ValueError: If the video has no audio track.
    """
    src = _to_path(source)
    out = _ensure_output_dir(output)
    clip = VideoFileClip(str(src))
    try:
        if clip.audio is None:
            msg = "Video has no audio track"
            raise ValueError(msg)
        clip.audio.write_audiofile(str(out), logger=None)
    finally:
        clip.close()
    return out


def thumbnail(source: VideoInput, *, time: float = 0.0) -> ThumbnailResult:
    """Extract a single frame from a video as a PNG image.

    Args:
        source: Path to the input video.
        time: Time in seconds at which to capture the frame (default ``0.0``).

    Returns:
        A :class:`ThumbnailResult` containing PNG bytes and dimensions.
    """
    src = _to_path(source)
    clip = VideoFileClip(str(src))
    try:
        frame = clip.get_frame(time)
        img = Image.fromarray(frame)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return ThumbnailResult(
            data=buf.getvalue(),
            width=img.width,
            height=img.height,
            format="png",
        )
    finally:
        clip.close()


def thumbnails(source: VideoInput, *, count: int = 5) -> list[ThumbnailResult]:
    """Extract evenly-spaced thumbnails from a video.

    Args:
        source: Path to the input video.
        count: Number of thumbnails to extract (default ``5``).

    Returns:
        A list of :class:`ThumbnailResult` objects.
    """
    src = _to_path(source)
    clip = VideoFileClip(str(src))
    try:
        results: list[ThumbnailResult] = []
        duration = clip.duration
        # Distribute thumbnails evenly across the video duration
        for i in range(count):
            t = (i / max(count - 1, 1)) * duration if count > 1 else 0.0
            # Clamp to slightly before the end to avoid out-of-range
            t = min(t, duration - 0.01)
            frame = clip.get_frame(t)
            img = Image.fromarray(frame)
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            results.append(
                ThumbnailResult(
                    data=buf.getvalue(),
                    width=img.width,
                    height=img.height,
                    format="png",
                )
            )
        return results
    finally:
        clip.close()


def concatenate(sources: Sequence[VideoInput], output: Path | str) -> Path:
    """Concatenate multiple videos into one.

    Args:
        sources: List of paths to video files to concatenate (in order).
        output: Path for the concatenated output video.

    Returns:
        Path to the output file.

    Raises:
        ValueError: If fewer than 2 sources are provided.
    """
    if len(sources) < 2:
        msg = "At least 2 video sources are required for concatenation"
        raise ValueError(msg)

    out = _ensure_output_dir(output)
    clips: list[VideoFileClip] = []
    try:
        for src in sources:
            clips.append(VideoFileClip(str(_to_path(src))))
        result = concatenate_videoclips(clips)
        result.write_videofile(str(out), logger=None)
        result.close()
    finally:
        for c in clips:
            c.close()
    return out


def rotate(source: VideoInput, output: Path | str, *, angle: float = 90) -> Path:
    """Rotate a video by a given angle.

    Args:
        source: Path to the input video.
        output: Path for the rotated output video.
        angle: Rotation angle in degrees (default ``90``). Positive values
            rotate counter-clockwise.

    Returns:
        Path to the output file.
    """
    src = _to_path(source)
    out = _ensure_output_dir(output)
    clip = VideoFileClip(str(src))
    try:
        rotated = clip.rotated(angle)
        rotated.write_videofile(str(out), logger=None)
        rotated.close()
    finally:
        clip.close()
    return out


def speed(source: VideoInput, output: Path | str, *, factor: float = 2.0) -> Path:
    """Change the playback speed of a video.

    Args:
        source: Path to the input video.
        output: Path for the output video.
        factor: Speed multiplier (default ``2.0``). Values ``> 1`` speed up,
            values ``< 1`` slow down.

    Returns:
        Path to the output file.

    Raises:
        ValueError: If ``factor`` is not positive.
    """
    if factor <= 0:
        msg = "Speed factor must be positive"
        raise ValueError(msg)

    src = _to_path(source)
    out = _ensure_output_dir(output)
    clip = VideoFileClip(str(src))
    try:
        sped = clip.with_speed_scaled(factor)
        sped.write_videofile(str(out), logger=None)
        sped.close()
    finally:
        clip.close()
    return out


def reverse_video(source: VideoInput, output: Path | str) -> Path:
    """Reverse a video so it plays backwards.

    Args:
        source: Path to the input video.
        output: Path for the reversed output video.

    Returns:
        Path to the output file.
    """
    src = _to_path(source)
    out = _ensure_output_dir(output)
    clip = VideoFileClip(str(src))
    try:
        reversed_clip = clip.time_transform(
            lambda t: clip.duration - t - 1 / clip.fps,
            keep_duration=True,
        )
        reversed_clip.write_videofile(str(out), logger=None)
        reversed_clip.close()
    finally:
        clip.close()
    return out


def strip_audio(source: VideoInput, output: Path | str) -> Path:
    """Remove the audio track from a video.

    Args:
        source: Path to the input video.
        output: Path for the output video without audio.

    Returns:
        Path to the output file.
    """
    src = _to_path(source)
    out = _ensure_output_dir(output)
    clip = VideoFileClip(str(src))
    try:
        silent = clip.without_audio()
        silent.write_videofile(str(out), logger=None)
        silent.close()
    finally:
        clip.close()
    return out


def gif_to_video(
    source: VideoInput,
    output: Path | str,
    *,
    fps: int = 24,
) -> Path:
    """Convert a GIF file to a video.

    Args:
        source: Path to the input GIF file.
        output: Path for the output video file.
        fps: Frames per second for the output video (default ``24``).

    Returns:
        Path to the output file.
    """
    src = _to_path(source)
    out = _ensure_output_dir(output)
    clip = VideoFileClip(str(src))
    try:
        clip.write_videofile(str(out), fps=fps, logger=None)
    finally:
        clip.close()
    return out


def video_to_gif(
    source: VideoInput,
    output: Path | str,
    *,
    fps: int = 10,
    width: int | None = None,
) -> Path:
    """Convert a video to an animated GIF.

    Args:
        source: Path to the input video.
        output: Path for the output GIF file.
        fps: Frames per second for the GIF (default ``10``).
        width: Optional target width (maintains aspect ratio).

    Returns:
        Path to the output file.
    """
    src = _to_path(source)
    out = _ensure_output_dir(output)
    clip = VideoFileClip(str(src))
    try:
        if width is not None:
            clip = clip.resized(width=width)
        clip.write_gif(str(out), fps=fps, logger=None)
    finally:
        clip.close()
    return out
