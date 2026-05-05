# 🎬 PyVideoKit

![Python](https://img.shields.io/badge/python-%3E%3D3.10-blue)
![License](https://img.shields.io/badge/license-GPLv3-green)

FFmpeg-based video processing toolkit for Python — featuring a library, a CLI, and a desktop GUI.

---

## 📦 Installation

### 🏗️ Arch Linux (AUR)

Install all three packages at once:

```bash
yay -S python-pyvideokit-libs python-pyvideokit-cli python-pyvideokit-gui
```

System dependencies (FFmpeg, FFprobe, SoX) are pulled in automatically by pacman.

### 🐍 Other systems (pip)

```bash
pip install PyVideoKit
```

This installs PyVideoKit-Libs, PyVideoKit-CLI, and PyVideoKit-GUI in one go.
Make sure **FFmpeg**, **FFprobe**, and **SoX** are available in your `PATH`.

---

## 🖥️ Desktop Integration

Non-Arch users can add PyVideoKit to their application launcher by manually creating the `.desktop` entry and icon.

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

## 🗂️ Subprojects

- 📚 **[PyVideoKit-Libs](PyVideoKit-Libs/)** — Core Python library. All video processing functions built on top of FFmpeg, FFprobe, and SoX. Base dependency for the other packages.
- 💻 **[PyVideoKit-CLI](PyVideoKit-CLI/)** — Command-line interface built on PyVideoKit-Libs. Each operation is exposed as a standalone command (`pvk`, `trim-video`, `fade-video`, etc.).
- 🖥️ **[PyVideoKit-GUI](PyVideoKit-GUI/)** — PySide6 desktop GUI. Tabbed interface with real-time progress tracking for all operations.
- 🏗️ **[arch/](arch/)** — PKGBUILD and .SRCINFO for Arch Linux. Builds and installs `python-pyvideokit-libs`, `python-pyvideokit-cli`, and `python-pyvideokit-gui` via pacman. Mirrors the [AUR package](https://aur.archlinux.org/packages/pyvideokit).

---

## 🔧 Build

```bash
make help          # show all available targets
make build-all     # build all wheels (Libs + CLI + GUI + meta-package)
make install-all   # build and install all packages locally
make aur           # build and install AUR packages with makepkg
```

---

## ⚖️ License

This project is licensed under the GPLv3 License — see the [LICENSE](LICENSE) file for details.
