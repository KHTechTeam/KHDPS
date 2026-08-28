# This application was written by Thomas Young from NDL in May of 2025 with the assitance of Chatgpt.
# This application is for the purpose of examining data related to Electrochemical Aptamer Sensors.

import sys
import os
import logging

# --- Logging setup happens BEFORE Qt starts ---
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename="logs/app_debug.log",
    filemode="w",              # use "a" to append instead
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

class PrintLogger:
    def write(self, message):
        if message.strip():
            logging.debug(message.strip())
    def flush(self):
        pass

sys.stdout = PrintLogger()
sys.stderr = PrintLogger()

def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logging.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

sys.excepthook = handle_exception

# --- Qt imports AFTER logging is ready ---
# "resources" (the compiled Qt resource module) lives in "Resource Files",
# a sibling folder to this file's own "Python Files" folder -- a plain
# `import resources` only searches this file's own directory and installed
# packages, so it can't find it there by default. Add it to sys.path first.
# This also needs to be a real filesystem path (not the _MEIPASS/frozen
# lookup used elsewhere) since this runs before PyInstaller's bootloader
# has fully set up -- and the matching --paths "Resource Files" build flag
# is what lets PyInstaller's static analysis find and bundle this module
# in the first place.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Resource Files"))
import resources
try:
    import pyi_splash  # only exists in the frozen EXE
except ImportError:
    pyi_splash = None
from PySide6.QtWidgets import QApplication, QDialog, QVBoxLayout, QLabel, QProgressBar
from PySide6.QtGui import QIcon, QPalette, QColor, QPixmap
from PySide6.QtCore import Qt, QTimer

from mainwindow import MainWindow

# --- KHDPS brand colors ---
COLOR_DEEP_NAVY = "#0f172a"
COLOR_BRIGHT_BLUE = "#2d65a3"
COLOR_SIGNAL_GOLD = "#fbbf24"
COLOR_SLATE_DARK = "#1e293b"
COLOR_SLATE_LIGHT = "#64748b"
COLOR_CANVAS_WHITE = "#ffffff"
COLOR_WASH_GREY = "#f8fafc"


def resource_path(*parts):
    """Resolve a path to a bundled resource, working both when run from
    source and when frozen into a PyInstaller build. In source, resources
    live one folder up from this file (in "Resource Files"). When frozen,
    PyInstaller extracts bundled data next to sys._MEIPASS -- make sure
    your .spec/build command includes:
        --add-data "Resource Files;Resource Files"
    so the same relative layout exists inside the bundle.
    """
    if hasattr(sys, "_MEIPASS"):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, *parts)


ICON_PATH = resource_path("Resource Files", "khdps_icon.ico")
LOGO_PATH = resource_path("Resource Files", "khdps_logo.png")

