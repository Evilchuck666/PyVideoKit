from pathlib import Path

from PySide6.QtWidgets import QDoubleSpinBox, QHBoxLayout, QLabel, QVBoxLayout

from pyvideokit_gui._base_panel import BasePanel
from pyvideokit_libs import trim_video


class TrimPanel(BasePanel):
    def _build_ui(self, layout: QVBoxLayout):
        self._input = self._input_row(layout, "Input file")

        row = QHBoxLayout()

        start_col = QVBoxLayout()
        start_col.addWidget(QLabel("Start (seconds)"))
        self._start = QDoubleSpinBox()
        self._start.setRange(0, 999999)
        self._start.setDecimals(2)
        start_col.addWidget(self._start)

        end_col = QVBoxLayout()
        end_col.addWidget(QLabel("End (seconds)"))
        self._end = QDoubleSpinBox()
        self._end.setRange(0, 999999)
        self._end.setDecimals(2)
        self._end.setValue(60)
        end_col.addWidget(self._end)

        row.addLayout(start_col)
        row.addLayout(end_col)
        layout.addLayout(row)

        self._output = self._output_row(layout, "Output (optional)")

    def _run(self):
        path = self._input.text().strip()
        if not path:
            self._status.setText("❌  Select an input file.")
            return
        output = self._output.text().strip() or None
        self._start_worker(
            trim_video,
            Path(path),
            self._start.value(),
            self._end.value(),
            output=output,
        )
