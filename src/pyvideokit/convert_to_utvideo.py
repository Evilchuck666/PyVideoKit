#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script to convert videos to UTVideo format (lossless) using FFmpeg.
This is useful for intermediate processing to avoid generation loss.
"""

import argparse
import sys
from pathlib import Path
from . import ffmpeg_utils as utils


def build_output_path(input_path: Path) -> Path:
    """
    Generates the output file path by appending '_utvideo' to the filename.
    The output format is forced to .avi as it is a common container for UTVideo.

    Args:
        input_path (Path): Path to the input video file.

    Returns:
        Path: The generated output file path.
    """
    stem = input_path.stem
    out_name = f"{stem}_utvideo.avi"
    return input_path.with_name(out_name)


def convert_to_utvideo(input_path: Path) -> None:
    """
    Runs FFmpeg to convert the input video to UTVideo format.

    Args:
        input_path (Path): Path to the input video file.
    """
    duration = utils.probe_duration(input_path)
    output_path = build_output_path(input_path)

    cmd = [
        "ffmpeg",
        "-hide_banner",         # Suppress printing banner
        "-y",                   # Overwrite output file without asking
        "-i", str(input_path),  # Input file
        "-map", "0",            # Map all streams from input
        "-c:v", "utvideo",      # Video codec: UTVideo (lossless)
        "-r", "60",             # Force frame rate to 60 fps
        "-c:a", "pcm_f32le",    # Audio codec: PCM 32-bit floating point (high quality)
        str(output_path)
    ]

    rc = utils.run_ffmpeg_with_progress(
        cmd,
        f"{utils.EMOJI_VIDEO} UTVideo conversion",
        f"Converting:\n{input_path.name}",
        duration=duration
    )

    if rc != 0:
        sys.exit(rc)
    else:
        print(f"{utils.EMOJI_SUCCESS} Conversion completed: {output_path}")


def main() -> None:
    """
    Main function to parse arguments and execute the conversion.
    """
    parser = argparse.ArgumentParser(description="Convert video to UTVideo format.")
    parser.add_argument("input", help="Input video path")
    args = parser.parse_args()

    input_path = Path(args.input).expanduser().resolve()
    if not input_path.exists():
        print(f"{utils.EMOJI_ERROR} Error: file does not exist: {input_path}", file=sys.stderr)
        sys.exit(1)

    convert_to_utvideo(input_path)


if __name__ == "__main__":
    main()
