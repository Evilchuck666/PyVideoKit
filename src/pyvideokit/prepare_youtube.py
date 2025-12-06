#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Prepare Video for YouTube Upload.

This script converts an input video to a high-quality format suitable for YouTube
uploading. It upscales the video to 4K (2160p) if necessary and encodes it using
Apple ProRes 422 HQ. This ensures minimal quality loss during YouTube's
processing and compression.

The script uses:
- ffmpeg for conversion
- ProRes 422 HQ codec for video
- PCM 16-bit LE codec for audio
"""

import argparse
import sys
from pathlib import Path
from . import ffmpeg_utils as utils


def build_output_path(input_path: Path) -> Path:
    """
    Generate the output file path.

    Appends '_youtube' to the original filename and changes the extension to .mov.

    Args:
        input_path (Path): Path to the input video file.

    Returns:
        Path: Path for the output video file.
    """
    stem = input_path.stem
    out_name = f"{stem}_youtube.mov"
    return input_path.with_name(out_name)


def prepare_youtube(input_path: Path) -> None:
    """
    Convert the video to a YouTube-optimized format (ProRes 422 HQ, 4K).

    Args:
        input_path (Path): Path to the input video file.
    """
    duration = utils.probe_duration(input_path)
    output_path = build_output_path(input_path)

    # Construct the ffmpeg command
    cmd = [
        "ffmpeg",
        "-hide_banner",             # Suppress printing banner
        "-y",                       # Overwrite output file if it exists
        "-i", str(input_path),      # Input file
        "-map", "0",                # Map all streams from input
        "-vf", "scale=-1:2160",     # Scale to 2160p (4K) height, keeping aspect ratio. YouTube gives better bitrate to 4K uploads.
        "-c:v", "prores_ks",        # Video codec: ProRes (ks implementation)
        "-profile:v", "3",          # Profile 3 corresponds to ProRes 422 HQ
        "-pix_fmt", "yuv422p10le",  # Pixel format: 10-bit 4:2:2
        "-c:a", "pcm_s16le",        # Audio codec: Uncompressed PCM 16-bit
        str(output_path)
    ]

    rc = utils.run_ffmpeg_with_progress(
        cmd,
        f"{utils.EMOJI_VIDEO} YouTube preparation (ProRes)",
        f"Converting:\n{input_path.name}",
        duration=duration
    )

    if rc != 0:
        sys.exit(rc)
    else:
        print(f"{utils.EMOJI_SUCCESS} Conversion completed: {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert video to ProRes 422 HQ for YouTube.")
    parser.add_argument("input", help="Input video path")
    args = parser.parse_args()

    input_path = Path(args.input).expanduser().resolve()
    if not input_path.exists():
        print(f"{utils.EMOJI_ERROR} Error: file does not exist: {input_path}", file=sys.stderr)
        sys.exit(1)

    prepare_youtube(input_path)


if __name__ == "__main__":
    main()
