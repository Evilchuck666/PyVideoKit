#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script to concatenate (join) multiple video files into a single file using ffmpeg.
It uses the concat demuxer to join files without re-encoding.
"""

import argparse
import shlex
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from . import ffmpeg_utils as utils


def total_duration(video_paths: list[Path]) -> float:
    """
    Calculate the total duration of all provided video files.

    Args:
        video_paths: List of paths to video files.

    Returns:
        Total duration in seconds.
    """
    total = 0.0
    for p in video_paths:
        total += utils.probe_duration(p)
    return total


def build_concat_file(video_paths: list[Path]) -> Path:
    """
    Create a temporary file suitable for the ffmpeg concat demuxer.

    The file will contain a list of 'file' directives pointing to the input videos.

    Args:
        video_paths: List of paths to video files to be concatenated.

    Returns:
        Path to the created temporary file.
    """
    tmp = tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False, encoding="utf-8"
    )
    with tmp as f:
        for p in video_paths:
            # Escape single quotes for ffmpeg concat file format
            path_str = str(p).replace("'", r"'\''")
            f.write(f"file '{path_str}'\n")
    return Path(tmp.name)


def build_output_path(first_video: Path) -> Path:
    """
    Generate an output file path based on the first video's name and current timestamp.

    Args:
        first_video: Path to the first video file.

    Returns:
        Path for the output joined video.
    """
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    ext = first_video.suffix or ".avi"
    return first_video.with_name(f"joined_{timestamp}{ext}")


def join_videos(video_paths: list[Path]) -> int:
    """
    Concatenate multiple video files into a single file.

    Args:
        video_paths: List of paths to video files.

    Returns:
        Exit code (0 for success, non-zero for failure).
    """
    if len(video_paths) < 2:
        print(f"{utils.EMOJI_ERROR} Need at least two input videos.")
        return 1

    concat_file = build_concat_file(video_paths)
    output_path = build_output_path(video_paths[0])

    # ffmpeg command to concat files without re-encoding
    cmd = [
        "ffmpeg", "-f", "concat", "-safe", "0",
        "-i", str(concat_file),
        "-c", "copy", str(output_path)
    ]

    print("Running:", " ".join(shlex.quote(c) for c in cmd))

    label = video_paths[0].name
    if len(video_paths) > 1:
        label = f"{video_paths[0].name} (+{len(video_paths) - 1} more)"

    total = total_duration(video_paths)

    rc = utils.run_ffmpeg_with_progress(
        cmd,
        f"{utils.EMOJI_JOIN} Video join",
        f"Joining:\n{label}",
        duration=total
    )

    # Cleanup temporary concat file
    try:
        concat_file.unlink(missing_ok=True)
    except Exception:
        pass

    return rc


def main() -> None:
    parser = argparse.ArgumentParser(description="Join multiple video files.")
    parser.add_argument("videos", nargs="+", help="List of video files to join")
    args = parser.parse_args()

    video_paths = [Path(p).expanduser().resolve() for p in args.videos]
    sys.exit(join_videos(video_paths))


if __name__ == "__main__":
    main()