class SplashScreen(QDialog):
    """Startup splash with logo and progress bar."""
    def __init__(self, parent=None):
        super().__init__(parent)

        # Frameless, on top
        self.setWindowFlags(
            Qt.FramelessWindowHint
            | Qt.Dialog
            | Qt.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        self.setStyleSheet(f"background-color: {COLOR_CANVAS_WHITE};")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # --- Logo ---
        logo_label = QLabel(self)
        logo_label.setAlignment(Qt.AlignCenter)

        pix = QPixmap(LOGO_PATH)
        if pix.isNull():
            pix = QPixmap(ICON_PATH)
        if not pix.isNull():
            pix = pix.scaled(256, 256, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(pix)
        else:
            logo_label.setText("KHDPS")
            logo_label.setStyleSheet(f"color: {COLOR_DEEP_NAVY}; font-size: 24pt; font-weight: bold;")

        layout.addWidget(logo_label)

        # --- Status text ---
        self._status_label = QLabel("Starting…", self)
        self._status_label.setAlignment(Qt.AlignCenter)
        self._status_label.setStyleSheet(f"color: {COLOR_SLATE_DARK};")
        layout.addWidget(self._status_label)

        # --- Progress bar ---
        self._progress = QProgressBar(self)
        self._progress.setRange(0, 100)
        self._progress.setValue(0)
        self._progress.setTextVisible(False)
        self._progress.setFixedHeight(16)

        self._progress.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid {COLOR_SLATE_LIGHT};
                border-radius: 8px;
                background-color: {COLOR_WASH_GREY};
            }}
            QProgressBar::chunk {{
                background-color: {COLOR_BRIGHT_BLUE};
                border-radius: 8px;
            }}
        """)

        layout.addWidget(self._progress)

        self.resize(420, 420)

        # Center on primary screen
        screen = QApplication.primaryScreen()
        if screen is not None:
            geo = screen.availableGeometry()
            self.move(
                geo.center().x() - self.width() // 2,
                geo.center().y() - self.height() // 2
            )

    def set_status(self, text: str, value: int | None = None):
        """Update the label and optionally the progress value."""
        self._status_label.setText(text)
        if value is not None:
            self._progress.setValue(value)
        QApplication.processEvents()

def main():
    app = QApplication(sys.argv)

    # Optional: comment this out if you want **pure native** look
    # app.setStyle("Fusion")

    # ---- Selection highlight color (KHDPS brand: Bright Blue) ----
    palette = app.palette()

    highlight_color = QColor(COLOR_BRIGHT_BLUE)
    highlight_text = QColor(COLOR_CANVAS_WHITE)   # white text on blue selection for contrast

    palette.setColor(QPalette.Highlight, highlight_color)
    palette.setColor(QPalette.HighlightedText, highlight_text)
    app.setPalette(palette)

    # ---- Tiny stylesheet: only selections, nothing else ----
    app.setStyleSheet(f"""
        /* Text selection in line edits / text edits */
        QLineEdit, QPlainTextEdit, QTextEdit {{
            selection-background-color: {COLOR_BRIGHT_BLUE};
            selection-color: {COLOR_CANVAS_WHITE};
        }}

        /* Rows/items in lists, trees, tables */
        QAbstractItemView::item:selected:active,
        QAbstractItemView::item:selected:!active {{
            background: {COLOR_BRIGHT_BLUE};
            color: {COLOR_CANVAS_WHITE};
        }}

        /* All push buttons: remove green focus box / default frame */
        #QPushButton:focus,
        QPushButton:default,
        QDialogButtonBox QPushButton:focus,
        QDialogButtonBox QPushButton:default {{
            outline: none;
            border: 1px solid {COLOR_BRIGHT_BLUE};
            border-radius: 6px;
            padding: 4px 10px;
        }}

        /* --- underline color for input boxes --- */
        QLineEdit {{
            border: None;    /* default-ish frame */
            border-radius: 2px;
            padding: 2px;
        }}

        /* color of the bottom line when focused */
        QLineEdit:focus {{
            border: None;    /* keep other sides */
            border-bottom: 2px solid {COLOR_BRIGHT_BLUE};  /* KHDPS accent color */
        }}

        QAbstractSpinBox::up-button,
        QAbstractSpinBox::down-button {{
            width: 0px;
            border: none;
        }}

        QAbstractSpinBox::up-arrow,
        QAbstractSpinBox::down-arrow {{
            image: none;
        }}

        /* Blue underline when focused (gets rid of green accent) */
        QAbstractSpinBox:focus {{
            border: 1px solid palette(Mid);
            border-bottom: 2px solid {COLOR_BRIGHT_BLUE};
            buttonSymbols: None;
        }}
    """)

    # Set application icon for all top-level windows
    app.setWindowIcon(QIcon(ICON_PATH))

    # --- create and show splash ---
    splash = SplashScreen()
    splash.show()
    splash.set_status("Starting KHDPS…", 10)

    splash.set_status("Loading modules…", 30)
    from mainwindow import MainWindow

    # Create main window while splash is visible
    win = MainWindow()
    if pyi_splash is not None:
        pyi_splash.close()
    win.setWindowIcon(QIcon(ICON_PATH))
    splash.set_status("Initializing interface…", 70)

    # Show main window AFTER at least 3 seconds of splash
    def show_main():
        splash.set_status("Ready", 100)
        win.show()
        splash.close()

    # 3000 ms = 3 seconds
    QTimer.singleShot(3000, show_main)

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
