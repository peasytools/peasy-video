# peasy-video — Video Processing Library Demo
Output demo.gif

Set FontSize 20
Set Width 1000
Set Height 580
Set Shell "zsh"
Set Theme "Catppuccin Mocha"
Set TypingSpeed 30ms
Set Padding 24

Type "uv run --with peasy-video python3"
Enter
Sleep 2.5s

Type "import peasy_video"
Enter
Sleep 1s

Type "# Available video operations"
Enter
Sleep 0.5s

Type "[f for f in dir(peasy_video) if not f.startswith('_')]"
Enter
Sleep 2s

Type "# VideoInfo dataclass fields"
Enter
Sleep 0.5s

Type "from peasy_video import VideoInfo"
Enter
Sleep 0.5s

Type "[f.name for f in VideoInfo.__dataclass_fields__.values()]"
Enter
Sleep 2s

Type "# Functions: info, trim, resize, speed, rotate,"
Enter
Sleep 0.5s

Type "#   thumbnail, thumbnails, extract_audio, strip_audio,"
Enter
Sleep 0.5s

Type "#   concatenate, video_to_gif, gif_to_video, reverse_video"
Enter
Sleep 0.5s

Type "print(f'peasy-video v{peasy_video.__version__} — 13 operations')"
Enter
Sleep 2s

Type "exit()"
Enter
Sleep 1s
