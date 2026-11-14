from pathlib import Path

from PySide6.QtWidgets import QDoubleSpinBox, QHBoxLayout, QLabel, QVBoxLayout

from pyvideokit_gui._base_panel import BasePanel
from pyvideokit_libs import fade_video


class FadePanel(BasePanel):
    def _build_ui(self, layout: QVBoxLayout):
        self._input = self._input_row(layout, "Input file (FFV1)")

        row = QHBoxLayout()

        fi_col = QVBoxLayout()
        fi_col.addWidget(QLabel("Fade-in (seconds, 0 = disabled)"))
        self._fade_in = QDoubleSpinBox()
        self._fade_in.setRange(0, 60)
        self._fade_in.setDecimals(2)
        fi_col.addWidget(self._fade_in)

        fo_col = QVBoxLayout()
        fo_col.addWidget(QLabel("Fade-out (seconds, 0 = disabled)"))
        self._fade_out = QDoubleSpinBox()
        self._fade_out.setRange(0, 60)
        self._fade_out.setDecimals(2)
        fo_col.addWidget(self._fade_out)

        row.addLayout(fi_col)
        row.addLayout(fo_col)
        layout.addLayout(row)

        self._output = self._output_row(layout, "Output (optional)")

    def _run(self):
        path = self._input.text().strip()
        if not path:
            self._status.setText("❌  Select an input file.")
            return
        fi = self._fade_in.value() or None
        fo = self._fade_out.value() or None
        if not fi and not fo:
            self._status.setText("❌  Set at least one fade duration.")
            return
        output = self._output.text().strip() or None
        self._start_worker(
            fade_video,
            Path(path),
            fade_in=fi,
            fade_out=fo,
            output=output,
        )
