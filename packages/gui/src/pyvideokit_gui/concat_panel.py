from pathlib import Path

from PySide6.QtWidgets import (
    QAbstractItemView,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from pyvideokit_gui._base_panel import BasePanel, DropListWidget, _VIDEO_EXTS
from pyvideokit_libs import join_videos


class ConcatPanel(BasePanel):
    def _build_ui(self, layout: QVBoxLayout):
        layout.addWidget(QLabel("Video files (add at least 2, drag to reorder)"))

        self._list = DropListWidget()
        self._list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self._list.setMinimumHeight(120)
        layout.addWidget(self._list)

        btns = QHBoxLayout()
        add_btn = QPushButton("Add files…")
        rm_btn = QPushButton("Remove selected")
        btns.addWidget(add_btn)
        btns.addWidget(rm_btn)
        layout.addLayout(btns)

        add_btn.clicked.connect(self._add_files)
        rm_btn.clicked.connect(self._remove_selected)

        self._output = self._output_row(layout, "Output (optional)")

    def _add_files(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self, "Add video files", "",
            "Video files (*.mkv *.mp4 *.mov *.avi *.webm);;All files (*)",
        )
        for p in paths:
            self._list.addItem(p)

    def _remove_selected(self):
        for item in self._list.selectedItems():
            self._list.takeItem(self._list.row(item))

    def _on_panel_drop(self, paths: list):
        for p in paths:
            if Path(p).suffix.lower() in _VIDEO_EXTS:
                self._list.addItem(p)

    def _run(self):
        paths = [Path(self._list.item(i).text()) for i in range(self._list.count())]
        if len(paths) < 2:
            self._status.setText("❌  Add at least 2 video files.")
            return
        output = self._output.text().strip() or None
        self._start_worker(join_videos, paths, output=output)
