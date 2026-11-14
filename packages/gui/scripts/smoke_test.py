#!/usr/bin/env python3
"""Headless smoke test: drives every panel of the GUI on a short generated clip.

Needs FFmpeg, FFprobe and SoX in PATH and runs Qt with the offscreen platform.
Run it against an installed package (not the src tree) so it checks what ships.
"""

import os
import subprocess
import sys
import tempfile
import time
from importlib.metadata import version
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

import pyvideokit_gui._base_panel as base_panel
from pyvideokit_gui._main_window import MainWindow

TABS = ["ConvertPanel", "TrimPanel", "ConcatPanel", "FadePanel",
        "VhsPanel", "ExtractAudioPanel", "YouTubePanel"]
TIMEOUT_S = 180


def video_codec(path: Path) -> str:
    return subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=codec_name",
         "-of", "default=nk=1:nw=1", str(path)],
        capture_output=True, text=True, check=True,
    ).stdout.strip()


def run_panel(panel) -> str:
    """Press Run, wait for the worker thread and return the status line."""
    panel._run()
    deadline = time.monotonic() + TIMEOUT_S
    while not panel._worker.isFinished():
        if time.monotonic() > deadline:
            sys.exit(f"FAIL {type(panel).__name__}: timed out after {TIMEOUT_S}s")
        QApplication.processEvents()
        time.sleep(0.05)
    QApplication.processEvents()  # deliver the queued finished/error signal
    return panel._status.text()


def check(label: str, panel, path: Path, codec: str | None = None) -> Path:
    status = run_panel(panel)
    if not status.startswith("✅"):
        sys.exit(f"FAIL {label}: {status}")
    if not path.is_file() or path.stat().st_size == 0:
        sys.exit(f"FAIL {label}: {path} is missing or empty")
    if codec and video_codec(path) != codec:
        sys.exit(f"FAIL {label}: expected {codec}, got {video_codec(path)!r}")
    print(f"ok   {label}: {path.name}")
    return path


def main() -> None:
    print(f"PyVideoKit-GUI {version('PyVideoKit-GUI')} on PyVideoKit-Libs {version('PyVideoKit-Libs')}")
    base_panel._SOUND_CMD = None  # keep the completion sound quiet

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    tabs = window.centralWidget()
    panels = {type(tabs.widget(i)).__name__: tabs.widget(i) for i in range(tabs.count())}
    if list(panels) != TABS:
        sys.exit(f"FAIL tabs: expected {TABS}, got {list(panels)}")
    print(f"ok   main window with {len(TABS)} tabs")

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        out = tmp / "out"
        out.mkdir()
        src = tmp / "source.mp4"
        subprocess.run(
            ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
             "-f", "lavfi", "-i", "testsrc2=size=320x240:rate=25:duration=3",
             "-f", "lavfi", "-i", "sine=frequency=440:sample_rate=48000:duration=3",
             "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", str(src)],
            check=True,
        )

        p = panels["ConvertPanel"]
        p._inputs.addItem(str(src))
        master = check("Convert to FFV1", p, tmp / "source_ffv1.mkv", "ffv1")

        p = panels["TrimPanel"]
        p._input.setText(str(master))
        p._start.setValue(0.5)
        p._end.setValue(2.0)
        p._output.setText(str(tmp / "trim.mkv"))
        check("Trim", p, tmp / "trim.mkv")

        p = panels["ConcatPanel"]
        p._list.addItem(str(master))
        p._list.addItem(str(master))
        p._output.setText(str(tmp / "joined.mkv"))
        check("Concat", p, tmp / "joined.mkv")

        p = panels["FadePanel"]
        p._input.setText(str(master))
        p._fade_in.setValue(0.5)
        p._fade_out.setValue(0.5)
        check("Fade", p, tmp / "source_ffv1_fade.mkv", "ffv1")

        for name, label, result, codec in [
            ("VhsPanel", "VHS Effect", "source_ffv1_vhs.mkv", "ffv1"),
            ("ExtractAudioPanel", "Extract Audio", "source_ffv1.wav", None),
            ("YouTubePanel", "YouTube", "source_ffv1_youtube.mov", "prores"),
        ]:
            p = panels[name]
            p._inputs.addItem(str(master))
            p._output_dir.setText(str(out))
            check(label, p, out / result, codec)

        if video_codec(master) != "ffv1":
            sys.exit("FAIL the FFV1 master was modified by a later step")

    window.close()

    # The console script must start the event loop and keep running.
    try:
        subprocess.run(["pvk-gui"], timeout=5, capture_output=True, check=True)
        sys.exit("FAIL pvk-gui exited on its own")
    except subprocess.TimeoutExpired:
        print("ok   pvk-gui starts and keeps running")
    except subprocess.CalledProcessError as e:
        sys.exit(f"FAIL pvk-gui crashed (exit {e.returncode}):\n{e.stderr.decode(errors='replace')}")

    print("All smoke tests passed.")


if __name__ == "__main__":
    main()
