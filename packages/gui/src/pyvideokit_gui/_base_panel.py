import shutil
import subprocess
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from pyvideokit_gui._worker import BatchWorker, Worker

_VIDEO_FILTER = "Video files (*.mkv *.mp4 *.mov *.avi *.webm);;All files (*)"
_VIDEO_EXTS = {".mkv", ".mp4", ".mov", ".avi", ".webm"}

_COMPLETE_SOUND = "/usr/share/sounds/freedesktop/stereo/complete.oga"
_SOUND_CMD: list[str] | None = None
for _cmd, _extra in [("paplay", []), ("pw-play", []), ("ffplay", ["-nodisp", "-autoexit", "-loglevel", "quiet"])]:
    if shutil.which(_cmd):
        _SOUND_CMD = [_cmd, *_extra, _COMPLETE_SOUND]
        break


class DropLineEdit(QLineEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls:
            self.setText(urls[0].toLocalFile())


class DropListWidget(QListWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAcceptDrops(True)
        self.setDragDropMode(QAbstractItemView.DragDrop)
        self.setDefaultDropAction(Qt.MoveAction)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragMoveEvent(event)

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                path = url.toLocalFile()
                if Path(path).suffix.lower() in _VIDEO_EXTS:
                    self.addItem(path)
            event.acceptProposedAction()
        else:
            super().dropEvent(event)


class BasePanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._worker = None
        self.setAcceptDrops(True)
        root = QVBoxLayout(self)
        root.setAlignment(Qt.AlignTop)
        root.setSpacing(10)
        root.setContentsMargins(20, 20, 20, 20)
        self._build_ui(root)
        root.addStretch()
        self._build_run_section(root)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        paths = [u.toLocalFile() for u in event.mimeData().urls()]
        if paths:
            self._on_panel_drop(paths)

    def _on_panel_drop(self, paths: list):
        if hasattr(self, "_inputs"):
            for p in paths:
                self._inputs.addItem(p)
        elif hasattr(self, "_input"):
            self._input.setText(paths[0])

    def _build_ui(self, layout: QVBoxLayout):
        raise NotImplementedError

    def _run(self):
        raise NotImplementedError

    # ── file picker helpers ───────────────────────────────────────────────

    def _input_row(self, layout, label="Input file", filter=_VIDEO_FILTER) -> QLineEdit:
        layout.addWidget(QLabel(label))
        row = QHBoxLayout()
        le = DropLineEdit()
        le.setPlaceholderText("Select a file…")
        btn = QPushButton("Browse…")
        row.addWidget(le)
        row.addWidget(btn)
        layout.addLayout(row)
        btn.clicked.connect(lambda: self._browse_open(le, label, filter))
        return le

    def _output_row(self, layout, label="Output (optional)") -> QLineEdit:
        layout.addWidget(QLabel(label))
        row = QHBoxLayout()
        le = DropLineEdit()
        le.setPlaceholderText("Leave empty for default…")
        btn = QPushButton("Browse…")
        row.addWidget(le)
        row.addWidget(btn)
        layout.addLayout(row)
        btn.clicked.connect(lambda: self._browse_save(le, label))
        return le

    def _browse_open(self, le: QLineEdit, title: str, filter: str):
        path, _ = QFileDialog.getOpenFileName(self, title, "", filter)
        if path:
            le.setText(path)

    def _browse_save(self, le: QLineEdit, title: str):
        path, _ = QFileDialog.getSaveFileName(self, title, "")
        if path:
            le.setText(path)

    def _output_dir_row(self, layout, label="Output directory (optional)") -> QLineEdit:
        layout.addWidget(QLabel(label))
        row = QHBoxLayout()
        le = DropLineEdit()
        le.setPlaceholderText("Leave empty to save next to each input file…")
        btn = QPushButton("Browse…")
        row.addWidget(le)
        row.addWidget(btn)
        layout.addLayout(row)
        btn.clicked.connect(lambda: self._browse_dir(le))
        return le

    def _browse_dir(self, le: QLineEdit):
        path = QFileDialog.getExistingDirectory(self, "Select output directory", "")
        if path:
            le.setText(path)

    # ── batch input list ──────────────────────────────────────────────────

    def _batch_input_list(self, layout, label="Input files") -> "DropListWidget":
        layout.addWidget(QLabel(label))
        lst = DropListWidget()
        lst.setSelectionMode(QAbstractItemView.ExtendedSelection)
        lst.setMinimumHeight(120)
        layout.addWidget(lst)
        btns = QHBoxLayout()
        add_btn = QPushButton("Add files…")
        rm_btn = QPushButton("Remove selected")
        btns.addWidget(add_btn)
        btns.addWidget(rm_btn)
        layout.addLayout(btns)
        add_btn.clicked.connect(lambda: self._batch_add(lst))
        rm_btn.clicked.connect(lambda: self._batch_remove(lst))
        return lst

    def _batch_add(self, lst):
        paths, _ = QFileDialog.getOpenFileNames(self, "Add video files", "", _VIDEO_FILTER)
        for p in paths:
            lst.addItem(p)

    def _batch_remove(self, lst):
        for item in lst.selectedItems():
            lst.takeItem(lst.row(item))

    # ── worker ────────────────────────────────────────────────────────────

    def _start_worker(self, fn, *args, **kwargs):
        self._progress.setValue(0)
        self._status.setText("Running…")
        self._run_btn.setEnabled(False)
        self._worker = Worker(fn, args, kwargs)
        self._worker.progress.connect(lambda pct: self._progress.setValue(int(pct)))
        self._worker.finished.connect(self._on_finished)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    def _start_batch(self, fn, paths, make_kwargs):
        self._progress.setValue(0)
        self._progress_item.setValue(0)
        self._status.setText(f"Starting batch ({len(paths)} files)…")
        self._run_btn.setEnabled(False)
        self._worker = BatchWorker(fn, paths, make_kwargs)
        self._worker.progress.connect(lambda pct: self._progress.setValue(int(pct)))
        self._worker.item_progress.connect(lambda pct: self._progress_item.setValue(int(pct)))
        self._worker.item_status.connect(self._status.setText)
        self._worker.finished.connect(self._on_batch_finished)
        self._worker.start()

    def _on_batch_finished(self, errors):
        n = len(self._worker._paths)
        self._run_btn.setEnabled(True)
        if errors:
            self._progress.setValue(0)
            self._progress_item.setValue(0)
            self._status.setText(f"❌  {len(errors)} error(s) — {errors[0]}")
        else:
            self._progress.setValue(100)
            self._progress_item.setValue(100)
            self._status.setText(f"✅  Batch complete ({n} files)")
            self._play_complete_sound()

    # ── run section ───────────────────────────────────────────────────────

    def _build_run_section(self, layout):
        self._run_btn = QPushButton("▶  Run")
        self._run_btn.setFixedHeight(36)
        self._run_btn.clicked.connect(self._run)
        layout.addWidget(self._run_btn)

        if hasattr(self, "_inputs"):
            self._progress_item = QProgressBar()
            self._progress_item.setRange(0, 100)
            self._progress_item.setValue(0)
            self._progress_item.setFormat("Current: %p%")
            layout.addWidget(self._progress_item)

        self._progress = QProgressBar()
        self._progress.setRange(0, 100)
        self._progress.setValue(0)
        if hasattr(self, "_inputs"):
            self._progress.setFormat("Overall: %p%")
        layout.addWidget(self._progress)

        self._status = QLabel("")
        layout.addWidget(self._status)

    def _play_complete_sound(self):
        if _SOUND_CMD:
            subprocess.Popen(_SOUND_CMD, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def _on_finished(self, result):
        self._progress.setValue(100)
        self._status.setText(f"✅  Done → {Path(str(result)).name}")
        self._run_btn.setEnabled(True)
        self._play_complete_sound()

    def _on_error(self, msg):
        self._progress.setValue(0)
        self._status.setText(f"❌  {msg}")
        self._run_btn.setEnabled(True)
