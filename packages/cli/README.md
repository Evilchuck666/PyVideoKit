# 🎬 PyVideoKit-CLI

![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20GNU%2FLinux%20%7C%20macOS-blue)
![Python](https://img.shields.io/badge/python-%3E%3D3.10-blue)
![Requires](https://img.shields.io/badge/requires-FFmpeg%2C%20SoX-blue)
[![License](https://img.shields.io/badge/license-GPLv3-green)](LICENSE)
[![Latest release](https://img.shields.io/github/v/release/Evilchuck666/PyVideoKit-CLI?label=download&sort=semver)](https://github.com/Evilchuck666/PyVideoKit-CLI/releases/latest)
[![Build and tests](https://github.com/Evilchuck666/PyVideoKit-CLI/actions/workflows/release.yml/badge.svg?branch=main)](https://github.com/Evilchuck666/PyVideoKit-CLI/actions/workflows/release.yml)

Command-line tool for FFmpeg-based video processing: trim, concatenate, fade, apply a VHS effect, extract audio, archive to lossless FFV1, and export for YouTube — all from a single `pvk` command.

---

## ✨ Features

- 📼 **VHS effect** — retro visual noise, color bleed, and audio degradation
- ✂️ **Trim** — cut a segment by start/end time with stream copy (no re-encoding)
- 🔗 **Concatenate** — join two or more videos with stream copy
- 🎬 **Fade** — fade-in and/or fade-out on an FFV1 master
- 🔊 **Extract audio** — dump the audio track to uncompressed WAV (PCM 16-bit)
- 🎞️ **Convert to FFV1** — create a lossless MKV master for editing
- 📺 **Prepare for YouTube** — encode to ProRes 422 HQ MOV, upscaled to 4K

---

## 📦 Requirements

- **Python** ≥ 3.10
- **FFmpeg** and **FFprobe** available in `PATH`
- **SoX** available in `PATH` (required by `apply-vhs-effect`)
- **PyVideoKit-Libs** — installed automatically as a dependency

---

## 🔧 Installation

### 🏗️ Arch Linux (AUR)

```bash
yay -S python-pyvideokit-cli
```

FFmpeg, FFprobe, SoX, and PyVideoKit-Libs are installed automatically as pacman dependencies.

### 🐍 Other systems (pip)

```bash
pip install PyVideoKit-CLI
```

Make sure **FFmpeg**, **FFprobe**, and **SoX** are available in your `PATH`.

This installs the `pvk` command group and seven standalone scripts (`trim-video`, `concat-videos`, etc.).

---

## 🖥️ Desktop Integration

If you also have [PyVideoKit-GUI](https://pypi.org/project/PyVideoKit-GUI/) installed, you can add it to your application launcher. Arch Linux users get this automatically via the AUR package. For all other systems:

**1. Save the icon:**

```bash
mkdir -p ~/.local/share/icons/hicolor/scalable/apps
cat > ~/.local/share/icons/hicolor/scalable/apps/pvk-gui.svg << 'EOF'
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48">
  <rect x="4" y="14" width="40" height="30" rx="3" fill="#2d3561"/>
  <rect x="10" y="19" width="28" height="20" rx="2" fill="#1a2038"/>
  <polygon points="18,21 18,37 33,29" fill="#ff6b6b"/>
  <rect x="4" y="6" width="40" height="8" rx="2" fill="#ff6b6b"/>
  <rect x="11" y="6" width="6" height="8" fill="#ffffff"/>
  <rect x="23" y="6" width="6" height="8" fill="#ffffff"/>
  <rect x="35" y="6" width="5" height="8" fill="#ffffff"/>
</svg>
EOF
```

**2. Create the `.desktop` entry:**

```bash
mkdir -p ~/.local/share/applications
cat > ~/.local/share/applications/pvk-gui.desktop << 'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=PyVideoKit
GenericName=Video Processing Tool
Comment=FFmpeg-based video processing GUI
Exec=pvk-gui
Icon=pvk-gui
Categories=AudioVideo;Video;AudioVideoEditing;
Terminal=false
Keywords=video;ffmpeg;trim;fade;vhs;youtube;convert;
EOF
```

**3. Refresh the icon cache** *(may be required on some desktop environments)*:

```bash
gtk-update-icon-cache ~/.local/share/icons/hicolor/
```

PyVideoKit will now appear in your application launcher.

---

## 🚀 Usage

```
pvk [--version] COMMAND [ARGS]...
```

Each command is also available as a standalone script — `trim-video ...` is equivalent to `pvk trim-video ...`.

---

### 📼 `apply-vhs-effect`

Apply a retro VHS visual and audio effect to a video.

```
pvk apply-vhs-effect INPUT [-o OUTPUT]
```

| Argument / Option | Description |
|---|---|
| `INPUT` | Input video file (must have an audio stream) |
| `-o, --output` | Output file or directory (optional) |

---

### 🔗 `concat-videos`

Concatenate two or more videos using stream copy (no re-encoding).

```
pvk concat-videos VIDEO VIDEO... [-o OUTPUT]
```

| Argument / Option | Description |
|---|---|
| `VIDEO` | Two or more input video files |
| `-o, --output` | Output file or directory (optional) |

---

### 🎞️ `convert-to-ffv1`

Convert a video to lossless FFV1/MKV format. Use this to create an editing master before applying effects.

```
pvk convert-to-ffv1 INPUT [--fps FPS] [-o OUTPUT]
```

| Argument / Option | Default | Description |
|---|---|---|
| `INPUT` | | Input video file |
| `--fps` | source fps | Force an output frame rate (integer) |
| `-o, --output` | | Output file or directory (optional) |

---

### 🔊 `extract-audio`

Extract the audio track to an uncompressed WAV file (PCM 16-bit).

```
pvk extract-audio INPUT [-o OUTPUT]
```

| Argument / Option | Description |
|---|---|
| `INPUT` | Input video file |
| `-o, --output` | Output file or directory (optional) |

---

### 🎬 `fade-video`

Add a fade-in and/or fade-out to an FFV1 video.

```
pvk fade-video INPUT [--fade SECS] [--fade-in SECS] [--fade-out SECS] [-o OUTPUT]
```

| Option | Default | Description |
|---|---|---|
| `--fade` | | Shorthand: apply the same duration to both fade-in and fade-out |
| `--fade-in` | | Fade-in duration in seconds |
| `--fade-out` | | Fade-out duration in seconds |
| `-o, --output` | | Output file or directory (optional) |

`--fade` is a shorthand: it sets whichever of `--fade-in` and `--fade-out` you did not give explicitly.

---

### 📺 `prepare-youtube`

Encode an FFV1 master to ProRes 422 HQ MOV, upscaled to 4K, optimized for YouTube upload.

```
pvk prepare-youtube INPUT [-o OUTPUT]
```

| Argument / Option | Description |
|---|---|
| `INPUT` | Input FFV1 video file |
| `-o, --output` | Output file or directory (optional) |

---

### ✂️ `trim-video`

Cut a segment from a video using stream copy (no re-encoding).

```
pvk trim-video INPUT --start TIME --end TIME [-o OUTPUT]
```

| Argument / Option | Description |
|---|---|
| `INPUT` | Input video file |
| `--start` | Start time: seconds (`90`, `90.5`) or `HH:MM:SS` |
| `--end` | End time: seconds or `HH:MM:SS` |
| `-o, --output` | Output file or directory (optional) |

---

## 🔄 Typical Workflow

```bash
# 1. Create a lossless master from any source video
pvk convert-to-ffv1 recording.mp4 -o master.mkv

# 2. Trim to the desired range
pvk trim-video master.mkv --start 00:00:10 --end 00:05:30 -o trimmed.mkv

# 3. Add a 1-second fade in and out
pvk fade-video trimmed.mkv --fade 1.0 -o faded.mkv

# 4. Export for YouTube
pvk prepare-youtube faded.mkv -o final_upload.mov
```

> All operations display a real-time progress bar in the terminal.
