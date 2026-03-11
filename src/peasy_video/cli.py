"""peasy-video CLI — video processing commands powered by moviepy."""

from __future__ import annotations

from pathlib import Path

import typer

from peasy_video import engine

app = typer.Typer(
    name="video",
    help="Video tools — trim, resize, extract audio, thumbnails, convert.",
    no_args_is_help=True,
)


@app.command()
def info(source: str = typer.Argument(help="Path to the video file")) -> None:
    """Show video metadata (duration, size, fps, audio, frames, file size)."""
    vi = engine.info(source)
    typer.echo(f"Duration:   {vi.duration:.2f}s")
    typer.echo(f"Size:       {vi.size[0]}x{vi.size[1]}")
    typer.echo(f"FPS:        {vi.fps}")
    typer.echo(f"Has audio:  {vi.has_audio}")
    typer.echo(f"Frames:     {vi.n_frames}")
    typer.echo(f"File size:  {vi.file_size_bytes:,} bytes")


@app.command()
def trim(
    source: str = typer.Argument(help="Path to the input video"),
    output: str = typer.Option(..., "-o", "--output", help="Path for the trimmed video"),
    start: float = typer.Option(0, "--start", help="Start time in seconds"),
    end: float | None = typer.Option(None, "--end", help="End time in seconds"),
) -> None:
    """Trim a video to a specific time range."""
    result = engine.trim(source, output, start=start, end=end)
    typer.echo(f"Trimmed video saved to {result}")


@app.command()
def resize(
    source: str = typer.Argument(help="Path to the input video"),
    output: str = typer.Option(..., "-o", "--output", help="Path for the resized video"),
    width: int | None = typer.Option(None, "--width", help="Target width in pixels"),
    height: int | None = typer.Option(None, "--height", help="Target height in pixels"),
) -> None:
    """Resize a video. Maintains aspect ratio if only one dimension given."""
    result = engine.resize(source, output, width=width, height=height)
    typer.echo(f"Resized video saved to {result}")


@app.command(name="extract-audio")
def extract_audio(
    source: str = typer.Argument(help="Path to the input video"),
    output: str = typer.Option(..., "-o", "--output", help="Path for the audio file"),
    format: str = typer.Option("mp3", "--format", help="Audio format (mp3, wav, ogg, aac)"),
) -> None:
    """Extract the audio track from a video."""
    result = engine.extract_audio(source, output, format=format)
    typer.echo(f"Audio extracted to {result}")


@app.command()
def thumbnail(
    source: str = typer.Argument(help="Path to the input video"),
    output: str = typer.Option(..., "-o", "--output", help="Path for the thumbnail PNG"),
    time: float = typer.Option(0.0, "--time", help="Time in seconds to capture"),
) -> None:
    """Extract a single frame from a video as a PNG image."""
    result = engine.thumbnail(source, time=time)
    out = Path(output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(result.data)
    typer.echo(f"Thumbnail saved to {out} ({result.width}x{result.height})")


@app.command()
def speed(
    source: str = typer.Argument(help="Path to the input video"),
    output: str = typer.Option(..., "-o", "--output", help="Path for the output video"),
    factor: float = typer.Option(2.0, "--factor", help="Speed multiplier (>1 faster, <1 slower)"),
) -> None:
    """Change the playback speed of a video."""
    result = engine.speed(source, output, factor=factor)
    typer.echo(f"Speed-adjusted video saved to {result}")


@app.command(name="to-gif")
def to_gif(
    source: str = typer.Argument(help="Path to the input video"),
    output: str = typer.Option(..., "-o", "--output", help="Path for the output GIF"),
    fps: int = typer.Option(10, "--fps", help="Frames per second for the GIF"),
    width: int | None = typer.Option(None, "--width", help="Target width (aspect ratio kept)"),
) -> None:
    """Convert a video to an animated GIF."""
    result = engine.video_to_gif(source, output, fps=fps, width=width)
    typer.echo(f"GIF saved to {result}")


_CONCAT_SOURCES_HELP = typer.Argument(help="Paths to video files to concatenate")


@app.command()
def concat(
    sources: list[str] = _CONCAT_SOURCES_HELP,
    output: str = typer.Option(..., "-o", "--output", help="Path for the concatenated video"),
) -> None:
    """Concatenate multiple videos into one."""
    result = engine.concatenate(sources, output)
    typer.echo(f"Concatenated video saved to {result}")


if __name__ == "__main__":
    app()
