#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Apply VHS Effect Script

This script applies a VHS-style aesthetic to an input video file. It processes both
the visual and audio components to simulate the look and sound of an old VHS tape.

The process involves:
1.  **Video Processing**:
    -   Splitting the video into Y, U, and V planes.
    -   Scaling the chroma planes (U and V) to simulate color bleeding.
    -   Reducing saturation.
    -   Adding noise.
    -   Applying horizontal jitter/displacement.
2.  **Audio Processing**:
    -   Generating brown noise.
    -   Mixing the noise with the original audio.
    -   Applying a low-pass filter to simulate tape frequency limitations.
3.  **Muxing**: Combining the processed video and audio into a final AVI file.
4.  **Cleanup**: Removing temporary files.

Dependencies:
-   ffmpeg
-   sox
-   ffmpeg_utils (local module)

Usage:
    python apply_vhs_effect.py [input_video_path]

If the input path is not provided as an argument, the script will prompt for it.
"""

import argparse
import math
import sys
from pathlib import Path
from . import ffmpeg_utils as utils


# -----------------------------------------------------------------------------
# Constants & Configuration
# -----------------------------------------------------------------------------

# Audio processing constants
SAMPLE_RATE   = 48000
BIT_DEPTH     = 32
CHANNELS      = 2
LOW_PASS_FREQ = 4000  # Cut-off frequency to simulate tape limitations
IN_VOL        = 1.0   # Original audio volume
OUT_VOL       = 0.077 # Noise volume
DB            = -22.75
DB_VOLUME     = math.pow(10, DB / 20.0)

# FFMPEG Filter Chain for VHS Visual Effect:
# 1. format=yuv420p: Ensure consistent pixel format.
# 2. split=3: Split video into 3 streams for Y, U, V processing.
# 3. extractplanes: Isolate Y (Luma), U (Chroma Blue), V (Chroma Red).
# 4. scale (U/V): Downscale and upscale chroma planes to simulate low color resolution (color bleeding).
# 5. mergeplanes: Recombine the processed planes.
# 6. eq: Reduce saturation to mimic aged tape.
# 7. noise: Add random noise.
# 8. geq: Apply horizontal jitter/displacement using a mathematical formula.
FFMPEG_FILTER = (
    "format=yuv420p, split=3 [a][b][c]; "
    "[a] extractplanes=y [y]; "
    "[b] extractplanes=u [u]; "
    "[c] extractplanes=v [v]; "
    "[y] scale=768:1080, scale=1920:1080 [luma_scaled]; "
    "[u] scale=120:540, scale=960:540 [u_scaled]; "
    "[v] scale=120:540, scale=960:540 [v_scaled]; "
    "[luma_scaled][u_scaled][v_scaled] mergeplanes=0x001020:yuv420p [merged]; "
    "[merged] eq=saturation=0.75, noise=alls=5:allf=t, "
    "geq='lum(X+5.5*(random(floor(Y/96))-0.5),Y)':cb='cb(X,Y)':cr='cr(X,Y)' [outv]"
)

# Temporary file paths
BASE_DIR  = Path.home()
VHS_FILE  = BASE_DIR / "vhs.avi"   # Intermediate video file (no audio)
WAV_FILE  = BASE_DIR / "audio.wav" # Extracted original audio
WAV_FX    = BASE_DIR / "vhs.wav"   # Processed audio
NOISE     = BASE_DIR / "noise.wav" # Generated noise file
MIX       = BASE_DIR / "mix.wav"   # Mixed audio (original + noise)

V_CODEC        = "utvideo"
A_CODEC        = "pcm_f32le"
PIX_FMT        = "yuv420p"
VID_COLORSPACE = "bt709"


def get_input_video_path(cli_path: str | None) -> Path:
    """
    Resolves the input video path.
    If not provided via CLI, prompts the user to enter it.
    """
    if not cli_path:
        print("Drag and drop the video here or type the full path:")
        cli_path = input("Video path: ").strip()

    cli_path = cli_path.strip('"')

    p = Path(cli_path)
    if not p.exists():
        print(f"{utils.EMOJI_ERROR} ERROR: file '{p}' does not exist.", file=sys.stderr)
        sys.exit(1)

    return p.resolve()


def step_0_vhs_fx(input_path: Path) -> None:
    """
    Step 0: Applies the VHS visual effect to the video track.
    - Extracts audio to a separate WAV file.
    - Applies the FFMPEG_FILTER chain to the video.
    - Outputs an intermediate AVI file without audio.
    """
    print(f"#### {utils.EMOJI_VIDEO} Step 0: Applying VHS effect to video ####")

    duration = utils.probe_duration(input_path)

    args = [
        "ffmpeg",
        "-hide_banner",
        "-y",
        "-i", str(input_path),
        "-filter_complex", FFMPEG_FILTER,
        "-c:v", V_CODEC,
        "-pix_fmt", PIX_FMT,
        "-colorspace", VID_COLORSPACE,
        "-color_primaries", VID_COLORSPACE,
        "-color_trc", VID_COLORSPACE,
        "-map", "[outv]",
        str(VHS_FILE),
        "-map", "a",
        "-c:a", A_CODEC,
        str(WAV_FILE),
    ]
    utils.run_ffmpeg_with_progress(args, f"{utils.EMOJI_VIDEO} VHS Video FX", input_path.name, duration)


def step_1_audio_fx(input_path: Path) -> None:
    """
    Step 1: Applies VHS audio effects.
    - Generates brown noise.
    - Mixes noise with the original audio.
    - Applies a low-pass filter to simulate tape frequency response.
    """
    print(f"#### {utils.EMOJI_AUDIO} Step 1: Applying VHS effect to audio ####")
    
    notif_id = utils.send_dunst_notification(
        f"{utils.EMOJI_AUDIO} VHS Audio FX",
        f"Processing audio for:\n{input_path.name}",
        timeout_ms=0
    )

    duration = utils.probe_duration(input_path)

    # 1. Generate brown noise matching the video duration
    args1 = [
        "sox",
        "-n",
        "-r", str(SAMPLE_RATE),
        "-b", str(BIT_DEPTH),
        "-e", "floating-point",
        "-c", str(CHANNELS),
        str(NOISE),
        "synth", str(duration), "brownnoise",
        "vol", f"{DB_VOLUME}",
    ]
    utils.run_command(args1)

    # 2. Mix the original audio with the generated noise
    args2 = [
        "sox",
        "-m",
        "-v", f"{IN_VOL}", str(WAV_FILE),
        "-v", f"{OUT_VOL}", str(NOISE),
        str(MIX),
    ]
    utils.run_command(args2)

    # 3. Apply low-pass filter
    args3 = [
        "sox",
        str(MIX),
        str(WAV_FX),
        "lowpass",
        str(LOW_PASS_FREQ),
    ]
    utils.run_command(args3)
    
    utils.close_dunst_notification(notif_id)
    utils.send_dunst_notification(
        f"{utils.EMOJI_AUDIO} VHS Audio FX",
        f"Audio processing complete:\n{input_path.name}",
        timeout_ms=2000
    )


def step_2_map_inputs(input_path: Path) -> None:
    """
    Step 2: Combines the processed video and audio into the final output file.
    """
    print(f"#### {utils.EMOJI_JOIN} Step 2: Mixing video and audio tracks into a single file ####")

    base_name = input_path.stem
    for ch in ':*?"<>|':
        base_name = base_name.replace(ch, "-")

    final_path = BASE_DIR / f"{base_name}.avi"

    duration = utils.probe_duration(VHS_FILE)

    args = [
        "ffmpeg",
        "-hide_banner",
        "-y",
        "-i", str(VHS_FILE),
        "-i", str(WAV_FX),
        "-map", "0:v",
        "-map", "1:a",
        "-c", "copy",
        str(final_path),
    ]
    utils.run_ffmpeg_with_progress(args, f"{utils.EMOJI_JOIN} VHS Muxing", final_path.name, duration)

    print(f"{utils.EMOJI_SUCCESS} Final file: {final_path}")


def step_3_clean() -> None:
    """
    Step 3: Cleans up temporary files created during the process.
    """
    print(f"#### {utils.EMOJI_PROCESS} Step 3: Cleaning temp files ####")
    for f in (NOISE, MIX, VHS_FILE, WAV_FX, WAV_FILE):
        try:
            f.unlink(missing_ok=True)
        except Exception:
            pass


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Apply VHS (video + audio) effect to an input video file."
    )
    parser.add_argument(
        "input",
        nargs="?",
        help="Input video path (optional; if omitted it will be asked on the console).",
    )
    args = parser.parse_args()

    input_path = get_input_video_path(args.input)

    global BASE_DIR, VHS_FILE, WAV_FILE, WAV_FX, NOISE, MIX
    BASE_DIR = input_path.parent
    VHS_FILE = BASE_DIR / "vhs.avi"
    WAV_FILE = BASE_DIR / "audio.wav"
    WAV_FX  = BASE_DIR / "vhs.wav"
    NOISE   = BASE_DIR / "noise.wav"
    MIX     = BASE_DIR / "mix.wav"

    step_0_vhs_fx(input_path)
    step_1_audio_fx(input_path)
    step_2_map_inputs(input_path)
    step_3_clean()


if __name__ == "__main__":
    main()
