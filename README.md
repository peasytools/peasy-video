# peasy-video

[![PyPI](https://img.shields.io/pypi/v/peasy-video)](https://pypi.org/project/peasy-video/)
[![Python](https://img.shields.io/pypi/pyversions/peasy-video)](https://pypi.org/project/peasy-video/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

Video processing made easy. Trim, resize, extract audio, generate thumbnails, concatenate clips, convert to GIF, adjust speed, and more -- all in pure Python powered by [moviepy](https://zulko.github.io/moviepy/) and ffmpeg. 13 functions covering the most common video operations, each designed to be called in a single line.

> **Requires ffmpeg** -- moviepy uses ffmpeg under the hood. Install it before using peasy-video:
>
> - **macOS**: `brew install ffmpeg`
> - **Ubuntu/Debian**: `sudo apt install ffmpeg`
> - **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html)

## Table of Contents

- [Install](#install)
- [Quick Start](#quick-start)
- [What You Can Do](#what-you-can-do)
  - [Video Info and Thumbnails](#video-info-and-thumbnails)
  - [Trimming and Concatenation](#trimming-and-concatenation)
  - [Resize and Transform](#resize-and-transform)
  - [Audio Extraction](#audio-extraction)
  - [GIF Conversion](#gif-conversion)
- [Command-Line Interface](#command-line-interface)
- [API Reference](#api-reference)
- [Peasy Developer Tools](#peasy-developer-tools)
- [License](#license)

## Install

```bash
# Core library
pip install peasy-video

# With CLI support
pip install "peasy-video[cli]"
```

## Quick Start

```python
from peasy_video import info, trim, thumbnail, video_to_gif

# Get video metadata
vi = info("input.mp4")
print(f"{vi.size[0]}x{vi.size[1]}, {vi.duration:.1f}s, {vi.fps} fps")

# Trim to 10-30 second range
trim("input.mp4", "clip.mp4", start=10, end=30)

# Extract a thumbnail at the 5-second mark
thumb = thumbnail("input.mp4", time=5.0)
with open("frame.png", "wb") as f:
    f.write(thumb.data)

# Convert a video to GIF
video_to_gif("input.mp4", "output.gif", fps=10, width=480)
```

## What You Can Do

### Video Info and Thumbnails

Get metadata from any video file -- duration, resolution, frame rate, audio presence, frame count, and file size. Extract single frames or evenly-spaced thumbnail sequences as PNG images.

| Function | Description |
|----------|-------------|
| `info(source)` | Return duration, size, fps, audio flag, frame count, file size |
| `thumbnail(source, *, time)` | Extract a single frame as PNG bytes |
| `thumbnails(source, *, count)` | Extract evenly-spaced thumbnails across the video |

```python
from peasy_video import info, thumbnail, thumbnails

# Inspect a video file
vi = info("interview.mp4")
print(f"{vi.size[0]}x{vi.size[1]} at {vi.fps} fps, {vi.duration:.1f}s")
print(f"Audio: {vi.has_audio}, Frames: {vi.n_frames}")

# Capture a specific moment
frame = thumbnail("interview.mp4", time=12.5)
print(f"Thumbnail: {frame.width}x{frame.height} PNG, {len(frame.data):,} bytes")

# Generate a thumbnail contact sheet
frames = thumbnails("interview.mp4", count=10)
for i, f in enumerate(frames):
    with open(f"thumb_{i:02d}.png", "wb") as fp:
        fp.write(f.data)
```

### Trimming and Concatenation

Cut videos to specific time ranges or join multiple clips together. Useful for removing intros/outros, extracting highlights, or assembling a montage from multiple source files.

| Function | Description |
|----------|-------------|
| `trim(source, output, *, start, end)` | Cut video to a time range |
| `concatenate(sources, output)` | Join multiple videos end-to-end |

```python
from peasy_video import trim, concatenate

# Extract a 20-second highlight
trim("game.mp4", "highlight.mp4", start=45, end=65)

# Trim from the start (keep first 30 seconds)
trim("lecture.mp4", "intro.mp4", end=30)

# Join three clips into one video
concatenate(["intro.mp4", "main.mp4", "outro.mp4"], "final.mp4")
```

### Resize and Transform

Resize videos while maintaining aspect ratio, rotate footage, change playback speed, or reverse playback. Remove audio tracks when you need silent video.

| Function | Description |
|----------|-------------|
| `resize(source, output, *, width, height)` | Resize (aspect ratio kept if one dimension given) |
| `rotate(source, output, *, angle)` | Rotate by any angle in degrees |
| `speed(source, output, *, factor)` | Speed up or slow down playback |
| `reverse_video(source, output)` | Reverse video playback |
| `strip_audio(source, output)` | Remove the audio track |

```python
from peasy_video import resize, rotate, speed, reverse_video, strip_audio

# Resize to 720p width (height auto-calculated)
resize("4k_footage.mp4", "720p.mp4", width=1280)

# Rotate a portrait video to landscape
rotate("portrait.mp4", "landscape.mp4", angle=90)

# Create a 2x timelapse
speed("sunset.mp4", "timelapse.mp4", factor=8.0)

# Reverse a short clip for a boomerang effect
reverse_video("jump.mp4", "boomerang.mp4")

# Remove audio for a background loop
strip_audio("ambient.mp4", "silent_loop.mp4")
```

### Audio Extraction

Pull the audio track from a video file and save it as MP3, WAV, OGG, or AAC. Useful for creating podcast clips from video interviews or extracting music.

| Function | Description |
|----------|-------------|
| `extract_audio(source, output, *, format)` | Extract audio as mp3, wav, ogg, or aac |

```python
from peasy_video import extract_audio

# Extract audio as MP3
extract_audio("interview.mp4", "interview.mp3")

# Extract as WAV for further processing
extract_audio("concert.mp4", "audio.wav", format="wav")
```

### GIF Conversion

Convert between video and animated GIF formats. Create shareable GIFs from video clips, or convert existing GIFs to video for broader compatibility and smaller file sizes.

| Function | Description |
|----------|-------------|
| `video_to_gif(source, output, *, fps, width)` | Convert video to animated GIF |
| `gif_to_video(source, output, *, fps)` | Convert GIF to video |

```python
from peasy_video import video_to_gif, gif_to_video

# Create a 480px-wide GIF at 12fps
video_to_gif("reaction.mp4", "reaction.gif", fps=12, width=480)

# Convert a GIF back to video (smaller file, better quality)
gif_to_video("animation.gif", "animation.mp4", fps=24)
```

## Command-Line Interface

Install with CLI extras: `pip install "peasy-video[cli]"`

```bash
# Video info
peasy-video info input.mp4

# Trim video
peasy-video trim input.mp4 -o clip.mp4 --start 10 --end 30

# Resize video
peasy-video resize input.mp4 -o small.mp4 --width 640

# Extract audio
peasy-video extract-audio input.mp4 -o audio.mp3 --format mp3

# Extract a thumbnail
peasy-video thumbnail input.mp4 -o frame.png --time 5.0

# Change speed
peasy-video speed input.mp4 -o fast.mp4 --factor 2.0

# Convert to GIF
peasy-video to-gif input.mp4 -o output.gif --fps 10 --width 480

# Concatenate videos
peasy-video concat video1.mp4 video2.mp4 -o combined.mp4
```

## API Reference

| Function | Signature | Returns |
|----------|-----------|---------|
| `info` | `(source) -> VideoInfo` | Video metadata |
| `trim` | `(source, output, *, start, end) -> Path` | Trimmed video |
| `resize` | `(source, output, *, width, height) -> Path` | Resized video |
| `extract_audio` | `(source, output, *, format) -> Path` | Audio file |
| `thumbnail` | `(source, *, time) -> ThumbnailResult` | PNG thumbnail |
| `thumbnails` | `(source, *, count) -> list[ThumbnailResult]` | Multiple thumbnails |
| `concatenate` | `(sources, output) -> Path` | Concatenated video |
| `rotate` | `(source, output, *, angle) -> Path` | Rotated video |
| `speed` | `(source, output, *, factor) -> Path` | Speed-adjusted video |
| `reverse_video` | `(source, output) -> Path` | Reversed video |
| `strip_audio` | `(source, output) -> Path` | Video without audio |
| `gif_to_video` | `(source, output, *, fps) -> Path` | Video from GIF |
| `video_to_gif` | `(source, output, *, fps, width) -> Path` | GIF from video |

## Peasy Developer Tools

Part of the [Peasy Tools](https://peasytools.com) open-source developer tools ecosystem.

| Package | PyPI | Description |
|---------|------|-------------|
| peasy-audio | [PyPI](https://pypi.org/project/peasy-audio/) | Audio processing with pydub -- convert, trim, merge, normalize |
| peasy-compress | [PyPI](https://pypi.org/project/peasy-compress/) | File compression -- gzip, brotli, zstd, lz4, snappy |
| peasy-convert | [PyPI](https://pypi.org/project/peasy-convert/) | File format conversion -- JSON, YAML, TOML, CSV, XML |
| peasy-css | [PyPI](https://pypi.org/project/peasy-css/) | CSS processing -- minify, format, merge, prefix |
| peasy-document | [PyPI](https://pypi.org/project/peasy-document/) | Document conversion -- Markdown, HTML, PDF, DOCX |
| peasy-image | [PyPI](https://pypi.org/project/peasy-image/) | Image processing -- resize, crop, rotate, compress, watermark |
| peasy-pdf | [PyPI](https://pypi.org/project/peasy-pdf/) | PDF tools -- merge, split, compress, watermark, extract |
| peasytext | [PyPI](https://pypi.org/project/peasytext/) | Text processing -- slug, case, hash, encode, truncate |
| **peasy-video** | [PyPI](https://pypi.org/project/peasy-video/) | **Video processing -- trim, resize, thumbnails, GIF, audio extraction** |

## License

MIT
