#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Fade Video Script
=================

This script applies fade-in and/or fade-out effects to a video file using FFmpeg.
It supports specifying fade durations in seconds or HH:MM:SS format.
The output video is encoded using the UTVideo codec with PCM audio.

Usage:
    python fade_video.py -i <input_video> --fade-in <duration> --fade-out <duration>
    python fade_video.py -i <input_video> --fade <duration>
"""

import argparse
import sys
from pathlib import Path
from typing import Optional
from . import ffmpeg_utils as utils


def parse_duration_arg(name: str, value: Optional[str]) -> Optional[float]:
    """
    Parses a duration argument string into seconds.

    Args:
        name: The name of the argument (for error messages).
        value: The value of the argument (e.g., "5", "00:00:05").

    Returns:
        The duration in seconds as a float, or None if value is None.

    Raises:
        ValueError: If the duration is not positive.
    """
    if value is None:
        return None
    secs = utils.parse_time_to_seconds(value)
    if secs is None:
        return None
    if secs <= 0:
        raise ValueError(f"{name} must be > 0 (got {secs})")
    return secs


def build_output_path(input_path: Path, output: Optional[str]) -> Path:
    """
    Determines the output file path.

    If output is not specified, creates a new filename based on the input filename
    with a '_fade' suffix in the same directory.
    If output is a directory, places the file inside it with the generated name.

    Args:
        input_path: Path to the input video file.
        output: Optional output path string (file or directory).

    Returns:
        Path object for the output file.
    """
    if output is None:
        return input_path.with_name(f"{input_path.stem}_fade{input_path.suffix}")

    out_path = Path(output).expanduser()
    if out_path.is_dir():
        return out_path / f"{input_path.stem}_fade{input_path.suffix}"
    return out_path


def build_fade_cmd(
    input_path: Path,
    fade_in: Optional[float],
    fade_out: Optional[float],
    total_duration: float,
    output_path: Path
) -> list[str]:
    """
    Constructs the FFmpeg command line arguments for applying fade effects.

    Args:
        input_path: Path to the input video.
        fade_in: Duration of fade-in in seconds (None for no fade-in).
        fade_out: Duration of fade-out in seconds (None for no fade-out).
        total_duration: Total duration of the input video in seconds.
        output_path: Path for the output video.

    Returns:
        A list of command line arguments for FFmpeg.
    """
    # Force 60 fps for consistency with other tools in this kit
    v_filters = ["fps=60"]

    if fade_in is not None:
        v_filters.append(f"fade=t=in:st=0:d={fade_in:.3f}")

    if fade_out is not None:
        # Calculate start time for fade out
        start_out = max(0.0, total_duration - fade_out)
        v_filters.append(f"fade=t=out:st={start_out:.3f}:d={fade_out:.3f}")

    v_filters.append("format=yuv420p")

    vf_chain = ",".join(v_filters)

    a_filters = []
    if fade_in is not None:
        a_filters.append(f"afade=t=in:st=0:d={fade_in:.3f}")
    if fade_out is not None:
        a_start_out = max(0.0, total_duration - fade_out)
        a_filters.append(f"afade=t=out:st={a_start_out:.3f}:d={fade_out:.3f}")

    # Combine audio filters if any exist
    af_chain = ",".join(a_filters) if a_filters else None

    cmd = [
        "ffmpeg",
        "-hide_banner",         # Suppress printing banner
        "-y",                   # Overwrite output file without asking
        "-i", str(input_path),  # Input file
        "-c:v", "utvideo",      # Use UTVideo lossless codec
        "-pix_fmt", "yuv420p",  # Pixel format
        "-r", "60",             # Output frame rate
    ]

    cmd += ["-vf", vf_chain]

    if af_chain:
        cmd += ["-c:a", "pcm_f32le", "-af", af_chain]
    else:
        cmd += ["-c:a", "pcm_f32le"]

    cmd.append(str(output_path))
    return cmd


def build_parser() -> argparse.ArgumentParser:
    """
    Creates and configures the argument parser.

    Returns:
        Configured argparse.ArgumentParser object.
    """
    p = argparse.ArgumentParser(
        description="Apply fade-in / fade-out to a video using FFmpeg (UTVideo, 60 fps, pcm_f32le) with dunst progress."
    )
    p.add_argument("-i", "--input", type=str, required=True, help="Input video path")
    p.add_argument("--fade-in", type=str, help="Fade-in duration (seconds or HH:MM:SS(.sss))")
    p.add_argument("--fade-out", type=str, help="Fade-out duration (seconds or HH:MM:SS(.sss))")
    p.add_argument("--fade", type=str, help="Symmetric fade duration (applies both fade-in and fade-out)")
    p.add_argument("-o", "--output", type=str, help="Output file or directory (default: same dir, '<stem>_fade<ext>')")
    return p


def main() -> None:
    """
    Main entry point for the script.
    Parses arguments, validates inputs, and executes the FFmpeg command.
    """
    if not utils.has_ffmpeg() or not utils.has_ffprobe():
        print(f"{utils.EMOJI_ERROR} Error: ffmpeg and ffprobe are required in PATH.", file=sys.stderr)
        sys.exit(1)

    parser = build_parser()
    args = parser.parse_args()

    input_path = Path(args.input).expanduser().resolve()
    if not input_path.exists():
        print(f"{utils.EMOJI_ERROR} Error: input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    try:
        fade_in: Optional[float]
        fade_out: Optional[float]

        if args.fade is not None:
            both = parse_duration_arg("--fade", args.fade)
            fade_in = both
            fade_out = both
        else:
            fade_in = parse_duration_arg("--fade-in", args.fade_in) if args.fade_in is not None else None
            fade_out = parse_duration_arg("--fade-out", args.fade_out) if args.fade_out is not None else None
    except ValueError as e:
        print(f"{utils.EMOJI_ERROR} Error parsing fade duration: {e}", file=sys.stderr)
        sys.exit(1)

    if fade_in is None and fade_out is None:
        print(f"{utils.EMOJI_ERROR} Error: you must specify at least one fade: --fade, --fade-in or --fade-out.", file=sys.stderr)
        sys.exit(1)

    try:
        total_duration = utils.probe_duration(input_path)
        if total_duration <= 0:
             raise RuntimeError("Non-positive duration")
    except RuntimeError as e:
        print(f"{utils.EMOJI_ERROR} Error: {e}", file=sys.stderr)
        sys.exit(1)

    output_path = build_output_path(input_path, args.output)

    cmd = build_fade_cmd(
        input_path=input_path,
        fade_in=fade_in,
        fade_out=fade_out,
        total_duration=total_duration,
        output_path=output_path
    )

    rc = utils.run_ffmpeg_with_progress(
        cmd,
        f"{utils.EMOJI_VIDEO} Video fade",
        f"Encoding:\n{input_path.name}",
        duration=total_duration
    )
    sys.exit(rc)


if __name__ == "__main__":
    main()
