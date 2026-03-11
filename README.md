# peasy-video

[![PyPI](https://img.shields.io/pypi/v/peasy-video)](https://pypi.org/project/peasy-video/)
[![Python](https://img.shields.io/pypi/pyversions/peasy-video)](https://pypi.org/project/peasy-video/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

Python video toolkit -- 13 operations for trimming, resizing, rotating, speed adjustment, audio extraction, thumbnail generation, GIF conversion, concatenation, and more. Powered by [moviepy](https://zulko.github.io/moviepy/) and [FFmpeg](https://ffmpeg.org/). Every function accepts a file path and returns a `Path` or dataclass result, so you can chain operations and integrate them into any pipeline. Handles MP4, WebM, MKV, AVI, MOV, and any container format supported by FFmpeg.

Built for [peasyvideo.com](https://peasyvideo.com), which offers free interactive tools for video trimming, resizing, format conversion, thumbnail extraction, and GIF creation. The site serves as the reference implementation and hosts the REST API, glossary, and developer guides that complement this library.

> **Try the interactive tools at [peasyvideo.com](https://peasyvideo.com)** -- video trimming, resizing, audio extraction, GIF conversion, and thumbnail generation.

<p align="center">
  <img src="demo.gif" alt="peasy-video demo — video operations and dataclass fields in Python REPL" width="800">
</p>

## Table of Contents

- [Prerequisites](#prerequisites)
- [Install](#install)
- [Quick Start](#quick-start)
- [What You Can Do](#what-you-can-do)
  - [Video Info and Thumbnails](#video-info-and-thumbnails)
  - [Trimming and Concatenation](#trimming-and-concatenation)
  - [Resize and Transform](#resize-and-transform)
  - [Audio Extraction](#audio-extraction)
  - [GIF Conversion](#gif-conversion)
- [Understanding Video Codecs and Containers](#understanding-video-codecs-and-containers)
  - [Video Codecs](#video-codecs)
  - [Container Formats](#container-formats)
  - [Resolution Standards](#resolution-standards)
  - [Frame Rates](#frame-rates)
  - [Aspect Ratios](#aspect-ratios)
- [Command-Line Interface](#command-line-interface)
- [MCP Server (Claude, Cursor, Windsurf)](#mcp-server-claude-cursor-windsurf)
- [API Reference](#api-reference)
- [Learn More About Video Processing](#learn-more-about-video-processing)
- [Also Available](#also-available)
- [Peasy Developer Tools](#peasy-developer-tools)
- [License](#license)

## Prerequisites

peasy-video uses FFmpeg under the hood for all encoding and decoding. Install it before using this library:

| Platform | Command |
|----------|---------|
| **macOS** | `brew install ffmpeg` |
| **Ubuntu/Debian** | `sudo apt install ffmpeg` |
| **Fedora/RHEL** | `sudo dnf install ffmpeg-free` |
| **Windows** | Download from [ffmpeg.org](https://ffmpeg.org/download.html) |
| **Docker** | `RUN apt-get update && apt-get install -y ffmpeg` |

Verify your installation with `ffmpeg -version`. Any FFmpeg version 4.x or later works. For best codec support (AV1, VP9), use FFmpeg 5.0+.

## Install

```bash
pip install peasy-video            # Core library (moviepy + Pillow)
pip install "peasy-video[cli]"     # + CLI (typer)
```

## Quick Start

```python
from peasy_video import info, trim, thumbnail, video_to_gif

# Get video metadata — resolution, duration, fps, audio presence
vi = info("input.mp4")
print(f"{vi.size[0]}x{vi.size[1]}, {vi.duration:.1f}s, {vi.fps} fps")
# 1920x1080, 125.3s, 30.0 fps

# Trim to a 20-second highlight clip
trim("input.mp4", "clip.mp4", start=10, end=30)

# Extract a thumbnail at the 5-second mark as PNG bytes
thumb = thumbnail("input.mp4", time=5.0)
with open("frame.png", "wb") as f:
    f.write(thumb.data)
print(f"Thumbnail: {thumb.width}x{thumb.height} PNG")

# Convert a video clip to an animated GIF for sharing
video_to_gif("input.mp4", "output.gif", fps=10, width=480)
```

## What You Can Do

### Video Info and Thumbnails

Every video file contains metadata that describes its technical properties -- resolution (width x height in pixels), frame rate (fps), total duration, whether an audio track is present, estimated frame count, and file size on disk. The `info()` function reads this metadata without decoding the entire file, making it fast even for large videos.

Thumbnail extraction captures a single frame at a specified timestamp and encodes it as a PNG image. The `thumbnails()` function distributes capture points evenly across the video's duration, producing a contact sheet that represents the video's visual content at a glance -- useful for video management systems, preview galleries, and content moderation workflows.

| Function | Description | Returns |
|----------|-------------|---------|
| `info(source)` | Duration, resolution, fps, audio flag, frame count, file size | `VideoInfo` dataclass |
| `thumbnail(source, *, time)` | Extract a single frame as PNG bytes at a specific timestamp | `ThumbnailResult` dataclass |
| `thumbnails(source, *, count)` | Extract evenly-spaced thumbnails across the video | `list[ThumbnailResult]` |

```python
from peasy_video import info, thumbnail, thumbnails

# Inspect a video file — all metadata in one call
vi = info("interview.mp4")
print(f"Resolution: {vi.size[0]}x{vi.size[1]}")  # 1920x1080
print(f"Duration:   {vi.duration:.1f}s")           # 3842.5s
print(f"Frame rate: {vi.fps} fps")                 # 30.0 fps
print(f"Audio:      {vi.has_audio}")               # True
print(f"Frames:     {vi.n_frames}")                # 115275
print(f"File size:  {vi.file_size_bytes:,} bytes")  # 1,284,039,680 bytes

# Capture a specific moment — returns PNG bytes + dimensions
frame = thumbnail("interview.mp4", time=12.5)
print(f"Thumbnail: {frame.width}x{frame.height} {frame.format}")
# Thumbnail: 1920x1080 png

# Generate a 10-frame contact sheet for preview
frames = thumbnails("interview.mp4", count=10)
for i, f in enumerate(frames):
    with open(f"thumb_{i:02d}.png", "wb") as fp:
        fp.write(f.data)
```

Learn more: [PeasyVideo](https://peasyvideo.com) · [Video Glossary](https://peasyvideo.com/glossary/)

### Trimming and Concatenation

Trimming cuts a video to a specific time range, keeping only the frames between the start and end timestamps. This is the most common video editing operation -- removing intros, extracting highlights, isolating a scene for a social media clip, or cutting dead air from a recorded presentation.

Concatenation joins multiple video files end-to-end into a single continuous video. The source videos should share the same resolution and frame rate for a seamless result. moviepy handles re-encoding automatically, so you can concatenate clips from different sources as long as they are compatible.

| Function | Description |
|----------|-------------|
| `trim(source, output, *, start, end)` | Cut video to a time range (seconds) |
| `concatenate(sources, output)` | Join 2+ videos end-to-end |

```python
from peasy_video import trim, concatenate

# Extract a 20-second highlight from a gameplay recording
trim("game.mp4", "highlight.mp4", start=45, end=65)

# Keep only the first 30 seconds of a lecture (omit start for 0)
trim("lecture.mp4", "intro.mp4", end=30)

# Trim from the 2-minute mark to the end (omit end for full remaining)
trim("lecture.mp4", "body.mp4", start=120)

# Assemble three clips into one continuous video
concatenate(["intro.mp4", "main.mp4", "outro.mp4"], "final.mp4")
```

Learn more: [PeasyVideo](https://peasyvideo.com) · [Developer Docs](https://peasyvideo.com/developers/)

### Resize and Transform

Resizing changes the pixel dimensions of a video. When only one dimension (width or height) is specified, the other is calculated automatically to maintain the original aspect ratio -- preventing stretching or squashing artifacts. This is essential for preparing videos for different platforms: YouTube (1920x1080), Instagram Reels (1080x1920), Twitter/X (1280x720), or web embeds (640x360).

Rotation, speed adjustment, reversal, and audio stripping are spatial and temporal transformations that modify how the video plays back without changing the underlying content.

| Function | Description | Key Parameters |
|----------|-------------|----------------|
| `resize(source, output, *, width, height)` | Scale video dimensions | Aspect ratio preserved if one dimension given |
| `rotate(source, output, *, angle)` | Rotate by any angle | `angle` in degrees, counter-clockwise |
| `speed(source, output, *, factor)` | Change playback speed | `>1.0` faster, `<1.0` slower |
| `reverse_video(source, output)` | Play video backwards | Full reversal with frame reordering |
| `strip_audio(source, output)` | Remove the audio track | Silent video output |

```python
from peasy_video import resize, rotate, speed, reverse_video, strip_audio

# Resize 4K footage (3840x2160) to 720p for web delivery
resize("4k_footage.mp4", "720p.mp4", width=1280)

# Prepare a vertical video for Instagram Reels (1080x1920)
resize("landscape.mp4", "reel.mp4", width=1080, height=1920)

# Rotate a portrait phone recording to landscape orientation
rotate("portrait.mp4", "landscape.mp4", angle=90)

# Create an 8x timelapse from a sunset recording
speed("sunset.mp4", "timelapse.mp4", factor=8.0)

# Slow down a fast action clip to half speed
speed("action.mp4", "slowmo.mp4", factor=0.5)

# Reverse a short clip for a boomerang effect
reverse_video("jump.mp4", "boomerang.mp4")

# Remove audio for a background loop on a website
strip_audio("ambient.mp4", "silent_loop.mp4")
```

Learn more: [PeasyVideo](https://peasyvideo.com) · [Video Glossary](https://peasyvideo.com/glossary/)

### Audio Extraction

Pulling the audio track from a video file is a common workflow for podcasters, music producers, and content creators. peasy-video extracts the audio stream and re-encodes it to your chosen format. FFmpeg handles the codec negotiation -- if the source contains AAC audio and you request MP3 output, the audio is transcoded automatically.

| Format | Extension | Typical Use | Lossy/Lossless |
|--------|-----------|-------------|:--------------:|
| **MP3** | `.mp3` | Podcasts, music sharing, universal compatibility | Lossy |
| **WAV** | `.wav` | Audio editing, production, uncompressed archival | Lossless |
| **OGG** | `.ogg` | Web audio, open-source projects, Opus codec | Lossy |
| **AAC** | `.aac` | Apple ecosystem, streaming, better quality than MP3 at same bitrate | Lossy |

```python
from peasy_video import extract_audio

# Extract audio as MP3 — universal compatibility
extract_audio("interview.mp4", "interview.mp3")

# Extract as WAV for further processing in Audacity or a DAW
extract_audio("concert.mp4", "audio.wav", format="wav")

# Extract as AAC for Apple ecosystem distribution
extract_audio("keynote.mp4", "keynote.aac", format="aac")

# Extract as OGG Vorbis for web audio players
extract_audio("tutorial.mp4", "tutorial.ogg", format="ogg")
```

Learn more: [PeasyVideo](https://peasyvideo.com) · [OpenAPI Spec](https://peasyvideo.com/api/openapi.json)

### GIF Conversion

Animated GIFs remain the dominant format for short, looping animations on the web -- reactions, tutorials, product demos, and memes. Despite being technically inefficient (GIF uses a 256-color palette with LZW compression from 1987), GIFs work universally in browsers, messaging apps, and email clients without requiring a video player.

The trade-off: a 5-second MP4 clip at 720p might be 500 KB, while the same content as a GIF could be 5-10 MB. The `width` and `fps` parameters let you control this trade-off -- reducing both produces smaller files at the cost of visual quality.

Converting GIFs back to video (MP4) is useful when you want to embed animated content with better compression and full-color support.

| Function | Description | Key Parameters |
|----------|-------------|----------------|
| `video_to_gif(source, output, *, fps, width)` | Convert video to animated GIF | `fps=10`, `width=None` |
| `gif_to_video(source, output, *, fps)` | Convert GIF to video | `fps=24` |

```python
from peasy_video import video_to_gif, gif_to_video

# Create a 480px-wide GIF at 12fps — good balance of quality and file size
video_to_gif("reaction.mp4", "reaction.gif", fps=12, width=480)

# Create a small GIF for Slack/Discord — aggressive size reduction
video_to_gif("demo.mp4", "demo.gif", fps=8, width=320)

# Full-resolution GIF for high-quality presentation
video_to_gif("product.mp4", "product.gif", fps=15)

# Convert a GIF back to MP4 — 10x smaller file, better quality
gif_to_video("animation.gif", "animation.mp4", fps=24)
```

Learn more: [PeasyVideo](https://peasyvideo.com) · [Developer Docs](https://peasyvideo.com/developers/)

## Understanding Video Codecs and Containers

Video files involve two distinct concepts: the **codec** (how video/audio data is compressed) and the **container** (the file format that packages the compressed streams together). Understanding this distinction is essential for choosing the right output format and troubleshooting compatibility issues.

### Video Codecs

A codec (coder-decoder) compresses raw video frames into a compact binary stream and decompresses them during playback. Modern codecs achieve 1000:1 compression ratios by exploiting spatial redundancy within frames (intra-frame compression) and temporal redundancy between consecutive frames (inter-frame compression using motion vectors).

| Codec | Standard | Compression Efficiency | Hardware Decode Support | Typical Use |
|-------|----------|:----------------------:|:-----------------------:|-------------|
| **H.264 (AVC)** | ITU-T H.264 / ISO 14496-10 | Baseline | Universal (all devices since ~2010) | Web video, streaming, Blu-ray, video calls |
| **H.265 (HEVC)** | ITU-T H.265 / ISO 23008-2 | ~50% better than H.264 | Modern devices (2015+) | 4K/8K streaming, HDR content, broadcast |
| **VP9** | Google / WebM Project | ~30-40% better than H.264 | Chrome, Android, most smart TVs | YouTube, Google Meet, WebM containers |
| **AV1** | Alliance for Open Media | ~30% better than H.265 | Emerging (2020+ hardware) | Next-gen streaming, Netflix, YouTube 4K |
| **MPEG-4 Part 2** | ISO 14496-2 | Legacy | Universal | Old camcorders, legacy systems |

H.264 remains the safest choice for maximum compatibility. It plays on virtually every device, browser, and platform manufactured in the last 15 years. H.265 offers significantly better compression (roughly half the bitrate for equivalent quality) but has licensing complexities and narrower browser support. VP9 and AV1 are royalty-free alternatives -- VP9 is widely supported through Chrome and YouTube, while AV1 is the newest codec with the best compression ratios but requires newer hardware for real-time decoding.

Learn more: [PeasyVideo](https://peasyvideo.com) · [Video Glossary](https://peasyvideo.com/glossary/)

### Container Formats

A container format is the file format that packages video streams, audio streams, subtitles, and metadata into a single file. The container determines which codecs can be used inside it, how seeking works, and which platforms can play it.

| Container | Extension | Typical Codecs | Streaming | Browser Support | Best For |
|-----------|-----------|----------------|:---------:|:---------------:|----------|
| **MP4** | `.mp4` | H.264, H.265, AAC | Yes (fragmented) | Universal | General distribution, web, mobile |
| **WebM** | `.webm` | VP8, VP9, AV1, Opus | Yes | Chrome, Firefox, Edge | Royalty-free web video |
| **MKV** | `.mkv` | Any codec | No (not designed for it) | VLC, media players | Archival, multiple audio/subtitle tracks |
| **AVI** | `.avi` | Legacy codecs, H.264 | No | Limited | Legacy Windows applications |
| **MOV** | `.mov` | H.264, ProRes, AAC | Yes | macOS, iOS, Safari | Apple ecosystem, professional editing |
| **FLV** | `.flv` | H.264, AAC | Yes (RTMP) | No (Flash deprecated) | Legacy streaming archives |

MP4 with H.264 video and AAC audio is the most universally compatible combination. When moviepy writes a video file with a `.mp4` extension, it uses this combination by default through FFmpeg.

Learn more: [PeasyVideo](https://peasyvideo.com) · [Developer Docs](https://peasyvideo.com/developers/)

### Resolution Standards

Video resolution defines the pixel dimensions of each frame. Higher resolution means more detail but larger file sizes and higher processing requirements. The naming convention (720p, 1080p, 4K) refers to the vertical pixel count or the approximate horizontal pixel count.

| Name | Dimensions | Pixels | Aspect Ratio | Common Use |
|------|-----------|-------:|:------------:|------------|
| **480p** (SD) | 854 x 480 | 410K | 16:9 | Mobile data saving, legacy DVD |
| **720p** (HD) | 1280 x 720 | 922K | 16:9 | Web embeds, video calls, budget streaming |
| **1080p** (Full HD) | 1920 x 1080 | 2.1M | 16:9 | YouTube, Netflix SD, Blu-ray, general production |
| **1440p** (2K / QHD) | 2560 x 1440 | 3.7M | 16:9 | Gaming monitors, YouTube high quality |
| **2160p** (4K / UHD) | 3840 x 2160 | 8.3M | 16:9 | Netflix 4K, professional production, cinema |
| **4320p** (8K / FUHD) | 7680 x 4320 | 33.2M | 16:9 | Future-proofing, NHK broadcast, large displays |
| **Vertical 1080** | 1080 x 1920 | 2.1M | 9:16 | Instagram Reels, TikTok, YouTube Shorts |

The "p" in 720p/1080p stands for "progressive scan" (every frame is a full image), as opposed to the older interlaced scan (1080i) used in broadcast television.

Learn more: [PeasyVideo](https://peasyvideo.com) · [Video Glossary](https://peasyvideo.com/glossary/)

### Frame Rates

Frame rate (frames per second, fps) determines how many individual images are displayed per second. Higher frame rates produce smoother motion but generate larger files and require more processing power. The choice of frame rate depends on the content type and target platform.

| Frame Rate | Use Case | File Size Impact |
|:----------:|----------|:----------------:|
| **12 fps** | Animated GIFs, stop-motion | Smallest |
| **24 fps** | Cinema, film, narrative content (the "cinematic look") | Baseline |
| **25 fps** | PAL television (Europe, Asia, Australia) | ~4% larger than 24 |
| **30 fps** | NTSC television (Americas, Japan), YouTube default | ~25% larger than 24 |
| **48 fps** | High frame rate cinema (The Hobbit), VR content | 2x larger than 24 |
| **60 fps** | Gaming, sports, smooth web video, slow-motion source | 2.5x larger than 24 |
| **120 fps** | Slow-motion capture, high-refresh gaming | 5x larger than 24 |
| **240 fps** | Ultra slow-motion (iPhone, GoPro) | 10x larger than 24 |

When using `video_to_gif()`, reducing the fps from 30 to 10-12 dramatically shrinks GIF file sizes while maintaining acceptable visual quality for most use cases.

Learn more: [PeasyVideo](https://peasyvideo.com) · [OpenAPI Spec](https://peasyvideo.com/api/openapi.json)

### Aspect Ratios

Aspect ratio is the proportional relationship between a video's width and height. Using the wrong aspect ratio causes black bars (letterboxing/pillarboxing) or content being cropped by the platform.

| Ratio | Decimal | Common Resolutions | Platform |
|:-----:|:-------:|---------------------|----------|
| **16:9** | 1.78 | 1920x1080, 1280x720, 3840x2160 | YouTube, Netflix, web standard |
| **9:16** | 0.56 | 1080x1920 | TikTok, Instagram Reels, YouTube Shorts |
| **4:3** | 1.33 | 1024x768, 640x480 | Legacy TV, presentations, iPad |
| **1:1** | 1.00 | 1080x1080 | Instagram feed, profile videos |
| **21:9** | 2.33 | 2560x1080, 3440x1440 | Ultrawide cinema, anamorphic |
| **4:5** | 0.80 | 1080x1350 | Instagram portrait posts |

When resizing with `resize()`, specifying only `width` or only `height` preserves the original aspect ratio automatically. Specifying both forces exact dimensions, which may stretch the video if the aspect ratio differs.

Learn more: [PeasyVideo](https://peasyvideo.com) · [Developer Docs](https://peasyvideo.com/developers/)

## Command-Line Interface

Install with CLI extras: `pip install "peasy-video[cli]"`

```bash
# Show video metadata — duration, resolution, fps, audio, frame count, file size
peasy-video info input.mp4

# Trim a video to a specific time range (seconds)
peasy-video trim input.mp4 -o clip.mp4 --start 10 --end 30

# Resize video to 640px wide (height auto-calculated for aspect ratio)
peasy-video resize input.mp4 -o small.mp4 --width 640

# Resize to exact dimensions
peasy-video resize input.mp4 -o reel.mp4 --width 1080 --height 1920

# Extract audio as MP3
peasy-video extract-audio input.mp4 -o audio.mp3 --format mp3

# Extract a thumbnail at the 5-second mark
peasy-video thumbnail input.mp4 -o frame.png --time 5.0

# Speed up a video 2x
peasy-video speed input.mp4 -o fast.mp4 --factor 2.0

# Convert video to animated GIF (480px wide, 10fps)
peasy-video to-gif input.mp4 -o output.gif --fps 10 --width 480

# Concatenate multiple videos into one
peasy-video concat video1.mp4 video2.mp4 -o combined.mp4
```

## MCP Server (Claude, Cursor, Windsurf)

peasy-video is available as an MCP tool through [peasy-mcp](https://pypi.org/project/peasy-mcp/), the unified MCP server for all Peasy tools. This exposes video operations to AI assistants like Claude, Cursor, and Windsurf.

**Claude Desktop** (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "peasy": {
      "command": "uvx",
      "args": ["--from", "peasy-mcp", "peasy-mcp"]
    }
  }
}
```

**Cursor** (`.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "peasy": {
      "command": "uvx",
      "args": ["--from", "peasy-mcp", "peasy-mcp"]
    }
  }
}
```

**Windsurf** (`~/.windsurf/mcp.json`):

```json
{
  "mcpServers": {
    "peasy": {
      "command": "uvx",
      "args": ["--from", "peasy-mcp", "peasy-mcp"]
    }
  }
}
```

Available video tools: `video_info`, `video_trim`, `video_resize`, `video_extract_audio`, `video_thumbnail`, `video_thumbnails`, `video_speed`, `video_to_gif`, `video_gif_to_video`, `video_concatenate`, `video_rotate`, `video_reverse`, `video_strip_audio`.

## API Reference

### Video Operations

| Function | Signature | Returns | Description |
|----------|-----------|---------|-------------|
| `info` | `(source: VideoInput) -> VideoInfo` | `VideoInfo` | Duration, resolution, fps, audio, frame count, file size |
| `trim` | `(source, output, *, start=0, end=None) -> Path` | `Path` | Cut video to a time range in seconds |
| `resize` | `(source, output, *, width=None, height=None) -> Path` | `Path` | Scale video dimensions (aspect ratio preserved if one dimension given) |
| `rotate` | `(source, output, *, angle=90) -> Path` | `Path` | Rotate video counter-clockwise by degrees |
| `speed` | `(source, output, *, factor=2.0) -> Path` | `Path` | Change playback speed (>1 faster, <1 slower) |
| `reverse_video` | `(source, output) -> Path` | `Path` | Reverse video playback (play backwards) |
| `strip_audio` | `(source, output) -> Path` | `Path` | Remove the audio track from a video |
| `extract_audio` | `(source, output, *, format="mp3") -> Path` | `Path` | Extract audio as mp3, wav, ogg, or aac |
| `thumbnail` | `(source, *, time=0.0) -> ThumbnailResult` | `ThumbnailResult` | Extract a single frame as PNG bytes |
| `thumbnails` | `(source, *, count=5) -> list[ThumbnailResult]` | `list[ThumbnailResult]` | Extract evenly-spaced thumbnails across the video |
| `concatenate` | `(sources, output) -> Path` | `Path` | Join 2+ videos end-to-end |
| `video_to_gif` | `(source, output, *, fps=10, width=None) -> Path` | `Path` | Convert video to animated GIF |
| `gif_to_video` | `(source, output, *, fps=24) -> Path` | `Path` | Convert GIF to video (MP4) |

### Types

| Type | Definition | Used By |
|------|------------|---------|
| `VideoInput` | `Path \| str` | All functions (source parameter) |
| `VideoInfo` | Frozen dataclass: `duration`, `size`, `fps`, `has_audio`, `n_frames`, `file_size_bytes` | `info()` return type |
| `ThumbnailResult` | Frozen dataclass: `data` (bytes), `width`, `height`, `format` (always `"png"`) | `thumbnail()`, `thumbnails()` return type |

## Learn More About Video Processing

- **Home**: [PeasyVideo](https://peasyvideo.com)
- **Reference**: [Video Glossary](https://peasyvideo.com/glossary/)
- **API**: [REST API Docs](https://peasyvideo.com/developers/) · [OpenAPI Spec](https://peasyvideo.com/api/openapi.json)

## Also Available

| Platform | Install | Link |
|----------|---------|------|
| **MCP** | `uvx --from peasy-mcp peasy-mcp` | [Config](#mcp-server-claude-cursor-windsurf) |

## Peasy Developer Tools

Part of the [Peasy Tools](https://peasytools.com) open-source developer tools ecosystem.

| Package | PyPI | npm | Description |
|---------|------|-----|-------------|
| peasy-image | [PyPI](https://pypi.org/project/peasy-image/) | [npm](https://www.npmjs.com/package/peasy-image) | 21 image operations: resize, crop, compress, convert, watermark -- [peasyimage.com](https://peasyimage.com) |
| peasy-pdf | [PyPI](https://pypi.org/project/peasy-pdf/) | [npm](https://www.npmjs.com/package/peasy-pdf) | PDF merge, split, rotate, compress, extract, encrypt -- [peasypdf.com](https://peasypdf.com) |
| peasy-css | [PyPI](https://pypi.org/project/peasy-css/) | [npm](https://www.npmjs.com/package/peasy-css) | CSS gradients, shadows, borders, flexbox, grid, animations -- [peasycss.com](https://peasycss.com) |
| peasy-compress | [PyPI](https://pypi.org/project/peasy-compress/) | [npm](https://www.npmjs.com/package/peasy-compress) | ZIP, TAR, gzip, bz2, lzma archive operations -- [peasytools.com](https://peasytools.com) |
| peasy-document | [PyPI](https://pypi.org/project/peasy-document/) | [npm](https://www.npmjs.com/package/peasy-document) | Markdown, HTML, CSV, JSON document conversion -- [peasytools.com](https://peasytools.com) |
| peasy-audio | [PyPI](https://pypi.org/project/peasy-audio/) | -- | Audio convert, trim, merge, normalize, analyze -- [peasyaudio.com](https://peasyaudio.com) |
| **peasy-video** | [PyPI](https://pypi.org/project/peasy-video/) | -- | **Video trim, resize, extract audio, thumbnails, GIF -- [peasyvideo.com](https://peasyvideo.com)** |
| peasy-convert | [PyPI](https://pypi.org/project/peasy-convert/) | -- | Unified CLI for all Peasy tools -- [peasytools.com](https://peasytools.com) |
| peasy-mcp | [PyPI](https://pypi.org/project/peasy-mcp/) | -- | Unified MCP server for AI assistants -- [peasytools.com](https://peasytools.com) |

## License

MIT
