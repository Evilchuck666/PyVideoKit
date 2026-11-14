# 🎬 PyVideoKit-GUI

![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20GNU%2FLinux%20%7C%20macOS-blue)
![Python](https://img.shields.io/badge/python-%3E%3D3.10-blue)
![PySide6](https://img.shields.io/badge/PySide6-%3E%3D6.2-blue)
![Requires](https://img.shields.io/badge/requires-FFmpeg%2C%20SoX-blue)
[![License](https://img.shields.io/badge/license-GPLv3-green)](LICENSE)
[![Latest release](https://img.shields.io/github/v/release/Evilchuck666/PyVideoKit-GUI?label=download&sort=semver)](https://github.com/Evilchuck666/PyVideoKit-GUI/releases/latest)
[![Build and tests](https://github.com/Evilchuck666/PyVideoKit-GUI/actions/workflows/release.yml/badge.svg?branch=main)](https://github.com/Evilchuck666/PyVideoKit-GUI/actions/workflows/release.yml)

Graphical interface for PyVideoKit — FFmpeg-based video processing. Provides the same operations as [PyVideoKit-CLI](../PyVideoKit-CLI) through a PySide6 desktop application with real-time progress tracking, drag-and-drop input, and batch processing.

---

## ✨ Features

- 🎞️ **Convert to FFV1** — batch-convert multiple videos to lossless FFV1/MKV masters
- ✂️ **Trim** — cut a segment by start/end time with stream copy (no re-encoding)
- 🔗 **Concatenate** — join multiple videos with drag-and-drop reordering and multi-selection
- 🎬 **Fade** — fade-in and/or fade-out on an FFV1 master
- 📼 **VHS effect** — batch-apply retro visual noise, color bleed, and audio degradation
- 🔊 **Extract audio** — batch-export audio tracks to uncompressed WAV (PCM 16-bit)
- 📺 **Prepare for YouTube** — batch-encode to ProRes 422 HQ MOV, upscaled to 4K
- 🖱️ **Drag & drop** — drop files anywhere on any panel; drop multiple files onto batch panels
- 📁 **Output directory** — optionally redirect all batch output to a chosen folder

---

## 📦 Requirements

- **Python** ≥ 3.10
- **PySide6** ≥ 6.2
- **FFmpeg** and **FFprobe** available in `PATH`
- **SoX** available in `PATH` (required by VHS effect)
- **PyVideoKit-Libs** — installed automatically as a dependency
- **`paplay`**, **`pw-play`**, or **`ffplay`** in `PATH` *(optional — for completion sound)*

---

## 🔧 Installation

### 🏗️ Arch Linux (AUR)

```bash
yay -S python-pyvideokit-gui
```

FFmpeg, FFprobe, SoX, PySide6, and PyVideoKit-Libs are installed automatically as pacman dependencies.

### 🐍 Other systems (pip)

```bash
pip install PyVideoKit-GUI
```

Make sure **FFmpeg**, **FFprobe**, and **SoX** are available in your `PATH`.

---

## 🖥️ Desktop Integration

Arch Linux users get the launcher entry and icon automatically via the AUR package. For all other systems, create them manually:

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

**3. Refresh the icon cache** *(maybe required in some desktop environments)*:

```bash
gtk-update-icon-cache ~/.local/share/icons/hicolor/
```

PyVideoKit will now appear in your application launcher.

---

## 🚀 Usage

```bash
pvk-gui
```

The application opens a tabbed window. Each tab corresponds to one operation:

| Tab                 | Operation                                                      | Batch |
|---------------------|----------------------------------------------------------------|:-----:|
| 🎞️ Convert to FFV1 | Convert videos to lossless FFV1/MKV masters                    |   ✅   |
| ✂️ Trim             | Cut a segment by start/end time (no re-encoding)               |   —   |
| 🔗 Concat           | Join multiple videos (drag to reorder, multi-select to remove) |   —   |
| 🎬 Fade             | Add fade-in and/or fade-out                                    |   —   |
| 📼 VHS Effect       | Apply retro VHS visual and audio effect                        |   ✅   |
| 🔊 Extract Audio    | Export audio tracks to WAV                                     |   ✅   |
| 📺 YouTube          | Encode to ProRes 422 HQ MOV for upload                         |   ✅   |

Batch panels accept multiple input files via drag & drop or the "Add files…" button, and optionally redirect output to a chosen directory. They show two progress bars: one for the current file and one for the overall batch.

All operations run in a background thread. A system sound plays on completion.

---

## 🔄 Typical Workflow

```
🎞️ Convert to FFV1  →  ✂️ Trim / 🎬 Fade / 📼 VHS Effect  →  📺 YouTube
```

> Operations that re-encode (Fade, VHS Effect, YouTube) expect an FFV1 `.mkv` as input.

---

## ⚖️ License

This project is licensed under the GPLv3 License — see the [LICENSE](LICENSE) file for details.
