from PySide6.QtWidgets import QMainWindow, QTabWidget

from pyvideokit_gui.concat_panel import ConcatPanel
from pyvideokit_gui.convert_panel import ConvertPanel
from pyvideokit_gui.extract_audio_panel import ExtractAudioPanel
from pyvideokit_gui.fade_panel import FadePanel
from pyvideokit_gui.trim_panel import TrimPanel
from pyvideokit_gui.vhs_panel import VhsPanel
from pyvideokit_gui.youtube_panel import YouTubePanel


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyVideoKit")
        self.setMinimumSize(670, 460)

        tabs = QTabWidget()
        tabs.addTab(ConvertPanel(), "🎞️  Convert to FFV1")
        tabs.addTab(TrimPanel(), "✂️  Trim")
        tabs.addTab(ConcatPanel(), "🔗  Concat")
        tabs.addTab(FadePanel(), "🎬  Fade")
        tabs.addTab(VhsPanel(), "📼  VHS Effect")
        tabs.addTab(ExtractAudioPanel(), "🔊  Extract Audio")
        tabs.addTab(YouTubePanel(), "📺  YouTube")

        self.setCentralWidget(tabs)
