"""Tests for peasy_video.engine — video processing functions."""

from __future__ import annotations

from pathlib import Path

import pytest

# Skip all tests if moviepy is not available (requires ffmpeg)
moviepy = pytest.importorskip("moviepy")

from moviepy import ColorClip  # noqa: E402

from peasy_video.engine import (  # noqa: E402
    ThumbnailResult,
    VideoInfo,
    concatenate,
    extract_audio,
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


def _make_test_video(
    path: Path,
    duration: float = 2.0,
    size: tuple[int, int] = (320, 240),
    fps: int = 24,
) -> Path:
    """Create a minimal test video using a solid color clip."""
    clip = ColorClip(size=size, color=(255, 0, 0), duration=duration)
    clip.write_videofile(str(path), fps=fps, logger=None)
    clip.close()
    return path


# ---------------------------------------------------------------------------
# info
# ---------------------------------------------------------------------------


class TestInfo:
    def test_info_returns_video_info(self, tmp_path: Path) -> None:
        video = _make_test_video(tmp_path / "test.mp4")
        vi = info(video)
        assert isinstance(vi, VideoInfo)
        assert vi.duration == pytest.approx(2.0, abs=0.1)
        assert vi.size == (320, 240)
        assert vi.fps == pytest.approx(24, abs=1)
        assert vi.n_frames > 0
        assert vi.file_size_bytes > 0

    def test_info_file_not_found(self) -> None:
        with pytest.raises(FileNotFoundError):
            info("/nonexistent/video.mp4")


# ---------------------------------------------------------------------------
# trim
# ---------------------------------------------------------------------------


class TestTrim:
    def test_trim_shortens_video(self, tmp_path: Path) -> None:
        video = _make_test_video(tmp_path / "input.mp4", duration=4.0)
        output = tmp_path / "trimmed.mp4"
        result = trim(video, output, start=1.0, end=3.0)
        assert result.exists()
        vi = info(result)
        assert vi.duration == pytest.approx(2.0, abs=0.2)

    def test_trim_with_start_only(self, tmp_path: Path) -> None:
        video = _make_test_video(tmp_path / "input.mp4", duration=3.0)
        output = tmp_path / "trimmed.mp4"
        result = trim(video, output, start=1.0)
        assert result.exists()
        vi = info(result)
        assert vi.duration == pytest.approx(2.0, abs=0.2)


# ---------------------------------------------------------------------------
# resize
# ---------------------------------------------------------------------------


class TestResize:
    def test_resize_by_width(self, tmp_path: Path) -> None:
        video = _make_test_video(tmp_path / "input.mp4", size=(320, 240))
        output = tmp_path / "resized.mp4"
        result = resize(video, output, width=160)
        assert result.exists()
        vi = info(result)
        assert vi.size[0] == 160
        # Aspect ratio maintained: 160/320 = 0.5, so height ~ 120
        assert vi.size[1] == pytest.approx(120, abs=2)

    def test_resize_by_height(self, tmp_path: Path) -> None:
        video = _make_test_video(tmp_path / "input.mp4", size=(320, 240))
        output = tmp_path / "resized.mp4"
        result = resize(video, output, height=120)
        assert result.exists()
        vi = info(result)
        assert vi.size[1] == 120

    def test_resize_requires_dimension(self, tmp_path: Path) -> None:
        video = _make_test_video(tmp_path / "input.mp4")
        with pytest.raises(ValueError, match="At least one"):
            resize(video, tmp_path / "out.mp4")


# ---------------------------------------------------------------------------
# thumbnail
# ---------------------------------------------------------------------------


class TestThumbnail:
    def test_thumbnail_returns_png(self, tmp_path: Path) -> None:
        video = _make_test_video(tmp_path / "input.mp4", size=(320, 240))
        result = thumbnail(video, time=0.5)
        assert isinstance(result, ThumbnailResult)
        assert result.format == "png"
        assert result.width == 320
        assert result.height == 240
        # Check PNG magic bytes
        assert result.data[:4] == b"\x89PNG"

    def test_thumbnail_at_start(self, tmp_path: Path) -> None:
        video = _make_test_video(tmp_path / "input.mp4")
        result = thumbnail(video, time=0.0)
        assert len(result.data) > 0


# ---------------------------------------------------------------------------
# thumbnails
# ---------------------------------------------------------------------------


class TestThumbnails:
    def test_thumbnails_count(self, tmp_path: Path) -> None:
        video = _make_test_video(tmp_path / "input.mp4", duration=3.0)
        results = thumbnails(video, count=3)
        assert len(results) == 3
        for r in results:
            assert isinstance(r, ThumbnailResult)
            assert r.data[:4] == b"\x89PNG"

    def test_thumbnails_single(self, tmp_path: Path) -> None:
        video = _make_test_video(tmp_path / "input.mp4")
        results = thumbnails(video, count=1)
        assert len(results) == 1


# ---------------------------------------------------------------------------
# speed
# ---------------------------------------------------------------------------


class TestSpeed:
    def test_speed_doubles(self, tmp_path: Path) -> None:
        video = _make_test_video(tmp_path / "input.mp4", duration=4.0)
        output = tmp_path / "fast.mp4"
        result = speed(video, output, factor=2.0)
        assert result.exists()
        vi = info(result)
        assert vi.duration == pytest.approx(2.0, abs=0.3)

    def test_speed_invalid_factor(self, tmp_path: Path) -> None:
        video = _make_test_video(tmp_path / "input.mp4")
        with pytest.raises(ValueError, match="positive"):
            speed(video, tmp_path / "out.mp4", factor=0)


# ---------------------------------------------------------------------------
# reverse
# ---------------------------------------------------------------------------


class TestReverse:
    def test_reverse_same_duration(self, tmp_path: Path) -> None:
        video = _make_test_video(tmp_path / "input.mp4", duration=2.0)
        output = tmp_path / "reversed.mp4"
        result = reverse_video(video, output)
        assert result.exists()
        vi = info(result)
        assert vi.duration == pytest.approx(2.0, abs=0.2)


# ---------------------------------------------------------------------------
# strip_audio
# ---------------------------------------------------------------------------


class TestStripAudio:
    def test_strip_audio_output_exists(self, tmp_path: Path) -> None:
        video = _make_test_video(tmp_path / "input.mp4")
        output = tmp_path / "silent.mp4"
        result = strip_audio(video, output)
        assert result.exists()


# ---------------------------------------------------------------------------
# concatenate
# ---------------------------------------------------------------------------


class TestConcatenate:
    def test_concatenate_two_clips(self, tmp_path: Path) -> None:
        v1 = _make_test_video(tmp_path / "v1.mp4", duration=1.5)
        v2 = _make_test_video(tmp_path / "v2.mp4", duration=1.5)
        output = tmp_path / "concat.mp4"
        result = concatenate([v1, v2], output)
        assert result.exists()
        vi = info(result)
        assert vi.duration == pytest.approx(3.0, abs=0.3)

    def test_concatenate_requires_two(self, tmp_path: Path) -> None:
        v1 = _make_test_video(tmp_path / "v1.mp4")
        with pytest.raises(ValueError, match="At least 2"):
            concatenate([v1], tmp_path / "out.mp4")


# ---------------------------------------------------------------------------
# video_to_gif
# ---------------------------------------------------------------------------


class TestVideoToGif:
    def test_video_to_gif_creates_file(self, tmp_path: Path) -> None:
        video = _make_test_video(tmp_path / "input.mp4", duration=1.0)
        output = tmp_path / "output.gif"
        result = video_to_gif(video, output, fps=5)
        assert result.exists()
        assert result.stat().st_size > 0
        # Check GIF magic bytes
        data = result.read_bytes()
        assert data[:4] == b"GIF8"


# ---------------------------------------------------------------------------
# rotate
# ---------------------------------------------------------------------------


class TestRotate:
    def test_rotate_creates_output(self, tmp_path: Path) -> None:
        video = _make_test_video(tmp_path / "input.mp4", size=(320, 240))
        output = tmp_path / "rotated.mp4"
        result = rotate(video, output, angle=90)
        assert result.exists()


# ---------------------------------------------------------------------------
# extract_audio
# ---------------------------------------------------------------------------


class TestExtractAudio:
    def test_extract_audio_no_audio(self, tmp_path: Path) -> None:
        """ColorClip has no audio, so extraction should raise ValueError."""
        video = _make_test_video(tmp_path / "input.mp4")
        with pytest.raises(ValueError, match="no audio"):
            extract_audio(video, tmp_path / "audio.mp3")
