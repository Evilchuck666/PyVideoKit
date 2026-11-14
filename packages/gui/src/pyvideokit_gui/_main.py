import sys

from PySide6.QtWidgets import QApplication

from pyvideokit_gui._main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("PyVideoKit")
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
