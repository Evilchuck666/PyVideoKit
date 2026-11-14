from PySide6.QtCore import QThread, Signal


class Worker(QThread):
    progress = Signal(float)
    finished = Signal(object)
    error = Signal(str)

    def __init__(self, fn, args=(), kwargs=None):
        super().__init__()
        self._fn = fn
        self._args = args
        self._kwargs = dict(kwargs or {})
        self._kwargs["on_progress"] = self.progress.emit

    def run(self):
        try:
            result = self._fn(*self._args, **self._kwargs)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class BatchWorker(QThread):
    progress = Signal(float)
    item_progress = Signal(float)
    item_status = Signal(str)
    finished = Signal(list)

    def __init__(self, fn, paths, make_kwargs):
        super().__init__()
        self._fn = fn
        self._paths = paths
        self._make_kwargs = make_kwargs

    def run(self):
        errors = []
        total = len(self._paths)
        for i, path in enumerate(self._paths):
            self.item_status.emit(f"Processing {i + 1}/{total}: {path.name}…")
            self.item_progress.emit(0)
            base = i / total * 100

            def on_progress(pct, _base=base):
                self.item_progress.emit(pct)
                self.progress.emit(_base + pct / total)

            try:
                kwargs = self._make_kwargs(path)
                kwargs["on_progress"] = on_progress
                self._fn(path, **kwargs)
            except Exception as e:
                errors.append(f"{path.name}: {e}")
            self.progress.emit((i + 1) / total * 100)
        self.finished.emit(errors)
