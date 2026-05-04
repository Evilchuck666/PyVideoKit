# 🎥 PyVideoKit

![Python](https://img.shields.io/badge/python-%3E%3D3.10-blue)
![License](https://img.shields.io/badge/license-GPLv3-green)

Monorepo raíz de PyVideoKit, un conjunto de herramientas Python para procesamiento de vídeo basado en FFmpeg.

---

## 📦 Subdirectorios

- 📚 **PyVideoKit-Libs/** — Librería Python principal. Contiene las funciones de procesamiento de vídeo (FFmpeg, FFprobe, SoX). Es la dependencia base del resto de paquetes.
- 💻 **PyVideoKit-CLI/** — Interfaz de línea de comandos construida sobre PyVideoKit-Libs. Expone cada operación como un comando independiente (`pvk`, `trim-video`, `fade-video`, etc.).
- 🖥️ **PyVideoKit-GUI/** — Interfaz gráfica de usuario. En desarrollo.
- 🏗️ **AUR/** — PKGBUILD para Arch Linux. Construye e instala `python-pyvideokit-libs` y `python-pyvideokit-cli` para Pacman.

---

## 🔧 Build

```bash
make help        # muestra todos los targets disponibles
make build-libs  # construye el wheel de PyVideoKit-Libs
make build-cli   # construye el wheel de PyVideoKit-CLI
make build-all   # construye ambos wheels
make aur         # construye e instala los paquetes AUR con makepkg
```
