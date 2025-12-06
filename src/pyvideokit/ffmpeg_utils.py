#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FFmpeg Utilities Module

This module provides utility functions for interacting with FFmpeg and FFprobe,
handling time conversions, and sending system notifications using dunstify.
"""

import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional


EMOJI_SUCCESS = "✅"
EMOJI_ERROR   = "❌"
EMOJI_WARNING = "⚠️"
EMOJI_INFO    = "ℹ️"
EMOJI_PROCESS = "⏳"
EMOJI_CUT     = "✂️"
EMOJI_JOIN    = "🔗"
EMOJI_AUDIO   = "🔊"
EMOJI_VIDEO   = "🎬"
EMOJI_SAVE    = "💾"


def which(cmd: str) -> Optional[str]:
    """Check if a command exists in the system PATH."""
    return shutil.which(cmd)


def has_ffmpeg() -> bool:
    """Check if ffmpeg is available."""
    return which("ffmpeg") is not None


def has_ffprobe() -> bool:
    """Check if ffprobe is available."""
    return which("ffprobe") is not None


def dunst_available() -> bool:
    """Check if dunstify (notification tool) is available."""
    return which("dunstify") is not None


def send_dunst_notification(summary: str,
                            body: str,
                            replaces_id: int | None = None,
                            timeout_ms: int = 0) -> int | None:
    """
    Send a system notification using dunstify.

    Args:
        summary: The title of the notification.
        body: The body text of the notification.
        replaces_id: Optional ID of a notification to replace.
        timeout_ms: Timeout in milliseconds (0 for default/infinite depending on config).

    Returns:
        The notification ID if successful, or None if dunstify is not available.
    """
    if not dunst_available():
        print(f"[NOTIFY] {summary}: {body}")
        return None

    try:
        cmd = ["dunstify", "-p", "-t", str(timeout_ms), summary, body]
        if replaces_id is not None:
            cmd.insert(1, "-r")
            cmd.insert(2, str(replaces_id))
            
        out = subprocess.check_output(
            cmd,
            stderr=subprocess.DEVNULL
        ).decode().strip()
        try:
            return int(out)
        except ValueError:
            return replaces_id
    except Exception:
        return replaces_id


def close_dunst_notification(notif_id: int | None) -> None:
    """
    Close a specific dunst notification.

    Args:
        notif_id: The ID of the notification to close.
    """
    if notif_id is None or not dunst_available():
        return
    try:
        subprocess.run(["dunstify", "-C", str(notif_id)],
                       stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)
    except Exception:
        pass


def parse_time_to_seconds(ts: str) -> Optional[float]:
    """
    Parse a time string into seconds.

    Supported formats:
    - "SS.ms" (seconds)
    - "MM:SS" (minutes:seconds)
    - "HH:MM:SS" (hours:minutes:seconds)

    Args:
        ts: Time string.

    Returns:
        Total seconds as float, or None if input is empty.
    """
    ts = (ts or "").strip()
    if ts == "":
        return None
    if ts.count(":") == 0:
        return float(ts)
    parts = [float(p) for p in ts.split(":")]
    if len(parts) == 2:
        mm, ss = parts
        return mm * 60 + ss
    if len(parts) == 3:
        hh, mm, ss = parts
        return hh * 3600 + mm * 60 + ss
    raise ValueError(f"Invalid time format: {ts}")


def seconds_to_hms(seconds: float) -> str:
    """
    Convert seconds to HH:MM:SS.mmm format.

    Args:
        seconds: Time in seconds.

    Returns:
        Formatted string "HH:MM:SS.mmm".
    """
    seconds = max(0.0, float(seconds))
    hh = int(seconds // 3600)
    mm = int((seconds % 3600) // 60)
    ss = seconds - (hh * 3600 + mm * 60)
    return f"{hh:02d}:{mm:02d}:{ss:06.3f}"


def probe_duration(path: Path) -> float:
    """
    Get the duration of a media file using ffprobe.

    Args:
        path: Path to the media file.

    Returns:
        Duration in seconds, or 0.0 if failed/not found.
    """
    if not has_ffprobe():
        return 0.0
    try:
        out = subprocess.check_output(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=nk=1:nw=1", str(path)],
            stderr=subprocess.DEVNULL
        ).decode().strip()
        return float(out)
    except Exception:
        return 0.0


def run_command(cmd: list[str]) -> None:
    """
    Run a subprocess command and exit on failure.

    Args:
        cmd: List of command arguments.
    """
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"{EMOJI_ERROR} Command failed: {' '.join(cmd)}", file=sys.stderr)
        sys.exit(e.returncode)


def run_ffmpeg_with_progress(cmd: list[str],
                             task_name: str,
                             file_label: str,
                             duration: float = 0.0) -> int:
    """
    Run an FFmpeg command and show progress via dunst notifications.

    Args:
        cmd: The FFmpeg command list.
        task_name: Name of the task (for notification title).
        file_label: Label for the file being processed (for notification body).
        duration: Total duration of the input file (for progress calculation).

    Returns:
        Return code of the process.
    """
    base_cmd = cmd[:1]
    rest_cmd = cmd[1:]
    
    # Inject progress flags if not present
    if "-progress" not in cmd:
        progress_flags = ["-progress", "pipe:1", "-nostats", "-loglevel", "error"]
        full_cmd = base_cmd + progress_flags + rest_cmd
    else:
        full_cmd = cmd

    initial_body = f"{file_label}\n0.0%"
    notif_id = send_dunst_notification(task_name, initial_body, timeout_ms=0)

    try:
        proc = subprocess.Popen(
            full_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=1,
            universal_newlines=True,
        )
    except FileNotFoundError:
        close_dunst_notification(notif_id)
        send_dunst_notification(EMOJI_ERROR + " " + task_name, "Error: ffmpeg not found.", timeout_ms=4000)
        return 1

    last_pct = -1.0
    
    # Read stdout line by line to parse progress
    for line in proc.stdout or []:
        line = line.strip()
        if not line:
            continue

        # Parse time from FFmpeg progress output
        if line.startswith("out_time_ms="):
            try:
                ms = int(line.split("=", 1)[1])
                out_time_sec = ms / 1_000_000.0
                
                # Calculate percentage
                if duration > 0:
                    pct = min(100.0, (out_time_sec / duration) * 100.0)
                else:
                    # Fallback progress if duration is unknown (cyclic 0-100)
                    pct = min(100.0, (out_time_sec % 10) * 10.0)

                # Update notification if progress changed by at least 1%
                if pct - last_pct >= 1.0 or pct >= 100.0:
                    last_pct = pct
                    body = f"{file_label}\n{pct:0.1f}%"
                    notif_id = send_dunst_notification(
                        task_name,
                        body,
                        replaces_id=notif_id,
                        timeout_ms=0,
                    )
            except ValueError:
                pass
        
        elif line.startswith("progress=end"):
            break

    rc = proc.wait()
    close_dunst_notification(notif_id)

    if rc == 0:
        send_dunst_notification(
            task_name,
            f"Finished:\n{file_label}",
            timeout_ms=2000,
        )
    else:
        send_dunst_notification(
            EMOJI_ERROR + " " + task_name,
            f"FFmpeg exited with code {rc}.",
            timeout_ms=4000,
        )
        print(f"Error: FFmpeg exited with code {rc}.", file=sys.stderr)

    return rc
