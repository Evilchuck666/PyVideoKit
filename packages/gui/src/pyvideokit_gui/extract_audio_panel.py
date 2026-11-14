from pathlib import Path

from PySide6.QtWidgets import QVBoxLayout

from pyvideokit_gui._base_panel import BasePanel
from pyvideokit_libs import extract_audio


class ExtractAudioPanel(BasePanel):
    def _build_ui(self, layout: QVBoxLayout):
        self._inputs = self._batch_input_list(layout, "Input files")
        self._output_dir = self._output_dir_row(layout)

    def _run(self):
        paths = [Path(self._inputs.item(i).text()) for i in range(self._inputs.count())]
        if not paths:
            self._status.setText("❌  Add at least one file.")
            return
        out_dir = self._output_dir.text().strip() or None
        self._start_batch(extract_audio, paths, lambda p: {"output": out_dir})
