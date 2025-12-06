#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script to extract audio from a video file using ffmpeg.
It extracts the audio stream without re-encoding (copy).
"""

import argparse
import sys
from pathlib import Path
from . import ffmpeg_utils as utils


def build_output_path(input_path: Path) -> Path:
    """
    Constructs the output file path by replacing the input extension with .wav.

    Args:
        input_path (Path): The path to the input video file.

    Returns:
        Path: The path to the output audio file.
    """
    stem = input_path.stem
    out_name = f"{stem}.wav"
    return input_path.with_name(out_name)


def extract_audio(input_path: Path) -> None:
    """
    Extracts the audio track from the video file using ffmpeg.

    Args:
        input_path (Path): The path to the input video file.
    """
    duration = utils.probe_duration(input_path)
    output_path = build_output_path(input_path)

    cmd = [
        "ffmpeg",
        "-hide_banner",         # Suppress printing banner
        "-y",                   # Overwrite output file if it exists
        "-i", str(input_path),  # Input file
        "-vn",                  # No video: disable video recording
        "-c:a", "copy",         # Codec audio: copy (no re-encoding)
        str(output_path)
    ]

    rc = utils.run_ffmpeg_with_progress(
        cmd,
        f"{utils.EMOJI_AUDIO} Audio extraction",
        f"Extracting from:\n{input_path.name}",
        duration=duration
    )

    if rc != 0:
        sys.exit(rc)
    else:
        print(f"{utils.EMOJI_SUCCESS} Extraction completed: {output_path}")


def main() -> None:
    """
    Main function to handle command line arguments and execute the audio extraction.
    """
    parser = argparse.ArgumentParser(description="Extract audio from video file.")
    parser.add_argument("input", help="Input video path")
    args = parser.parse_args()

    input_path = Path(args.input).expanduser().resolve()
    if not input_path.exists():
        print(f"{utils.EMOJI_ERROR} Error: file does not exist: {input_path}", file=sys.stderr)
        sys.exit(1)

    extract_audio(input_path)


if __name__ == "__main__":
    main()
