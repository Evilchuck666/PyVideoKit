#!/usr/bin/env python3
"""End-to-end smoke test: runs every pvk command on a short generated clip.

Needs FFmpeg, FFprobe and SoX in PATH. Run it against an installed package
(not the src tree) so it checks the entry points that actually ship.
"""

import subprocess
import sys
import tempfile
from importlib.metadata import version
from pathlib import Path

COMMANDS = [
    "apply-vhs-effect", "concat-videos", "convert-to-ffv1", "extract-audio",
    "fade-video", "prepare-youtube", "trim-video",
]


def run(*args: str) -> str:
    result = subprocess.run(args, capture_output=True, text=True)
    if result.returncode != 0:
        sys.exit(f"FAIL {' '.join(args)}\n{result.stdout}{result.stderr}")
    return result.stdout.strip()


def video_codec(path: Path) -> str:
    return run("ffprobe", "-v", "error", "-select_streams", "v:0",
               "-show_entries", "stream=codec_name", "-of", "default=nk=1:nw=1", str(path))


def check(label: str, out: str, codec: str | None = None) -> Path:
    path = Path(out.splitlines()[-1]) if out else Path()
    if not path.is_file() or path.stat().st_size == 0:
        sys.exit(f"FAIL {label}: {out!r} is not a non-empty file")
    if codec and video_codec(path) != codec:
        sys.exit(f"FAIL {label}: expected {codec}, got {video_codec(path)!r}")
    print(f"ok   {label}: {path.name}")
    return path


def main() -> None:
    cli_version = version("PyVideoKit-CLI")
    print(f"PyVideoKit-CLI {cli_version} on PyVideoKit-Libs {version('PyVideoKit-Libs')}")
    if cli_version not in run("pvk", "--version"):
        sys.exit("FAIL pvk --version does not report the package version")
    for name in COMMANDS:
        run("pvk", name, "--help")
        run(name, "--help")
    print(f"ok   pvk and {len(COMMANDS)} standalone scripts answer --help")

    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "source.mp4"
        run("ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-f", "lavfi", "-i", "testsrc2=size=320x240:rate=25:duration=3",
            "-f", "lavfi", "-i", "sine=frequency=440:sample_rate=48000:duration=3",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", str(src))

        master = check("convert-to-ffv1", run("pvk", "convert-to-ffv1", str(src)), "ffv1")
        check("trim-video", run("pvk", "trim-video", str(master), "--start", "0.5", "--end", "00:00:02",
                                "-o", str(Path(tmp) / "trim.mkv")))
        check("concat-videos", run("pvk", "concat-videos", str(master), str(master)))
        check("fade-video", run("pvk", "fade-video", str(master), "--fade", "0.5"), "ffv1")
        check("extract-audio", run("pvk", "extract-audio", str(master)))
        check("apply-vhs-effect", run("pvk", "apply-vhs-effect", str(master)), "ffv1")
        check("prepare-youtube", run("pvk", "prepare-youtube", str(master)), "prores")

    print("All smoke tests passed.")


if __name__ == "__main__":
    main()
