#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Video Trimming Script

This script trims a video segment using FFmpeg with stream copying (no re-encoding).
It supports both command-line arguments and an interactive mode using 'rofi' to
prompt for start and end times.

Usage:
    python3 trim_video.py -i input.mp4 --start 10 --end 20
    python3 trim_video.py -i input.mp4 --interactive

Dependencies:
    - ffmpeg
    - ffprobe
    - rofi (optional, for interactive mode)
"""

import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Tuple
from . import ffmpeg_utils as utils


class UserCancelled(Exception):
    """Exception raised when the user cancels an interactive prompt."""
    pass


def ensure_rofi() -> None:
    """
    Checks if 'rofi' is available in the system PATH.
    Exits the script with an error if 'rofi' is not found.
    """
    if utils.which("rofi") is None:
        sys.stderr.write(f"{utils.EMOJI_ERROR} Error: --interactive requires 'rofi' in PATH.\n")
        sys.exit(1)


def rofi_prompt(label: str, initial: str = "") -> str:
    """
    Prompts the user for input using 'rofi' in dmenu mode.

    Args:
        label (str): The prompt label to display.
        initial (str): The initial value to pre-fill (used as filter).

    Returns:
        str: The user's input string.

    Raises:
        UserCancelled: If the user cancels the rofi prompt (returns non-zero exit code or empty string).
    """
    ensure_rofi()
    # Run rofi with dmenu mode, prompt label, and initial filter text
    proc = subprocess.run(
        ["rofi", "-dmenu", "-p", label, "-filter", initial],
        input="", text=True, capture_output=True
    )
    if proc.returncode != 0:
        raise UserCancelled
    val = proc.stdout.strip()
    if val == "":
        raise UserCancelled
    return val


def prompt_interactive_rofi(defaults: dict) -> Tuple[str, str]:
    """
    Prompts the user for start and end times using rofi.

    Args:
        defaults (dict): A dictionary containing default 'start' and 'end' values.

    Returns:
        Tuple[str, str]: A tuple containing the start and end time strings.
    """
    start = rofi_prompt("Start (e.g., 12.5 or 00:00:12.5)", defaults.get("start", "0"))
    end   = rofi_prompt("End timestamp (seconds or HH:MM:SS(.sss))", defaults.get("end", ""))
    return start, end


def build_output_path(input_path: Path) -> Path:
    """
    Constructs the output file path based on the current timestamp.

    Args:
        input_path (Path): The path to the input video file.

    Returns:
        Path: The constructed output file path (e.g., YYYYMMDD_HHMMSS.ext).
    """
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    ext = input_path.suffix
    name = f"{ts}{ext}"
    return input_path.with_name(name)


def build_parser() -> argparse.ArgumentParser:
    """
    Builds the command-line argument parser.

    Returns:
        argparse.ArgumentParser: The configured argument parser.
    """
    p = argparse.ArgumentParser(description="Cut a segment from a video using FFmpeg (stream copy only).")
    p.add_argument("-i", "--input", type=str, required=True, help="Input video path")
    p.add_argument("--start", type=str, help="Start time (seconds or HH:MM:SS(.sss))")
    p.add_argument("--end", type=str, help="End time (seconds or HH:MM:SS(.sss))")
    p.add_argument("--interactive", action="store_true", help="Prompt for start and end via rofi")
    return p


def main() -> None:
    """
    Main function to execute the video trimming logic.
    """
    # Check for required dependencies
    if not utils.has_ffmpeg() or not utils.has_ffprobe():
        print(f"{utils.EMOJI_ERROR} Error: ffmpeg/ffprobe are required in PATH.", file=sys.stderr)
        sys.exit(1)

    parser = build_parser()
    args = parser.parse_args()

    input_path = Path(args.input).expanduser().resolve()
    if not input_path.exists():
        print(f"{utils.EMOJI_ERROR} Error: input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    # Handle interactive mode or command-line arguments
    if args.interactive:
        try:
            start_str, end_str = prompt_interactive_rofi({
                "start": args.start or "0",
                "end": args.end or "",
            })
        except UserCancelled:
            print("Cancelled by user.")
            sys.exit(0)
    else:
        if not args.start or not args.end:
            parser.error("Missing required arguments: --start and --end")
        start_str, end_str = args.start, args.end

    # Parse time strings to seconds
    try:
        start_seconds = utils.parse_time_to_seconds(start_str)
        end_seconds = utils.parse_time_to_seconds(end_str)
    except ValueError as e:
        print(f"{utils.EMOJI_ERROR} Error: {e}", file=sys.stderr)
        sys.exit(1)

    if start_seconds is None or end_seconds is None:
        print("Cancelled by user.")
        sys.exit(0)

    # Validate start and end times
    if end_seconds <= start_seconds:
        print(f"{utils.EMOJI_ERROR} Error: end time must be greater than start time.", file=sys.stderr)
        sys.exit(1)

    duration_seconds = end_seconds - start_seconds

    # Check against file duration
    file_dur = utils.probe_duration(input_path)
    if file_dur > 0 and start_seconds > file_dur:
        print(f"{utils.EMOJI_ERROR} Error: start ({start_seconds:.3f}s) exceeds input duration ({file_dur:.3f}s).", file=sys.stderr)
        sys.exit(1)

    output_path = build_output_path(input_path)

    # Construct FFmpeg command
    # -ss before -i for fast seeking
    # -t for duration
    # -c copy to avoid re-encoding
    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-y",
        "-ss", utils.seconds_to_hms(float(start_seconds)),
        "-i", str(input_path),
        "-t", utils.seconds_to_hms(float(duration_seconds)),
        "-c", "copy",
        str(output_path)
    ]

    # Run FFmpeg with progress bar
    rc = utils.run_ffmpeg_with_progress(
        cmd,
        f"{utils.EMOJI_CUT} Video cut",
        f"Cutting:\n{input_path.name}",
        duration=float(duration_seconds)
    )
    sys.exit(rc)


if __name__ == "__main__":
    main()
