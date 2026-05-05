# 🎥 PyVideoKit

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

## 🗂️ Subprojects

- 📚 **[PyVideoKit-Libs](PyVideoKit-Libs/)** — Core Python library. All video processing functions built on top of FFmpeg, FFprobe, and SoX. Base dependency for the other packages.
- 💻 **[PyVideoKit-CLI](PyVideoKit-CLI/)** — Command-line interface built on PyVideoKit-Libs. Each operation is exposed as a standalone command (`pvk`, `trim-video`, `fade-video`, etc.).
- 🖥️ **[PyVideoKit-GUI](PyVideoKit-GUI/)** — PySide6 desktop GUI. Tabbed interface with real-time progress tracking for all operations.
- 🏗️ **[AUR](AUR/)** — PKGBUILD for Arch Linux. Builds and installs `python-pyvideokit-libs`, `python-pyvideokit-cli`, and `python-pyvideokit-gui` via pacman.

---

## 🔧 Build

```bash
make help          # show all available targets
make build-all     # build all wheels (Libs + CLI + GUI + meta-package)
make install-all   # build and install all packages locally
make upload        # upload all wheels to PyPI
make aur           # build and install AUR packages with makepkg
```

---

## ⚖️ License

This project is licensed under the GPLv3 License — see the [LICENSE](LICENSE) file for details.
