from pathlib import Path

from PySide6.QtWidgets import QCheckBox, QHBoxLayout, QSpinBox, QVBoxLayout

from pyvideokit_gui._base_panel import BasePanel
from pyvideokit_libs import convert_to_ffv1


class ConvertPanel(BasePanel):
    def _build_ui(self, layout: QVBoxLayout):
        self._inputs = self._batch_input_list(layout, "Input files")

        fps_row = QHBoxLayout()
        self._fps_override = QCheckBox("Override FPS")
        self._fps = QSpinBox()
        self._fps.setRange(1, 240)
        self._fps.setValue(60)
        self._fps.setEnabled(False)
        self._fps_override.toggled.connect(self._fps.setEnabled)
        fps_row.addWidget(self._fps_override)
        fps_row.addWidget(self._fps)
        fps_row.addStretch()
        layout.addLayout(fps_row)

        self._output_dir = self._output_dir_row(layout)

    def _run(self):
        paths = [Path(self._inputs.item(i).text()) for i in range(self._inputs.count())]
        if not paths:
            self._status.setText("❌  Add at least one file.")
            return
        fps = self._fps.value() if self._fps_override.isChecked() else None
        out_dir = self._output_dir.text().strip() or None
        self._start_batch(convert_to_ffv1, paths, lambda p: {"fps": fps, "output": out_dir})
