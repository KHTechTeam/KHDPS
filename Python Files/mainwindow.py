# This Python file uses the following encoding: utf-8
import sys
import os
import re
import json
import pandas as pd
import numpy as np
import datetime
import threading
import time
import queue
import matplotlib as mpl
import matplotlib.backends.backend_pdf
csv_write_lock = threading.RLock()

from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget
from PySide6.QtWidgets import QFileDialog
from PySide6.QtCore import QStringListModel
from PySide6.QtCore import QRunnable, QThreadPool, Slot, QObject, Signal
from PySide6.QtWidgets import QInputDialog
from PySide6.QtWidgets import QAbstractItemView
from PySide6.QtWidgets import QWidget, QFormLayout
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QMdiArea
from PySide6.QtWidgets import QDialog, QTableWidgetItem
from PySide6.QtCore import QSignalBlocker, QItemSelectionModel
from PySide6.QtCore import QEvent
from PySide6.QtCore import QFileSystemWatcher
from PySide6.QtWidgets import QHeaderView, QVBoxLayout
from PySide6.QtWidgets import QLabel, QProgressBar, QComboBox
from PySide6.QtGui import QStandardItemModel, QStandardItem, QIcon, QPixmap
from PySide6.QtGui import QPalette, QColor
from functools import partial
from PySide6 import QtWidgets, QtCore
from PySide6.QtWidgets import QMessageBox
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.ticker import MultipleLocator, AutoLocator
from collections import defaultdict
from scipy.signal import find_peaks, peak_widths
from data_analysis import fourier_smooth
from scipy.interpolate import interp1d
from numpy import trapezoid as trapz


# pyinstaller main.py --name "KHDPS" --windowed --onefile --icon "Resource Files/khdps_icon.ico" --paths "Resource Files" --add-data "Resource Files;Resource Files" --hidden-import=matplotlib.backends.backend_pdf
# pyinstaller main.py --name "KHDPS" --windowed --onefile --icon "Resource Files/khdps_icon.ico" --paths "Resource Files" --add-data "Resource Files;Resource Files" --splash "Resource Files/khdps_logo.png" --hidden-import=matplotlib.backends.backend_pdf
# pyinstaller main.py --name "KHDPS" --windowed --onedir --icon "Resource Files/khdps_icon.ico" --paths "Resource Files" --add-data "Resource Files;Resource Files" --hidden-import=matplotlib.backends.backend_pdf

def _resource_path(*parts):
    """Resolve a bundled resource path for both source and frozen (PyInstaller)
    runs -- see the matching helper/comment in main.py."""
    if hasattr(sys, "_MEIPASS"):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, *parts)

_ICON_PATH = _resource_path("Resource Files", "khdps_icon.ico")

# pyside6-uic form.ui -o ui_form.py
# pyside6-uic add_conc.ui -o ui_add_conc.py
# pyside6-uic folder_compiler.ui -o ui_folder_compiler.py
# pyside6-uic graphing.ui -o ui_graphing.py

# pyside6-rcc resources.qrc -o resources_rc.py

# Important:
# You need to run the following command to generate the ui_form.py file
#     pyside6-uic form.ui -o ui_form.py, or
#     pyside2-uic form.ui -o ui_form.py
#     To check what has changed: git status
#     To add all changes: git add .
#     To commit changes: git commit -m "Description"
#     To push to github use command: git push origin master


from ui_form import Ui_MainWindow
from ui_graphing import Ui_Graphing
from ui_add_conc import Ui_Dialog
from ui_folder_compiler import Ui_Compiler
from ui_calibwindow import Ui_calib_window
from data_analysis import run_full_analysis
from data_analysis import CalibrationFitter
from data_analysis import (
    read_swv_text_file,
    read_cv_text_file,
    extract_electrode,
    extract_frequency,
    extract_run_number,
    extract_device_id,
    extract_segment_number,
    extract_filename_timestamp_key,
    extract_timestamp,
    extract_cv_electrode,
    extract_cv_scanrate,
    extract_cv_run,
    find_peak_and_baseline_dual,
    find_peak_and_baseline_mid80
)
from graph_canvas import GraphCanvas, GraphToolbar

# --- Global font family ---
mpl.rcParams["font.family"] = "Arial"
#mpl.rcParams["font.sans-serif"] = ["Arial"]

# Global style defaults for all plots
mpl.rcParams["axes.titlesize"] = 8         # default title size
mpl.rcParams["axes.titleweight"] = "bold"   # make titles bold

mpl.rcParams["axes.labelsize"]   = 8
mpl.rcParams["axes.labelweight"] = "bold"

mpl.rcParams["xtick.labelsize"] = 8
mpl.rcParams["ytick.labelsize"] = 8

mpl.rcParams["legend.fontsize"] = 8

mpl.rcParams["xtick.major.width"] = 1
mpl.rcParams["ytick.major.width"] = 1

#mpl.rcParams["figure.figsize"] = (1.75, 1.75)  # width, height in inches

# --- Global save/export defaults ---
# High-resolution PNG by default when using the toolbar "Save" button
mpl.rcParams["savefig.dpi"] = 600
mpl.rcParams["savefig.bbox"] = "tight"

# Make vector exports Illustrator-friendly
mpl.rcParams["svg.fonttype"] = "none"   # keep text as text in SVG
mpl.rcParams["pdf.fonttype"] = 42      # TrueType fonts in PDF (editable)

# Correlate y-axis names in graphing.ui to header names in data output
METRIC_COLUMN = {
    "Peak Height": "Peak - Baseline (A)",
    "i max": "Peak Current (A)",
    "Signal Change (%)": "Signal Change (%)",
    "AUC": "AUC Normalized (A·V)",
    "Peak Position": "Peak Position (V)",
    "i max/cm²": "Peak Current Norm (A/cm²)",
    "Peak Height/cm²": "Peak Height Norm (A/cm2)",
    "AUC/cm²": "AUC Norm (A·V/cm2)"
}

def is_file_stable(filepath: str, threshold_ms: int = 500) -> bool:
    """
    Check if a file has not been modified in the last `threshold_ms` milliseconds.
    Returns True if stable.
    """
    try:
        last_mod = os.path.getmtime(filepath)
        return (time.time() - last_mod) * 1000 >= threshold_ms
    except Exception:
        return False

def get_processed_files(csv_path: str) -> set[str]:
    try:
        if os.path.exists(csv_path):
            print(f"[DEBUG] Reading processed file list from: {csv_path}")
            df = pd.read_csv(csv_path, usecols=["File Name"])
            return set(df["File Name"].dropna().unique())
    except Exception as e:
        print(f"[WARN] Could not read processed CSV: {e}")
    return set()

class CloseBlocker(QObject):
    """Event filter that ignores any Close events."""
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Close:
            # Swallow the close event so the subwindow never actually closes.
            return True
        return False

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.setWindowIcon(QIcon(_ICON_PATH))
        self.ui.setupUi(self)

        # In-memory set to track which files have already been appended to CSV
        self._processed_files: set[str] = set()
        # Chronological cycle tracking for our internal FC board, keyed by
        # device_id only -- a "run" is one full cycle through the device's
        # configured frequencies (s1/s2/s3...), shared across every
        # electrode/frequency scanned in that cycle. Segment number resetting
        # back down (not time) marks a new cycle, since automatic scan
        # intervals vary, manual scans can happen in between, and disconnects
        # can create large time gaps that don't represent a real cycle break.
        self._device_current_run: dict[str, int] = {}
        self._device_prev_segment: dict[str, int] = {}
        # (folder, fname) -> resolved run number, assigned synchronously
        # before a file is handed off to a worker thread.
        self._assigned_run_numbers: dict[tuple[str, str], int] = {}
        # For FC-board files: (electrode, frequency) -> run number of
        # whichever scan is currently stored as that combo's reference.
        # Needed because parse tasks run on multiple worker threads and can
        # finish out of chronological order -- without this, whichever task
        # happens to finish first would win the reference slot even if a
        # file with an earlier run number is still being processed.
        self._reference_peak_runs: dict[tuple[str, float], int] = {}
        # Cache for first timestamp per (electrode, freq) for quick dt calculations if needed
        self._t0_by_pair: dict[tuple[str, float], pd.Timestamp] = {}
        # Be a bit conservative with worker threads to avoid I/O thrash
        try:
            QThreadPool.globalInstance().setMaxThreadCount(max(2, (os.cpu_count() or 4)//2))
        except Exception:
            pass


        self.watcher = QFileSystemWatcher(self)
        self.watcher.directoryChanged.connect(self.on_directory_changed)

        self._seen_files: dict[str, set[str]] = {}
        self._pending_parse_tasks = 0
        self._pending_files: set[tuple[str, str, str]] = set()  # (group, folder, fname)

        # Save / Load Defaults Setup
        self.ui.save_defaults_button.clicked.connect(self.save_defaults)
        self.ui.load_def_button.clicked.connect(self.load_defaults)
        self._graph_screen_requested = False  # if you're using deferred screen load

        self.cv_lookup: dict[tuple[str, str], dict[str, float]] = {}

        # keep a reference to the original central widget (home screen)
        self._home_widget   = self.centralWidget()

        # create the graphing widget once
        self._graph_widget  = GraphingWidget()

        # Connect Graph 1 Plot Button
        self._graph_widget.ui.graph1_plot_button.clicked.connect(lambda: self.plot_graph(1))

        # Connect Graph 2 Plot Button
        self._graph_widget.ui.graph2_plot_button.clicked.connect(lambda: self.plot_graph(2))

        # Connect Graph 3 Plot Button
        self._graph_widget.ui.graph3_plot_button.clicked.connect(lambda: self.plot_graph(3))

        # Connect Graph 4 Plot Button
        self._graph_widget.ui.graph4_plot_button.clicked.connect(lambda: self.plot_graph(4))

        # build a stacked container so neither page ever gets deleted
        self._stack = QStackedWidget()
        self._stack.addWidget(self._home_widget)
        self._stack.addWidget(self._graph_widget)

        # make the stack our one-and-only central widget
        super().setCentralWidget(self._stack)

        # Load Graphing Window
        self.ui.graph_button.clicked.connect(self.run_graph_analysis)
        #self.ui.graph_button.clicked.connect(self.show_graph_screen)

        # Setup Add Folder Button
        self.ui.add_folder_button.clicked.connect(self.select_folder)

        # Setup Remove Folder Button
        self.ui.rm_folder_button.clicked.connect(self.remove_selected_folder)

        #Setup Add Group Button
        self.ui.add_group_button.clicked.connect(self.add_group_name)

        # Setup Remove Group Button
        self.ui.remove_group_button.clicked.connect(self.remove_selected_group)

        # Create a list to hold folder paths
        self.folder_paths = []
        # Add folder to list
        self.folder_model = QStringListModel()
        self.ui.folder_list.setModel(self.folder_model)

        # Setup location for per-group data
        self.group_data: dict[str, dict] = {}

        # (group, frequency) -> "#RRGGBB"
        self.custom_colors: dict[tuple[str, float | str], str] = {}

        # Allow multi-select for Electrodes
        self.ui.swv_electrode_select.setSelectionMode(QAbstractItemView.MultiSelection)
        self.ui.cv_electrode_select.setSelectionMode(QAbstractItemView.MultiSelection)

        # When the user picks a folder, show its electrodes
        self.ui.swv_folder_select.itemSelectionChanged.connect(self.populate_swv_electrodes)
        self.ui.cv_folder_select.itemSelectionChanged.connect(self.populate_cv_electrodes)

        # When the user clicks “add electrodes to group”
        self.ui.swv_folder_es_group_button.clicked.connect(self.save_swv_electrodes_to_group)
        self.ui.cv_folder_es_group_button.clicked.connect(self.save_cv_electrodes_to_group)

        # Clears selected electrodes when new group is selected
        self.ui.group_names_list.itemSelectionChanged.connect(
            self.on_group_changed          # New
        )

        # Setup Add Concentration Button
        self._conc_dialog = AddConcDialog(self)
        self.setWindowIcon(QIcon(_ICON_PATH))
        self.ui.add_conc_button.clicked.connect(self._conc_dialog.show)

        # wire every back-button to return us home
        for btn in (
            self._graph_widget.ui.graph1_back,
            self._graph_widget.ui.graph2_back,
            self._graph_widget.ui.graph3_back,
            self._graph_widget.ui.graph4_back,
        ):
            btn.clicked.connect(self.show_home_screen)

        # Setup Folder Compiler Button
        self._folder_compiler_dialog = FolderCompilerDialog(self)
        self.ui.folder_compiler_button.clicked.connect(self._open_folder_compiler)

        # Setup Data Output Folder
        self._data_output_path = None
        self.ui.data_output_loc.clicked.connect(self.select_data_output_folder)

        # Setup CV Data Save Location
        self._cv_data_rows = []

        self.folder_update_timer = QTimer(self)
        self.folder_update_timer.setSingleShot(True)
        self.folder_update_timer.timeout.connect(self._process_folder_changes)
        self._pending_changed_folder = None

        # --- Fourier Smooth controls sync ---
        self.ui.fouriersmoothslider.valueChanged.connect(self.on_fouriersmooth_slider_changed)
        self.ui.fouriersmoothvalue.editingFinished.connect(self.on_fouriersmooth_value_changed)

        self.ui.fouriersmooth.setTristate(False)
        self.ui.fouriersmooth.setChecked(False)

        self.ui.fouriersmooth.toggled.connect(
            lambda checked: print(f"[DEBUG] Fourier smoothing toggled => {checked}")
        )

    # Updates folder list
    def update_folder_views(self):
        # Update QListView (uses model)
        self.folder_model.setStringList(self.folder_paths)

        # Update QListWidget for swv_folder_select
        self.ui.swv_folder_select.clear()
        self.ui.swv_folder_select.addItems(self.folder_paths)

        # Update QListWidget for cv_folder_select
        self.ui.cv_folder_select.clear()
        self.ui.cv_folder_select.addItems(self.folder_paths)

    # Adds folder to list
    def select_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder_path and folder_path not in self.folder_paths:
            self.folder_paths.append(folder_path)
            self.update_folder_views()

    # Removes folder from list
    def remove_selected_folder(self):
        index = self.ui.folder_list.currentIndex()
        if not index.isValid():
            return  # Nothing is selected

        folder_to_remove = self.folder_paths[index.row()]

        # Remove from the shared folder_paths list
        self.folder_paths.remove(folder_to_remove)

        # Update all folder views
        self.update_folder_views()

    # Adds Group name to List
    def add_group_name(self):
        group_name, ok = QInputDialog.getText(self, "Add Group", "Enter a group name:")
        if ok and group_name:
            existing_names = [self.ui.group_names_list.item(i).text()
                              for i in range(self.ui.group_names_list.count())]
            if group_name not in existing_names:
                self.ui.group_names_list.addItem(group_name)
                self.group_data[group_name] = {}          # NEW
            else:
                print(f"Group '{group_name}' already exists.")

    # Removes Group name and data from List
    def remove_selected_group(self):
        selected_items = self.ui.group_names_list.selectedItems()
        if not selected_items:
            return          # nothing highlighted

        for item in selected_items:
            group_name = item.text()
            row = self.ui.group_names_list.row(item)
            # remove the visible entry
            self.ui.group_names_list.takeItem(row)
            # purge its stored data (if any)
            self.group_data.pop(group_name, None)

    # Extract Electrode List
    def _extract_electrodes(self, folder_path: str) -> list[str]:
        """Return a sorted list like ['E1', 'E2', 'E10'] appearing in any
           filename inside folder_path.
        """
        electrodes = set()
        pattern = re.compile(r"E\d+")
        # Fallback for files that use a text label (e.g. "Low"/"High") as the
        # electrode name instead of "E1"/"E2", like "01-5Hz-Low_1.txt".
        label_pattern = re.compile(r"\d+Hz-([A-Za-z][A-Za-z0-9]*)_\d+\.txt$")
        for fname in os.listdir(folder_path):
            match = pattern.search(fname)
            if match:
                electrodes.add(match.group(0))
                continue
            label_match = label_pattern.search(fname)
            if label_match:
                electrodes.add(label_match.group(1))

        def sort_key(name: str):
            m = re.fullmatch(r"E(\d+)", name)
            return (0, int(m.group(1))) if m else (1, name)          # E1/E2 numeric, else alphabetic

        return sorted(electrodes, key=sort_key)

    # List Electrodes
    def populate_swv_electrodes(self):
        items = self.ui.swv_folder_select.selectedItems()
        if not items:
            return
        folder = items[0].text()
        labels = self._extract_electrodes(folder)
        self.ui.swv_electrode_select.clear()
        self.ui.swv_electrode_select.addItems(labels)

    def populate_cv_electrodes(self):
        items = self.ui.cv_folder_select.selectedItems()
        if not items:
            return
        folder = items[0].text()

        # 1) List all files in that folder
        all_files = os.listdir(folder)

        # 2) Keep only those starting with "E<digit(s)>-"
        hyphenated = [f for f in all_files if re.match(r"^E\d+-", f)]

        # 3) Extract only valid "E<number>" strings
        labels = set()
        for f in hyphenated:
            part = f.split("-", 1)[0]
            if re.fullmatch(r"E\d+", part):
                labels.add(part)

        # 4) Sort numerically by number after "E"
        electrodes = sorted(labels, key=lambda s: int(s[1:]))

        # 5) Populate the QListWidget
        self.ui.cv_electrode_select.clear()
        self.ui.cv_electrode_select.addItems(electrodes)

    # Store Information under Selected Group
    def _current_group(self) -> str | None:
        grps = self.ui.group_names_list.selectedItems()
        return grps[0].text() if grps else None

    def save_swv_electrodes_to_group(self):
        group = str(self._current_group())
        if not group:
            return          # No group chosen
        folder_items = self.ui.swv_folder_select.selectedItems()
        el_items = self.ui.swv_electrode_select.selectedItems()
        if not folder_items or not el_items:
            return

        folder = folder_items[0].text()
        electrodes = [i.text() for i in el_items]

        g = self.group_data.setdefault(group, {})
        g["swv"] = {folder: electrodes}

        # Only include files that match both the electrode name AND end with _<run>.txt
        run_pattern = re.compile(r"_(\d+)\.txt$")
        raw_list = [
            f
            for f in os.listdir(folder)
            # Match electrode as a whole "word" bounded by non-alphanumeric
            # characters (not Python's \b, which treats "_" as a word
            # character and would miss labels like "Low" in "Low_1.txt").
            if any(re.search(rf"(?<![A-Za-z0-9]){re.escape(elec)}(?![A-Za-z0-9])", f) for elec in electrodes)
               and run_pattern.search(f)
        ]
        # Sort by the run-number captured by the regex
        raw_list.sort(key=lambda x: int(run_pattern.search(x).group(1)))
        g["swv_files"] = {folder: raw_list}
        print(f"Saved SWV electrodes {electrodes} and files for folder '{folder}' under group '{group}'")

    def save_cv_electrodes_to_group(self):
        group = self._current_group()
        if not group:
            return
        folder_items = self.ui.cv_folder_select.selectedItems()
        el_items = self.ui.cv_electrode_select.selectedItems()
        dt_item = self.ui.cv_data_type_select.currentItem()
        if not folder_items or not el_items or dt_item is None:
            return

        folder = folder_items[0].text()
        electrodes = [i.text() for i in el_items]
        data_type = dt_item.text()

        g = self.group_data.setdefault(group, {})

        # Allow multiple folders, one per data_type
        cv_map = g.setdefault("cv", {})
        # Remove all folders tied to the same data type
        folders_to_remove = [f for f, meta in cv_map.items() if meta.get("data_type") == data_type]
        for f in folders_to_remove:
            del cv_map[f]

        # Replace with the new folder
        cv_map[folder] = {
            "electrodes": electrodes,
            "data_type": data_type
        }

        # --------- Same for cv_files ---------
        cv_files_map = g.setdefault("cv_files", {})
        for f in folders_to_remove:
            if f in cv_files_map:
                del cv_files_map[f]

        run_pattern = re.compile(r"[-_](\d+)\.txt$")
        raw_list = [
            f for f in os.listdir(folder)
            if any(f.startswith(e + "-") for e in electrodes) and run_pattern.search(f)
        ]
        # Sort by run number
        raw_list.sort(key=lambda f: extract_cv_run(f) or 0)

        cv_files_map[folder] = raw_list

        print(f"Saved CV electrodes {electrodes} with data type '{data_type}' under group '{group}'")

    # Update Electrode Selection Based on Group
    def on_group_changed(self):
        """When user highlights a different group:
           • clear both electrode widgets
           • (if possible) restore the electrodes that were saved earlier
             for the combination (group, selected folder, SWV/CV).
        """
        self.clear_electrode_selections()

        group = self._current_group()
        if not group:
            return

        # ---- SWV side --------------------------------------------------
        swv_folder_items = self.ui.swv_folder_select.selectedItems()
        if swv_folder_items:
            folder = swv_folder_items[0].text()
            saved = (
                self.group_data                    # may not exist yet
                .get(group, {})
                .get("swv", {})
                .get(folder, [])
            )
            self._reselect_items(self.ui.swv_electrode_select, saved)

        # ---- CV side ---------------------------------------------------
        cv_folder_items = self.ui.cv_folder_select.selectedItems()
        if cv_folder_items:
            folder = cv_folder_items[0].text()
            saved = (
                self.group_data
                .get(group, {})
                .get("cv", {})
                .get(folder, {})
            )

            if isinstance(saved, dict):  # New format
                electrodes = saved.get("electrodes", [])
                saved_type = saved.get("data_type", None)

                # Get current selected item in cv_data_type_select
                dt_item = self.ui.cv_data_type_select.currentItem()
                current_type = dt_item.text() if dt_item else None

                # Only reselect electrodes if the data type matches
                if saved_type == current_type:
                    self._reselect_items(self.ui.cv_electrode_select, electrodes)

                # Still highlight the saved data_type
                if saved_type:
                    self._reselect_items(self.ui.cv_data_type_select, [saved_type])

    def clear_electrode_selections(self):
        self.ui.swv_electrode_select.clearSelection()
        self.ui.cv_electrode_select.clearSelection()

    def _reselect_items(self, list_widget, labels: list[str]):
        """Tick (highlight) every list item whose text is in *labels*."""
        for i in range(list_widget.count()):
            item = list_widget.item(i)
            item.setSelected(item.text() in labels)

    def on_fouriersmooth_slider_changed(self, value: int):
        """
        When the slider moves, update the QLineEdit text.
        """
        with QSignalBlocker(self.ui.fouriersmoothvalue):
            self.ui.fouriersmoothvalue.setText(str(value))

    def on_fouriersmooth_value_changed(self):
        """
        When the user edits the QLineEdit, update the slider position.
        """
        text = self.ui.fouriersmoothvalue.text().strip()
        try:
            val = int(float(text))
        except ValueError:
            return  # ignore invalid input

        slider = self.ui.fouriersmoothslider
        val = max(slider.minimum(), min(slider.maximum(), val))
        # use the correct signal blocker class
        with QSignalBlocker(slider):
            slider.setValue(val)

    def fourier_enabled(self) -> bool:
        try:
            return bool(self.ui.fouriersmooth.isChecked())
        except Exception:
            return False

    def fourier_keep_frac(self) -> float:
        """
        Parse keep_frac from the line edit.
        Accepts either 0–1 (“0.12”) or 0–100 (“12” -> 0.12).
        Clamps to (0.01, 0.99) with default 0.11 if invalid.
        """
        default = 0.11
        try:
            raw = self.ui.fouriersmoothvalue.text().strip()
            if not raw:
                return default
            val = float(raw)
            if val > 1.0:
                val = val / 100.0
            # clamp
            val = max(0.01, min(0.99, val))
            return val
        except Exception:
            return default

    def show_graph_screen(self):

        # 1) grab every group name the user entered
        group_names = [
            self.ui.group_names_list.item(i).text()
            for i in range(self.ui.group_names_list.count())
        ]

        # 2) for each of the four graph-tabs, clear + refill + allow multi-select
        from PySide6.QtWidgets import QAbstractItemView
        targets = (
            self._graph_widget.ui.graph1_groups_list,
            self._graph_widget.ui.graph2_groups_list,
            self._graph_widget.ui.graph3_groups_list,
            self._graph_widget.ui.graph4_groups_list,
        )
        for lw in targets:
            lw.clear()
            lw.addItems(group_names)
            lw.setSelectionMode(QAbstractItemView.MultiSelection)

        # 3) swap in the graphing widget as before
        self._stack.setCurrentWidget(self._graph_widget)

        # Trigger an initial build of the per-graph concentration tables based on current selections
        try:
            self._graph_widget.populate_graph_concentrations(self._graph_widget.ui.graph1_groups_list, self._graph_widget.ui.conc_table_graph1)
            self._graph_widget.populate_graph_concentrations(self._graph_widget.ui.graph2_groups_list, self._graph_widget.ui.conc_table_graph2)
            self._graph_widget.populate_graph_concentrations(self._graph_widget.ui.graph3_groups_list, self._graph_widget.ui.conc_table_graph3)
            self._graph_widget.populate_graph_concentrations(self._graph_widget.ui.graph4_groups_list, self._graph_widget.ui.conc_table_graph4)
        except Exception:
            pass

        # Pull user’s concentrations (sorted by index)…
        committed = self._conc_dialog.get_concentrations_by_group()
        conc_list = [committed[i] for i in sorted(committed)]
        # concentrations now stored per-group; concentration tables are driven by group selection

    def show_home_screen(self):
        self._stack.setCurrentWidget(self._home_widget)

    def _open_folder_compiler(self):
        # 1. Instantiate a brand-new dialog
        dlg = FolderCompilerDialog(self)

        # 2. Reset its state
        dlg.compile_folder_list.clear()
        dlg.comp_folder_save_location = None
        try:
            dlg.savePathLineEdit.clear()
        except AttributeError:
                pass

        # 3. Run modally
        dlg.exec()

    def save_defaults(self):
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Defaults",
            "",
            "Text Files (*.txt);;JSON Files (*.json)"
        )
        if not path:
            return

        data = {
            # 1) the folder list
            "folder_paths": self.folder_paths,
            # 2) your full group→{swv/cv maps} data
            "group_data": self.group_data,
            # 3) group names in order
            "groups": [
                self.ui.group_names_list.item(i).text()
                for i in range(self.ui.group_names_list.count())
            ],
            # 4) concentrations & unit
            "concentrations_by_group": self._conc_dialog.get_concentrations_by_group(),
            "conc_unit": self._conc_dialog.ui.conc_unit.text(),
            "custom_colors": self.custom_colors,
        }

        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            QMessageBox.information(self, "Saved",
                                    f"Defaults saved to:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Error Saving", str(e))


    def load_defaults(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Load Defaults",
            "",
            "Text Files (*.txt);;JSON Files (*.json)"
        )
        if not path:
            return

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            QMessageBox.critical(self, "Error Loading", str(e))
            return

        # --- 1) restore folder_paths & UI folder lists ---
        self.folder_paths = data.get("folder_paths", [])
        self.update_folder_views()

        # --- 2) restore group_data in memory ---
        self.group_data = data.get("group_data", {})

        # --- 3) rebuild the group QListWidget ---
        self.ui.group_names_list.clear()
        for grp in data.get("groups", []):
            self.ui.group_names_list.addItem(grp)

        # if there’s at least one group, select it so electrodes redraw
        if self.ui.group_names_list.count() > 0:
            self.ui.group_names_list.setCurrentRow(0)
            # and manually fire the handler in case the signal isn't auto-connected
            self.on_group_changed()

        # --- 4) reload concentrations & unit in your AddConc dialog ---
        by_group = data.get("concentrations_by_group")
        if isinstance(by_group, dict):
            self._conc_dialog._committed_by_group = {str(k): list(v) for k, v in by_group.items()}
        else:
            # legacy: single flat list → apply to all current groups
            flat = data.get("concentrations", [])
            groups = [self.ui.group_names_list.item(i).text() for i in range(self.ui.group_names_list.count())]
            self._conc_dialog._committed_by_group = {g: list(flat) for g in groups}
        self._conc_dialog.ui.conc_unit.setText(data.get("conc_unit", ""))
        self._conc_dialog._rollback()

        self.custom_colors = data.get("custom_colors", {})

        QMessageBox.information(self, "Loaded",
                                f"Defaults loaded from:\n{path}")

    def select_data_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self._data_output_path = folder
            print(f"Output folder selected: {self._data_output_path}")

    def _plot_mean_with_band(self, ax, xs, ys, errs, *, label: str, color: str | None):
        """
        Draw a mean line (with circle markers) and a translucent ±SD band.
        Returns (line, band).
        """
        line, = ax.plot(
            xs, ys,
            marker='s', markersize=2, linestyle='None',
            label=label,
            color=color if color else None,
            picker=5
        )
        import numpy as np
        xs_arr = np.asarray(xs, dtype=float)
        ys_arr = np.asarray(ys, dtype=float)
        es_arr = np.asarray(errs, dtype=float) if errs is not None else np.zeros_like(ys_arr)
        band = ax.fill_between(
            xs_arr,
            ys_arr - es_arr,
            ys_arr + es_arr,
            facecolor=line.get_color(),
            alpha=0.15,
            edgecolor='none',
            zorder=line.get_zorder()-1  # sit behind the line/markers
        )
        return line, band

    def run_graph_analysis(self):
        ready_path = os.path.join(self._data_output_path, "NDL_Data.ready")
        if os.path.exists(ready_path):
            os.remove(ready_path)

        if not self.group_data:
            QMessageBox.warning(self, "No Data", "No group data is available for analysis.")
            return
        if not self._data_output_path:
            QMessageBox.warning(self, "No Output Folder", "Please select a data output location first.")
            return

        norm_point = self._conc_dialog.get_normalization_point()

        use_smooth = self.fourier_enabled()
        kf = self.fourier_keep_frac()
        print(f"[DEBUG] run_full_analysis(use_smoothing={use_smooth}, keep_frac={kf})")
        self.graph_results = run_full_analysis(
            group_data=self.group_data,
            norm_point=norm_point,
            output_dir=self._data_output_path,
            parent=self,
            use_smoothing=use_smooth,
            keep_frac=kf,
        )
        ready_path = os.path.join(self._data_output_path, "NDL_Data.ready")
        with open(ready_path, "w") as f:
            f.write("ready")
        self.show_graph_screen()

        # 1) Read the freshly-written CSV (guarded) and seed in-memory caches
        csv_path = os.path.join(self._data_output_path, "NDL_Data.csv")
        with csv_write_lock:
            df_all = pd.read_csv(csv_path)
        # Track already processed file names in memory (avoids read/write races later)
        if not df_all.empty and "File Name" in df_all.columns:
            self._processed_files = set(df_all["File Name"].dropna().unique())
        else:
            self._processed_files = set()
        # Build first-timestamp cache per (Electrode, Frequency)
        try:
            df_all["Timestamp_dt"] = pd.to_datetime(df_all["Timestamp"], errors="coerce")
            g = df_all.groupby(["Electrode", "Frequency (Hz)"])["Timestamp_dt"].min()
            self._t0_by_pair = {
                (str(k[0]), float(k[1])): v for k, v in g.dropna().items()
            }
        except Exception:
            self._t0_by_pair = {}

        # 2) Filter to rows where Run Number == norm_point
        df_ref = df_all.loc[df_all["Run Number"] == norm_point, :]

        # 3) Build self.reference_peaks[(electrode, freq)] = Peak Current (A)
        self.reference_peaks = {}
        for _, row in df_ref.iterrows():
            key = (row["Electrode"], row["Frequency (Hz)"])
            self.reference_peaks[key] = float(row["Peak - Baseline (A)"])

        # 4) Save normalization point
        self.norm_point = norm_point

        # Register every SWV-folder (i.e. any key in group_data[group]["swv_files"])
        #    with our QFileSystemWatcher, so that we hear when new files appear.
        # ─────────────────────────────────────────────────────────────────────────────

        cv_csv_path = os.path.join(self._data_output_path, "NDL_CV_Data.csv")
        has_cv_files = any(
            group.get("cv_files") for group in self.group_data.values()
        )

        if has_cv_files and not os.path.exists(cv_csv_path):
            print("[INFO] CV files exist but CV data not yet available — delaying SWV file monitoring.")
            return  # or delay watcher setup
        else:
            self.load_cv_lookup()
            for group, details in self.group_data.items():
                # details["swv_files"] is a dict: folder_path → [list of filenames]
                swv_files_map = details.get("swv_files", {})
                for folder_path in swv_files_map:
                    # Only addPath() if it isn’t already watched
                    if folder_path not in self.watcher.directories():
                        self.watcher.addPath(folder_path)
            # ─────────────────────────────────────────────────────────────────────────────
            print("[DEBUG] Watching folders:", self.watcher.directories())
            self.show_graph_screen()
            return

    def _build_run_to_x_map(self, graph_num: int):
        """
        Recreate the run->xvalue mapping for the active x-axis mode.
        Returns (run_to_x: dict[int, float], x_axis_label: str).
        """
        ui = self._graph_widget.ui

        # which x-axis mode is selected in this graph tab
        x_list = getattr(ui, f'graph{graph_num}_xax', None)
        x_axis_label = ""
        if hasattr(x_list, "currentItem") and x_list.currentItem():
            x_axis_label = x_list.currentItem().text()

        run_to_x: dict[int, float] = {}

        # grab conc table for possible legacy mapping
        conc_table = getattr(ui, f'conc_table_graph{graph_num}', None)

        # collect all runs present in results (fallbacks/backfill)
        all_runs_in_data = set()
        for group_dict in getattr(self, "graph_results", {}).values():
            for runs_data in group_dict.values():
                for run_i, _val in runs_data:
                    try:
                        all_runs_in_data.add(int(run_i))
                    except Exception:
                        pass

        # --- X = Scan Number ---
        if x_axis_label == "Scan Number":
            # prefer conc_table if it has a first column of run indices
            if conc_table and conc_table.model():
                model = conc_table.model()
                for row in range(model.rowCount()):
                    raw_idx = model.index(row, 0).data()
                    try:
                        run = int(raw_idx)
                        run_to_x[run] = float(run)
                    except Exception:
                        continue
            # fill any missing from data
            for run in all_runs_in_data:
                run_to_x.setdefault(run, float(run))

        # --- X = Concentration (legacy 2-col table only; per-group is handled in plot_graph via x_for) ---
        elif x_axis_label == "Concentration":
            if conc_table and conc_table.model() and conc_table.model().columnCount() == 2:
                model = conc_table.model()
                for row in range(model.rowCount()):
                    raw_idx  = model.index(row, 0).data()
                    raw_conc = model.index(row, 1).data()
                    try:
                        run  = int(raw_idx)
                        conc = float(raw_conc)
                        run_to_x[run] = conc
                    except Exception:
                        continue
            # backfill to run numbers where we have no concentration
            for run in all_runs_in_data:
                run_to_x.setdefault(run, float(run))
                print("fellback")

        # --- X = Time (Hrs)/(Days) ---
        elif x_axis_label.startswith("Time"):
            data_file_path = os.path.join(self._data_output_path, "NDL_Data.csv")
            if os.path.exists(data_file_path):
                with csv_write_lock:
                    df = pd.read_csv(data_file_path)

                # Ensure dt_hours exists (compute if needed)
                if "dt_hours" not in df.columns:
                    df["Timestamp_dt"] = pd.to_datetime(df["Timestamp"], errors="coerce")
                    # t0 per (Electrode, Frequency)
                    t0 = df.groupby(["Electrode", "Frequency (Hz)"])["Timestamp_dt"].transform("min")
                    df["dt_hours"] = (df["Timestamp_dt"] - t0).dt.total_seconds() / 3600.0

                # Use the earliest time for each Run Number (robust across electrodes/freqs)
                good = df[["Run Number", "dt_hours"]].dropna()
                if not good.empty:
                    per_run = good.groupby("Run Number")["dt_hours"].min()
                    max_hours = float(per_run.max()) if len(per_run) else 0.0
                    use_days = max_hours > 48.0

                    for run, t in per_run.items():
                        try:
                            run = int(run)
                            run_to_x[run] = float(t) / 24.0 if use_days else float(t)
                        except Exception:
                            continue

                    # normalize the label
                    x_axis_label = "Time (Days)" if use_days else "Time (Hrs)"

        # --- X = Frequency ---
        elif x_axis_label == "Frequency":
            x_axis_label = "Frequency (Hz)"

            # If we still have nothing (e.g., no CSV yet), fall back to run numbers
            for run in all_runs_in_data:
                run_to_x.setdefault(run, float(run))

        # --- Fallback if literally nothing built (shouldn’t happen, but safe) ---
        if not run_to_x:
            for run in all_runs_in_data:
                run_to_x[run] = float(run)
            if not x_axis_label:
                x_axis_label = "Scan Number"

        return run_to_x, x_axis_label

    def plot_graph(self, graph_num):

        ui = self._graph_widget.ui

        # figure out canvas + toolbar + container widgets
        canvas_attr  = f'canvas{graph_num}'
        toolbar_attr = f'toolbar{graph_num}'
        graph_window = getattr(ui, f'graph_window{graph_num}', None)
        if graph_window is None:
            print(f"[ERROR] Graph window {graph_num} not found.")
            return

        # convenience getter for y/x dropdowns
        def get_list_text(name):
            w = getattr(ui, name, None)
            if hasattr(w, 'currentItem'):
                it = w.currentItem()
                return it.text() if it else ''
            return ''

        # --- Y axis selection / which metric column to load from CSV ---
        y_axis = get_list_text(f'graph{graph_num}_yax')
        if y_axis == "Concentration":
            metric_col = "Concentration"
        else:
            metric_col = METRIC_COLUMN.get(y_axis, "Signal Change (%)")
        self.graph_results = self.load_graph_results_from_csv(metric_col, graph_num)

        # --- Build/replace the Matplotlib canvas + toolbar in this graph pane ---
        layout = getattr(ui, f'verticalLayout_graph{graph_num}', None) \
                 or graph_window.layout() \
                 or QVBoxLayout(graph_window)
        if graph_window.layout() is None:
            graph_window.setLayout(layout)

        canvas = self.replace_graph_canvas(
            canvas_attr=canvas_attr,
            toolbar_attr=toolbar_attr,
            layout=layout,
            parent_widget=graph_window,
            mdi_area=self._graph_widget.mdi
        )

        calib_btn = getattr(ui, f"calib_graph{graph_num}", None)
        if calib_btn:
            # Re-parent the button directly to the new Matplotlib canvas
            calib_btn.setParent(canvas)

            # Position it (X, Y) relative to the top-left of the canvas.
            # You can adjust these numbers to put it exactly where you want!
            calib_btn.move(240, 5)

            calib_btn.setStyleSheet("""
                QPushButton {
                    background-color: rgba(45, 101, 163, 220); /* KHDPS Bright Blue, slight transparency */
                    color: white;
                    border: 1px solid #64748b;
                    border-radius: 6px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: rgba(45, 101, 163, 255); /* Solid Bright Blue on hover */
                    border: 1px solid #0f172a;
                }
                QPushButton:pressed {
                    background-color: rgba(15, 23, 42, 255); /* KHDPS Deep Navy when clicked */
                }
            """)

            # Force it to the absolute top of the visual stack
            calib_btn.raise_()
            calib_btn.show()

        # Wipe any leftover artists from a previous draw
        for art in list(canvas.ax.lines) + list(canvas.ax.collections):
            try:
                art.remove()
            except Exception:
                pass
        if canvas.ax.legend_:
            try:
                canvas.ax.legend_.remove()
            except Exception:
                pass

        # --- X axis mapping (run → x value like time, conc, etc.) ---
        run_to_x, resolved_x_label = self._build_run_to_x_map(graph_num)

        # --- Pull UI selections the plot depends on ---
        # groups
        groups_w = getattr(ui, f'graph{graph_num}_groups_list', None)
        groups = [it.text() for it in groups_w.selectedItems()] if groups_w else []

        # runs (from concentration table cells; per-group)
        conc_table = getattr(ui, f'conc_table_graph{graph_num}', None)
        selected_runs_by_group: dict[str, set[int]] = {}
        any_cell_selected = False
        if conc_table and conc_table.selectionModel() and conc_table.model():
            model = conc_table.model()
            from PySide6.QtCore import Qt as _Qt
            headers = [model.headerData(c, _Qt.Horizontal) for c in range(model.columnCount())]
            for idx in conc_table.selectionModel().selectedIndexes():
                col = idx.column()
                row = idx.row()
                if col == 0:
                    continue  # "Run" column
                grp = headers[col]
                if not grp:
                    continue
                any_cell_selected = True
                # run is 1-based row index
                run_val = row + 1
                selected_runs_by_group.setdefault(str(grp), set()).add(int(run_val))

        def run_allowed(grp: str, run: int) -> bool:
            # If nothing selected anywhere -> allow all (plot everything)
            if not any_cell_selected:
                return True
            # If this group has a non-empty selection, allow only selected runs
            sel = selected_runs_by_group.get(str(grp))
            if sel:
                return run in sel
            # This group has no specific selection -> allow all
            return True

        # helper for per-group concentration x lookup from the table
        def x_for(group_name: str, run: int, default: float) -> float:
            if resolved_x_label != "Concentration":
                return default
            if not (conc_table and conc_table.model()):
                return default
            model = conc_table.model()
            from PySide6.QtCore import Qt as _Qt2
            headers = [model.headerData(c, _Qt2.Horizontal) for c in range(model.columnCount())]
            # find column for this group
            try:
                col = next(i for i, h in enumerate(headers) if h == group_name)
            except StopIteration:
                return default
            r = run - 1
            if r < 0 or r >= model.rowCount():
                return default
            try:
                raw = model.index(r, col).data()
                return float(raw) if raw not in (None, "") else default
            except Exception:
                return default

        # frequencies
        #(and "KDM")
        freq_table = getattr(ui, f'graph{graph_num}_freq_table', None)
        selected_freq_map: dict[str, set[float]] = {}
        selected_kdm_groups: set[str] = set()
        if freq_table and freq_table.selectionModel() and freq_table.model():
            model = freq_table.model()
            from PySide6.QtCore import Qt
            col_headers = [model.headerData(col, Qt.Horizontal)
                           for col in range(model.columnCount())]

            for idx in freq_table.selectionModel().selectedIndexes():
                col = idx.column()
                row = idx.row()
                raw = model.index(row, col).data()
                group_name = col_headers[col]
                if not group_name:
                    continue

                if raw == "KDM":
                    selected_kdm_groups.add(group_name)
                else:
                    try:
                        freq_val = float(raw)
                        selected_freq_map.setdefault(group_name, set()).add(freq_val)
                    except Exception:
                        continue

        # electrodes
        elec_table = getattr(ui, f'graph{graph_num}_electrodes_table', None)
        selected_elec_map: dict[str, set[str]] = {}
        if elec_table and elec_table.selectionModel() and elec_table.model():
            model = elec_table.model()
            from PySide6.QtCore import Qt
            col_headers = [model.headerData(c, Qt.Horizontal)
                           for c in range(model.columnCount())]
            for idx in elec_table.selectionModel().selectedIndexes():
                col = idx.column()
                row = idx.row()
                electrode_name = model.index(row, col).data()
                group_name = col_headers[col]
                if electrode_name:
                    selected_elec_map.setdefault(group_name, set()).add(electrode_name)

        # averaged checkbox
        avg_chk = getattr(ui, f'graph{graph_num}_average', None)
        is_avg = avg_chk.isChecked() if avg_chk else False

        # --- ACTUAL PLOTTING ---
        try:
            is_freq_x = (resolved_x_label == "Frequency (Hz)")

            for group in groups:
                data = self.graph_results.get(group, {})
                if not data:
                    continue

                if is_avg:
                    if is_freq_x:
                        self._plot_frequency_x_average(
                            canvas, group, data, y_axis, graph_num, run_allowed,
                            selected_freq_map, selected_elec_map
                        )
                    else:
                        self._plot_standard_x_average(
                            canvas, group, data, y_axis, graph_num, run_to_x, x_for,
                            run_allowed, selected_freq_map, selected_elec_map, selected_kdm_groups
                        )
                else:
                    if is_freq_x:
                        self._plot_frequency_x_individual(
                            canvas, group, data, y_axis, run_allowed,
                            selected_freq_map, selected_elec_map
                        )
                    else:
                        self._plot_standard_x_individual(
                            canvas, group, data, y_axis, graph_num, run_to_x, x_for,
                            run_allowed, selected_freq_map, selected_elec_map, selected_kdm_groups
                        )

        except Exception as e:
            print(f"[ERROR] plot_graph({graph_num}) failed while plotting: {e}")

        # --- Finalize axes ---
        canvas.ax.set_title(f"Graph {graph_num}", fontweight="bold", fontsize=8)

        conc_unit = self._conc_dialog.ui.conc_unit.text()
        if resolved_x_label == "Concentration":
            canvas.ax.set_xlabel(f"{resolved_x_label} ({conc_unit})", fontweight="bold")
        else:
            canvas.ax.set_xlabel(resolved_x_label, fontweight="bold")

        canvas.ax.set_ylabel(y_axis, fontweight="bold")

        # Make tick labels bold
        for lab in list(canvas.ax.get_xticklabels()) + list(canvas.ax.get_yticklabels()):
            lab.set_fontweight("bold")

        # grid
        canvas.ax.grid(
            True,
            which='major',
            axis='both',
            linestyle='--',
            linewidth=0.5
        )

        # legend with color syncing
        handles, labels = canvas.ax.get_legend_handles_labels()
        if labels:
            try:
                legend = canvas.ax.legend(
                    handles, labels,
                    loc='center left',
                    bbox_to_anchor=(1.0, 0.5)
                )
                legend.set_draggable(True)

                # Make legend text bold
                for text in legend.get_texts():
                    text.set_fontweight("bold")

                # make legend patch colors match line colors
                for handle in legend.legendHandles:
                    lbl = handle.get_label()
                    for line in canvas.ax.lines:
                        if line.get_label() == lbl:
                            handle.set_color(line.get_color())
                            break
            except Exception as e:
                print(f"[WARNING] legend() raised {type(e).__name__}: {e}")

        # click handler
        canvas.mpl_connect('button_press_event', canvas.on_click)

        # draw
        try:
            canvas.draw()
        except Exception as e:
            print(f"[ERROR] canvas.draw() failed: {e}")

    # -------------------------------------------------------------------------
    # PLOTTING HELPER METHODS
    # -------------------------------------------------------------------------
    def _plot_frequency_x_average(self, canvas, group, data, y_axis, graph_num, run_allowed, selected_freq_map, selected_elec_map):
        """Plots mean values across selected electrodes against Frequency on the X-axis."""
        run_freq_data = defaultdict(list)

        for (elec, freq), runs_data in data.items():
            if freq == "KDM": continue
            try: f_val = float(freq)
            except ValueError: continue

            if selected_freq_map and f_val not in selected_freq_map.get(group, ()): continue
            if selected_elec_map and elec not in selected_elec_map.get(group, ()): continue

            for run, val in runs_data:
                if run_allowed(group, run):
                    run_freq_data[(run, f_val)].append(val)

        run_to_fvals = defaultdict(list)
        for (run, f_val), vals in run_freq_data.items():
            run_to_fvals[run].append((f_val, np.mean(vals), np.std(vals, ddof=1) if len(vals)>1 else 0))

        for run, pts in run_to_fvals.items():
            pts.sort(key=lambda x: x[0])
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            errs = [p[2] for p in pts]

            line, band = self._plot_mean_with_band(
                canvas.ax, xs, ys, errs,
                label=f"{group} avg (Run {run})", color=None
            )
            line._meta = {
                'group': group, 'runs': [run] * len(xs), 'xvals': xs, 'frequency': xs,
                'average': True, 'y_label': y_axis, 'band': band, 'graph_num': graph_num
            }

    def _plot_frequency_x_individual(self, canvas, group, data, y_axis, run_allowed, selected_freq_map, selected_elec_map):
        """Plots individual electrode runs against Frequency on the X-axis."""
        run_freq_data = defaultdict(list)

        for (elec, freq), runs_data in data.items():
            if freq == "KDM": continue
            try: f_val = float(freq)
            except ValueError: continue

            if selected_freq_map and f_val not in selected_freq_map.get(group, ()): continue
            if selected_elec_map and elec not in selected_elec_map.get(group, ()): continue

            for run, val in runs_data:
                if run_allowed(group, run):
                    run_freq_data[(elec, run)].append((f_val, val))

        for (elec, run), pts in run_freq_data.items():
            pts.sort(key=lambda x: x[0])
            x_vals = [p[0] for p in pts]
            y_vals = [p[1] for p in pts]

            line, = canvas.ax.plot(
                x_vals, y_vals, marker='s', markersize=4, linestyle='-',
                label=f"{group}-{elec} (Run {run})"
            )
            line._meta = {
                'group': group, 'electrode': elec, 'runs': [run] * len(x_vals), 'xvals': x_vals, 'frequency': x_vals,
                'average': False, 'y_label': y_axis
            }

    def _plot_standard_x_average(self, canvas, group, data, y_axis, graph_num, run_to_x, x_for, run_allowed, selected_freq_map, selected_elec_map, selected_kdm_groups):
        """Plots average values across electrodes against Time/Run/Concentration on the X-axis."""
        # 1. KDM Processing
        if group in selected_kdm_groups:
            freqs_selected = sorted(selected_freq_map.get(group, []))
            if len(freqs_selected) == 2:
                low_freq, high_freq = freqs_selected[0], freqs_selected[1]
                chosen_electrodes = selected_elec_map.get(group, set())

                run_vals_low, run_vals_high = defaultdict(list), defaultdict(list)

                for (elec, f), runs_data in data.items():
                    if chosen_electrodes and elec not in chosen_electrodes: continue
                    for run, val in runs_data:
                        if not run_allowed(group, run): continue
                        if f == low_freq: run_vals_low[run].append(val)
                        elif f == high_freq: run_vals_high[run].append(val)

                common_runs = sorted(set(run_vals_low) & set(run_vals_high))
                if common_runs:
                    xs, yl_vals, yl_errs, yh_vals, yh_errs, y_kdm, kdm_errs = [], [], [], [], [], [], []

                    for run in common_runs:
                        vl, vh = run_vals_low[run], run_vals_high[run]
                        ml, mh = float(np.mean(vl)), float(np.mean(vh))
                        sl, sh = np.std(vl, ddof=1) if len(vl) > 1 else 0, np.std(vh, ddof=1) if len(vh) > 1 else 0

                        xs.append(x_for(group, run, run_to_x.get(run, float(run))))
                        yl_vals.append(ml); yl_errs.append(sl)
                        yh_vals.append(mh); yh_errs.append(sh)
                        y_kdm.append(mh - ml); kdm_errs.append(np.sqrt(sl**2 + sh**2))

                    elecs_used = chosen_electrodes or {e for (e, f) in data.keys() if f in (low_freq, high_freq)}
                    electrodes_all = sorted(elecs_used, key=lambda s: int(s[1:]))

                    # Plot Low Freq, High Freq, and KDM lines
                    ll, lb = self._plot_mean_with_band(canvas.ax, xs, yl_vals, yl_errs, label=f"{group} avg ({int(low_freq)} Hz)", color=self.custom_colors.get((group, low_freq)))
                    ll._meta = {'group': group, 'frequency': low_freq, 'xvals': xs, 'runs': common_runs, 'electrodes': electrodes_all, 'graph_num': graph_num, 'average': True, 'y_label': y_axis, 'band': lb}

                    hl, hb = self._plot_mean_with_band(canvas.ax, xs, yh_vals, yh_errs, label=f"{group} avg ({int(high_freq)} Hz)", color=self.custom_colors.get((group, high_freq)))
                    hl._meta = {'group': group, 'frequency': high_freq, 'xvals': xs, 'runs': common_runs, 'electrodes': electrodes_all, 'graph_num': graph_num, 'average': True, 'y_label': y_axis, 'band': hb}

                    kl, kb = self._plot_mean_with_band(canvas.ax, xs, y_kdm, kdm_errs, label=f"{group} (avg KDM)", color=self.custom_colors.get((group, "KDM")))
                    kl._meta = {'group': group, 'frequency': 'KDM', 'low_freq': low_freq, 'high_freq': high_freq, 'xvals': xs, 'runs': common_runs, 'electrodes': electrodes_all, 'graph_num': graph_num, 'average': True, 'y_label': y_axis, 'kdm': True, 'band': kb}
        else:
            # 2. Normal Frequency Processing
            freqs = sorted({f for (_, f) in data.keys() if f != "KDM"})
            for freq in freqs:
                if selected_freq_map and freq not in selected_freq_map.get(group, ()): continue

                run_vals = defaultdict(list)
                for (elec, f), runs_data in data.items():
                    if f != freq: continue
                    if selected_elec_map and elec not in selected_elec_map.get(group, ()): continue

                    for run, val in runs_data:
                        if run_allowed(group, run):
                            run_vals[run].append(val)

                if run_vals:
                    raw_runs = sorted(run_vals)
                    xs = [x_for(group, r, run_to_x.get(r, float(r))) for r in raw_runs]
                    ys = [np.mean(run_vals[r]) for r in raw_runs]
                    errs = [np.std(run_vals[r], ddof=1) if len(run_vals[r]) > 1 else 0 for r in raw_runs]

                    line, band = self._plot_mean_with_band(canvas.ax, xs, ys, errs, label=f"{group} avg ({int(freq)} Hz)", color=self.custom_colors.get((group, freq)))
                    line._meta = {'group': group, 'frequency': freq, 'xvals': xs, 'runs': raw_runs, 'electrodes': list(run_vals.keys()), 'graph_num': graph_num, 'average': True, 'y_label': y_axis, 'band': band}

    def _plot_standard_x_individual(self, canvas, group, data, y_axis, graph_num, run_to_x, x_for, run_allowed, selected_freq_map, selected_elec_map, selected_kdm_groups):
        """Plots individual electrode values against Time/Run/Concentration on the X-axis."""
        # 1. KDM Processing
        if group in selected_kdm_groups:
            freqs_selected = sorted(selected_freq_map.get(group, []))
            if len(freqs_selected) >= 2:
                low_freq, high_freq = freqs_selected[0], freqs_selected[1]
                chosen = selected_elec_map.get(group, set())
                electrodes_all = sorted({e for (e, f) in data.keys() if f in (low_freq, high_freq) and (not chosen or e in chosen)}, key=lambda s: int(s[1:]))

                for elec in electrodes_all:
                    low_map = {r: v for r, v in data.get((elec, low_freq), []) if run_allowed(group, r)}
                    high_map = {r: v for r, v in data.get((elec, high_freq), []) if run_allowed(group, r)}

                    common_runs = sorted(set(low_map) & set(high_map))
                    if not common_runs: continue

                    xs = [x_for(group, r, run_to_x.get(r, float(r))) for r in common_runs]
                    y_low = [low_map[r] for r in common_runs]
                    y_high = [high_map[r] for r in common_runs]
                    y_kdm = [high_map[r] - low_map[r] for r in common_runs]

                    # Low, High, and KDM Lines
                    ll, = canvas.ax.plot(xs, y_low, marker='s', markersize=4, linestyle='None', label=f"{group}-{elec} @ {int(low_freq)} Hz")
                    ll._meta = {'group': group, 'electrode': elec, 'frequency': low_freq, 'low_freq': low_freq, 'high_freq': high_freq, 'xvals': xs, 'runs': common_runs, 'average': False, 'y_label': y_axis, 'kdm': True}

                    hl, = canvas.ax.plot(xs, y_high, marker='s', markersize=4, linestyle='None', label=f"{group}-{elec} @ {int(high_freq)} Hz")
                    hl._meta = {'group': group, 'electrode': elec, 'frequency': high_freq, 'low_freq': low_freq, 'high_freq': high_freq, 'xvals': xs, 'runs': common_runs, 'average': False, 'y_label': y_axis, 'kdm': True}

                    kl, = canvas.ax.plot(xs, y_kdm, marker='s', markersize=4, linestyle='None', label=f"{group}-{elec} (Δ KDM)")
                    kl._meta = {'group': group, 'electrode': elec, 'frequency': "KDM", 'low_freq': low_freq, 'high_freq': high_freq, 'xvals': xs, 'runs': common_runs, 'average': False, 'y_label': y_axis, 'kdm': True}

        else:
            # 2. Normal Frequency Processing
            for (elec, freq), runs_data in data.items():
                if freq == "KDM": continue
                if selected_freq_map and float(freq) not in selected_freq_map.get(group, ()): continue
                if selected_elec_map and elec not in selected_elec_map.get(group, ()): continue

                pts = [(r, v) for r, v in runs_data if run_allowed(group, r)]
                if not pts: continue

                raw_runs, y_vals = zip(*pts)
                x_vals = [x_for(group, r, run_to_x.get(r, float(r))) for r in raw_runs]

                color = self.custom_colors.get((group, freq))
                line, = canvas.ax.plot(x_vals, y_vals, marker='s', markersize=4, linestyle='None', label=f"{group}-{elec} ({int(freq)} Hz)", picker=5, color=color)
                line._meta = {'group': group, 'electrode': elec, 'frequency': freq, 'xvals': x_vals, 'runs': list(raw_runs), 'average': False, 'y_label': y_axis}

    def replace_graph_canvas(self, canvas_attr, toolbar_attr, layout, parent_widget, mdi_area):
        # - delete existing toolbar if it exists -
        old_toolbar = getattr(self._graph_widget, toolbar_attr, None)
        if old_toolbar:
            layout.removeWidget(old_toolbar)
            old_toolbar.deleteLater()
            delattr(self._graph_widget, toolbar_attr)

        # - delete existing canvas if it exists -
        old_canvas = getattr(self._graph_widget, canvas_attr, None)
        if old_canvas:
            layout.removeWidget(old_canvas)

            # ① Make sure Matplotlib is not still trying to draw on it:
            try:
                old_canvas.figure.clear()
            except Exception:
                pass

            # ② Force-close/stop any Qt/Mpl callbacks:
            try:
                old_canvas.close()
            except Exception:
                pass

            old_canvas.deleteLater()
            delattr(self._graph_widget, canvas_attr)

        # … then create new_canvas as before …
        new_canvas = GraphCanvas(parent_widget, mdi_area=mdi_area)
        new_toolbar = GraphToolbar(new_canvas, self._graph_widget, main_window=self)

        layout.addWidget(new_canvas)
        layout.addWidget(new_toolbar)
        setattr(self._graph_widget, canvas_attr, new_canvas)
        setattr(self._graph_widget, toolbar_attr, new_toolbar)
        return new_canvas

    def load_graph_results_from_csv(self, metric_col: str, graph_num: int = None, attempt=1, max_attempts=3, delay_ms=200):
        data_file_path = os.path.join(self._data_output_path, "NDL_Data.csv")
        if not os.path.exists(data_file_path):
            print(f"[WARN] NDL_Data.csv not found.")
            return {}
        try:
            with csv_write_lock:
                with csv_write_lock:
                        df = pd.read_csv(data_file_path)
        except Exception as e:
            print(f"[WARN] Attempt {attempt}: Could not read CSV: {e}")
            if attempt < max_attempts:
                QTimer.singleShot(
                    delay_ms,
                    lambda: self.load_graph_results_from_csv(metric_col, attempt + 1, max_attempts, delay_ms)
                )
            return {}
        if metric_col not in df.columns and metric_col != "Concentration":
            print(f"[WARN] '{metric_col}' not found in NDL_Data.csv.")
            return {}

        structured = {}
        is_concentration_plot = (metric_col == "Concentration")

        # We need this import for the inverse math
        from data_analysis import calculate_concentration_from_signal

        for _, row in df.iterrows():
            group = str(row["Group"]).strip()
            electrode = row["Electrode"]
            freq      = row["Frequency (Hz)"]
            run       = int(row["Run Number"])

            val = np.nan

            # Scenario 1: Standard raw metric plotting
            if not is_concentration_plot:
                if metric_col in row:
                    val = row[metric_col]

            # Scenario 2: Dynamic Concentration Calculation!
            else:
                saved_calibs = getattr(self, "saved_calibrations", {})

                # --- THE FIX: Pull the exact calibration saved for THIS specific graph ---
                calib_data = saved_calibs.get((graph_num, float(freq)))

                if calib_data:
                    # Find out what raw metric this calibration was built on
                    orig_metric = calib_data["metric"]
                    fit_results = calib_data["results"]

                    # Grab that raw signal from the CSV row
                    raw_signal = row.get(METRIC_COLUMN.get(orig_metric, "Signal Change (%)"))

                    if pd.notna(raw_signal):
                        # Convert it!
                        val = calculate_concentration_from_signal(float(raw_signal), fit_results)

            # Only append valid numbers to the structured dictionary
            if pd.notna(val):
                structured\
                    .setdefault(group, {})\
                    .setdefault((electrode, freq), [])\
                    .append((run, val))

        return structured

    def load_cv_lookup(self):
        path = os.path.join(self._data_output_path, "NDL_CV_Data.csv")
        if not os.path.exists(path):
            print("[WARN] CV normalization data not found.")
            return
        df = pd.read_csv(path)
        # Pick best values
        def pick_best_value(subdf, col, priority_tags):
            for tag in priority_tags:
                vals = subdf.loc[subdf["Data Type"] == tag, col].dropna()
                if not vals.empty:
                    return vals.iloc[0]
            return np.nan
        lookup = {}
        for (group, elec), subdf in df.groupby(["Group", "Electrode"]):
            group = str(group).strip()
            elec = str(elec).strip()
            au_cm2 = pick_best_value(subdf, "Au cm2", ["EASA After Roughening", "EASA Before Roughening"])
            num_mb = pick_best_value(subdf, "Number MB", ["CVs With Hydrogel", "CVs Without Hydrogel"])
            pdens = num_mb / au_cm2 if au_cm2 else np.nan
            lookup[(group, elec)] = {
                "Au cm2": au_cm2,
                "Number MB": num_mb,
                "Packing Density (MB/cm²)": pdens
            }
        self.cv_lookup = lookup
        print(f"[DEBUG] Loaded CV entries: {len(lookup)}")
        print("[DEBUG] CV Lookup has been populated.")

    def on_directory_changed(self, folder_path: str):
        ready_path = os.path.join(self._data_output_path, "NDL_Data.ready")
        if not os.path.exists(ready_path):
            print("[DEBUG] Ignoring directory change until .ready file exists.")
            return
        print(f"[DEBUG] Folder changed: {folder_path}")
        self._pending_changed_folder = folder_path
        if self.folder_update_timer.isActive():
            self.folder_update_timer.stop()
        self.folder_update_timer.start(500)  # or 250ms, depending on stability

    def _process_folder_changes(self):
        if self._pending_changed_folder:
            self._handle_folder_update(self._pending_changed_folder)

    def _resolve_run_number(self, folder: str, fname: str, elec: str | None, freq: float | None) -> int | None:
        """Get the run number for a file, assigning one if this is an
        internal-FC-board file that doesn't encode a run number in its
        filename. Safe to call multiple times for the same file (idempotent).
        Must be called in chronological order for FC-board files, since the
        cycle boundary is detected from segment-number resets relative to
        the previous file seen for that device.
        """
        cached = self._assigned_run_numbers.get((folder, fname))
        if cached is not None:
            return cached

        device_id = extract_device_id(fname)
        if device_id is None:
            # Single/multi-channel potentiostat file -- run number is
            # already embedded in the filename.
            run = extract_run_number(fname)
        else:
            seg = extract_segment_number(fname)
            prev_seg = self._device_prev_segment.get(device_id)
            current_run = self._device_current_run.get(device_id, 0)
            if prev_seg is None or seg is None or seg <= prev_seg:
                current_run += 1
                self._device_current_run[device_id] = current_run
            if seg is not None:
                self._device_prev_segment[device_id] = seg
            run = current_run

        if run is not None:
            self._assigned_run_numbers[(folder, fname)] = run
        return run

    def _is_file_stable(self, full_path: str) -> bool:
        try:
            with open(full_path, 'rb') as f:
                f.read(1024)
            return True
        except Exception:
            return False

    def _handle_folder_update(self, _):
        csv_path = os.path.join(self._data_output_path, "NDL_Data.csv")
        ready_path = os.path.join(self._data_output_path, "NDL_Data.ready")
        if not os.path.exists(csv_path) or not os.path.exists(ready_path):
            print("[DEBUG] NDL_Data.csv not fully ready — skipping update.")
            return
        else:
            # Use in-memory set captured after initial analysis; avoids read/write races
            already_processed = set(self._processed_files)
            new_tasks = 0
        for folder in self.folder_paths:
            try:
                # Only include likely SWV files: must include Hz and match "-<run>.txt"
                swv_run_pattern = re.compile(r"-\d+Hz-.+_(\d+)\.txt$")
                all_files = [
                    f for f in os.listdir(folder)
                    if swv_run_pattern.search(f) and f not in already_processed
                ]
                # Sort chronologically (by filename timestamp when present) so
                # that internal-FC-board files, which have no run number of
                # their own, get numbered in the order they were actually
                # scanned rather than in arbitrary directory-listing order.
                all_files.sort(key=lambda f: extract_filename_timestamp_key(f) or f)
            except Exception as e:
                print(f"[WARN] Could not read directory '{folder}': {e}")
                continue

            for fname in all_files:
                full_path = os.path.join(folder, fname)
                if not os.path.isfile(full_path):
                    continue
                if not self._is_file_stable(full_path):
                    print(f"[DEBUG] File not stable yet: {fname}")
                    continue

                # Try to find which group this file belongs to
                matched_group = None
                elec = extract_electrode(fname)
                for group, details in self.group_data.items():
                    swv_map = details.get("swv", {})
                    if folder in swv_map and elec in swv_map[folder]:
                        matched_group = group
                        break

                if matched_group:
                    print(f"[DEBUG] New file detected: {fname} (Group: {matched_group})")
                    freq = extract_frequency(fname)
                    self._resolve_run_number(folder, fname, elec, freq)
                    key = (matched_group, folder, fname)
                    if key not in self._pending_files:
                        self._pending_files.add(key)
                        self._start_parse_task(matched_group, folder, fname)
                    new_tasks += 1
                else:
                    print(f"[WARN] Could not match file to a group: {fname}")

        if new_tasks == 0:
            print("[DEBUG] No new SWV files to process.")

    def _queue_file_retry(self, folder_path, group, fname):
        def retry_later():
            print(f"[RETRY] Re-processing file after delay: {fname}")
            task = FileParseTask(self, group, folder_path, fname)
            QThreadPool.globalInstance().start(task)

        # Retry after 2 seconds
        QTimer.singleShot(2000, retry_later)

    def _start_parse_task(self, group, folder, fname):
        self._pending_parse_tasks += 1
        task = FileParseTask(self, group, folder, fname)
        QThreadPool.globalInstance().start(task)

    @Slot(str, str, str)
    def _on_parse_task_finished(self, group: str, folder: str, fname: str):
        self._pending_parse_tasks -= 1
        self._pending_files.discard((group, folder, fname))
        # Try updating graphs with new data
        for graph_num in range(1, 5):
            self.update_graph_lines(graph_num)

        print(f"[DEBUG] Finished processing: {fname} — Remaining tasks: {self._pending_parse_tasks}, pending files: {len(self._pending_files)}")

        if self._pending_files:
            # More files might be incoming, recheck after delay
            self.folder_update_timer.start(500)
        elif self._graph_screen_requested and self._pending_parse_tasks == 0:
            self._finalize_graph_analysis()

    def process_new_swv_file(self, group: str, folder_path: str, fname: str):
        """
        Read exactly one new SWV file, compute its metrics, and append a row to NDL_Data.csv.
        If run == norm_point, store its peak-current into self.reference_peaks.
        Otherwise, compute signal_change using the stored reference peak.

        Required members:
          • self.norm_point (int)
          • self.reference_peaks: dict[(str electrode, float freq) -> float]
          • self._data_output_path: path to output folder (where NDL_Data.csv lives)
        """
        # 1) Parse electrode, freq, run
        elec = extract_electrode(fname)      # e.g. "E1"
        freq = extract_frequency(fname)      # e.g. 60
        run  = self._resolve_run_number(folder_path, fname, elec, freq)  # e.g. 3

        if elec is None or freq is None or run is None:
            # Filename didn’t match expected pattern-ignore.
            return

        # 2) Read timestamp line and data
        full_path = os.path.join(folder_path, fname)
        ts_string = extract_timestamp(full_path) or ""
        print("ts_string:", ts_string)
        df = read_swv_text_file(full_path)
        if df.empty:
            # no data-ignore
            return

        use_smooth = self.fourier_enabled()
        kf = self.fourier_keep_frac()

        # raw data
        diff_array = df["Diff"].to_numpy()
        x_vals = df["Potential"].to_numpy()

        # smooth if enabled; otherwise pass raw through
        y_vals_proc = fourier_smooth(diff_array, keep_frac=kf) if use_smooth else diff_array

        # peak finding on the processed (smoothed or raw) series
        res = find_peak_and_baseline_dual(x_vals, y_vals_proc, min_distance=10)
        if not res:
            return
        peak_idx     = res["peak_idx"]
        peak_pot     = res["peak_potential"]
        peak_current = res["peak_current"]
        slope        = res["slope"]
        intercept    = res["intercept"]

        baseline_array     = slope * x_vals + intercept
        peak_baseline      = slope * peak_pot + intercept
        peak_minus_baseline = peak_current - peak_baseline

        # AUC on the same processed series
        auc_raw   = float(trapz(y_vals_proc, x_vals))
        auc_bline = float(trapz(baseline_array, x_vals))
        auc_combine = auc_raw - auc_bline

        # FWHM on baseline-corrected processed series
        curr_corr = y_vals_proc - baseline_array
        widths, heights, left_ips, right_ips = peak_widths(curr_corr, [peak_idx], rel_height=0.5)
        idxs = np.arange(len(x_vals))
        left_v  = float(np.interp(left_ips[0],  idxs, x_vals))
        right_v = float(np.interp(right_ips[0], idxs, x_vals))
        fwhm = abs(right_v - left_v)

        # iO2 from the same processed or raw? Requirement says “raw if unchecked, smoothed if checked”
        lowest_pot = x_vals.min()
        target_pot = lowest_pot * 0.9
        iO2 = float(np.interp(target_pot, x_vals, y_vals_proc))

        # 5) Compute signal_change (%) using the normalization point
        ref_key = (elec, freq)
        is_fc_board_file = extract_device_id(fname) is not None

        if is_fc_board_file:
            # Internal FC board: a frequency can be added to a monitoring
            # session partway through (its first appearance won't
            # necessarily land on norm_point), so the earliest-run scan
            # seen so far for that combo becomes its 0% baseline instead
            # of requiring an exact match to norm_point. Guarded by a lock
            # and compared by run number (not arrival order) since parse
            # tasks run on multiple worker threads and can finish out of
            # chronological order.
            with csv_write_lock:
                current_ref_run = self._reference_peak_runs.get(ref_key)
                if current_ref_run is None or run < current_ref_run:
                    self.reference_peaks[ref_key] = peak_minus_baseline
                    self._reference_peak_runs[ref_key] = run
                    is_reference = True
                else:
                    is_reference = False
                ref_pmb = self.reference_peaks.get(ref_key)
            if is_reference:
                signal_change = 0.0
            else:
                signal_change = (
                    np.nan if not ref_pmb
                    else ((peak_minus_baseline - ref_pmb) / ref_pmb) * 100.0
                )
        elif run == self.norm_point:
            # Store this run as the reference for this electrode/freq
            self.reference_peaks[ref_key] = peak_minus_baseline
            signal_change = 0.0
        else:
            ref_pmb = self.reference_peaks.get(ref_key)
            if ref_pmb is None or ref_pmb == 0:
                # We don't have a reference yet for this electrode/freq.
                # We still continue and write the row, but mark Signal Change as NaN.
                signal_change = np.nan
            else:
                signal_change = ((peak_minus_baseline - ref_pmb) / ref_pmb) * 100.0

        # 7) Prepare a dict for one CSV row
        row = {
            "Group": group,
            "Electrode": elec,
            "Frequency (Hz)": freq,
            "Run Number": run,
            "Timestamp": ts_string,
            "Peak Current (A)": round(peak_current, 12),
            "Peak Position (V)": round(peak_pot, 6),
            "Baseline Current (A)": round((slope * peak_pot + intercept), 12),
            "Peak - Baseline (A)": round((peak_current - (slope * peak_pot + intercept)), 12),
            "Signal Change (%)": (round(signal_change, 3) if pd.notna(signal_change) else np.nan),
            "AUC (A·V)": round(auc_raw, 12),
            "AUC Normalized (A·V)": round(auc_combine, 12),
            "FWHM (V)": round(fwhm, 6),
            "iO2 (A)": round(iO2, 12),
            "File Name": fname,
            "Folder Path": folder_path
        }

        # 8.5) Look up electrode constants
        norm_vals = self.cv_lookup.get((str(group), elec), {})
        print(f"[DEBUG] Lookup for ({group}, {elec}):", norm_vals)
        au_cm2 = norm_vals.get("Au cm2", np.nan)
        num_mb = norm_vals.get("Number MB", np.nan)
        packing_dens = norm_vals.get("Packing Density (MB/cm²)", np.nan)

        def safe_div(val, denom):
            return round(val / denom, 25) if pd.notna(val) and pd.notna(denom) and denom != 0 else np.nan

        row["Peak Current Norm (A/cm²)"] = safe_div(row["Peak Current (A)"], au_cm2)
        row["Peak Current Norm (A/#Apt)"]     = safe_div(row["Peak Current (A)"], num_mb)
        row["Peak Current Norm (A/PD)"]     = safe_div(row["Peak Current (A)"], packing_dens)

        row["Peak Height Norm (A/cm2)"]  = safe_div(row["Peak - Baseline (A)"], au_cm2)
        row["Peak Height Norm (A/#Apt)"]      = safe_div(row["Peak - Baseline (A)"], num_mb)
        row["Peak Height Norm (A/PD)"]      = safe_div(row["Peak - Baseline (A)"], packing_dens)

        row["Signal Change Norm (%/cm2)"] = safe_div(row["Signal Change (%)"], au_cm2)
        row["Signal Change Norm (%/#Apt)"]     = safe_div(row["Signal Change (%)"], num_mb)
        row["Signal Change Norm (%/PD)"]     = safe_div(row["Signal Change (%)"], packing_dens)

        row["AUC Norm (A·V/cm2)"] = safe_div(row["AUC Normalized (A·V)"], au_cm2)
        row["AUC Norm (A·V/#Apt)"]     = safe_div(row["AUC Normalized (A·V)"], num_mb)
        row["AUC Norm(A·V/PD)"]     = safe_div(row["AUC Normalized (A·V)"], packing_dens)
        # Skip if we've already processed this exact file name
        if fname in self._processed_files:
            return

        # 8) Append it to NDL_Data.csv (append-only, lock-guarded)
        csv_path = os.path.join(self._data_output_path, "NDL_Data.csv")

        # Compute dt_seconds / dt_hours incrementally using per-(Electrode,Freq) t0 cache
        try:
            ts_dt = pd.to_datetime(ts_string, errors='coerce') if ts_string else pd.NaT
        except Exception:
            ts_dt = pd.NaT
        key_pair = (str(elec), float(freq)) if freq is not None else (str(elec), float('nan'))
        t0 = self._t0_by_pair.get(key_pair)
        if pd.notna(ts_dt):
            if t0 is None or (pd.notna(t0) and ts_dt < t0):
                self._t0_by_pair[key_pair] = ts_dt
                t0 = ts_dt
            dt_seconds = (ts_dt - t0).total_seconds() if pd.notna(t0) else None
            row["dt_seconds"] = dt_seconds
            row["dt_hours"] = (dt_seconds / 3600.0) if dt_seconds is not None else None
        else:
            row["dt_seconds"] = None
            row["dt_hours"] = None

        # Normalize Timestamp formatting now to keep append cheap
        if ts_string:
            try:
                row["Timestamp"] = pd.to_datetime(ts_string, errors='coerce').strftime('%Y%m%d %H:%M:%S')
            except Exception:
                pass

        df_new = pd.DataFrame([row])
        with csv_write_lock:
            if not os.path.exists(csv_path):
                df_new.to_csv(csv_path, index=False, encoding='utf-8-sig')
            else:
                # Append without re-reading the entire CSV
                df_new.to_csv(csv_path, mode='a', header=False, index=False, encoding='utf-8-sig')

        # Update in-memory processed set AFTER a successful write
        self._processed_files.add(fname)
        print(f"Appended new file to CSV: {fname}  (Group={group}, E={elec}, {freq}Hz, Run {run})")

        return row

    def update_graph_lines(self, graph_num):
        """
        Optimized graph update: only updates lines and error bars, does not redraw entire layout.
        """
        ui = self._graph_widget.ui
        canvas = getattr(self._graph_widget, f"canvas{graph_num}", None)
        if canvas is None:
            return

        try:
            y_axis = getattr(ui, f'graph{graph_num}_yax').currentItem().text()
            if y_axis == "Concentration":
                metric_col = "Concentration"
            else:
                metric_col = METRIC_COLUMN.get(y_axis, "Signal Change (%)")
            self.graph_results = self.load_graph_results_from_csv(metric_col, graph_num)

            run_to_x, resolved_x_label = self._build_run_to_x_map(graph_num)

            # helper to fetch per-group concentration X from the conc table
            def _x_for(group_name: str, run: int, default: float) -> float:
                if not resolved_x_label == "Concentration":
                    return default
                conc_table = getattr(self._graph_widget.ui, f'conc_table_graph{graph_num}', None)
                if not (conc_table and conc_table.model()):
                    return default
                model = conc_table.model()
                from PySide6.QtCore import Qt as _QtU
                headers = [model.headerData(c, _QtU.Horizontal) for c in range(model.columnCount())]
                # find group column
                try:
                    col = next(i for i, h in enumerate(headers) if h == group_name)
                except StopIteration:
                    return default
                r = run - 1
                if r < 0 or r >= model.rowCount():
                    return default
                try:
                    raw = model.index(r, col).data()
                    return float(raw) if raw not in (None, "") else default
                except Exception:
                    return default

            # Get selected electrodes from the graph's table
            elec_table = getattr(ui, f'graph{graph_num}_electrodes_table', None)
            selected_elec_map: dict[str, set[str]] = {}
            if elec_table and elec_table.selectionModel():
                model = elec_table.model()
                from PySide6.QtCore import Qt
                col_headers = [model.headerData(c, Qt.Horizontal) for c in range(model.columnCount())]
                for idx in elec_table.selectionModel().selectedIndexes():
                    col = idx.column()
                    row = idx.row()
                    electrode_name = model.index(row, col).data()
                    group_name = col_headers[col]
                    if electrode_name:
                        selected_elec_map.setdefault(group_name, set()).add(electrode_name)

            lines = list(canvas.ax.lines)
            for line in lines:
                meta = getattr(line, "_meta", None)
                if not meta:
                    continue

                group = meta.get("group")
                if group not in self.graph_results:
                    continue

                freq = meta.get("frequency")
                elec = meta.get("electrode")
                average = meta.get("average", False)
                is_kdm = meta.get("kdm", False)

                if is_kdm and average:
                    electrodes = meta.get("electrodes", [])
                    runs_list = meta.get("runs", [])
                    data = self.graph_results.get(group, {})
                    run_vals_low = defaultdict(list)
                    run_vals_high = defaultdict(list)
                    low_freq = meta.get("low_freq")
                    high_freq = meta.get("high_freq")
                    if low_freq is None or high_freq is None:
                        continue

                    for (e, f), pts in data.items():
                        if e not in electrodes:
                            continue
                        for run, val in pts:
                            if f == low_freq:
                                run_vals_low[run].append(val)
                            elif f == high_freq:
                                run_vals_high[run].append(val)

                    common_runs = sorted(set(run_vals_low) & set(run_vals_high))
                    xs, ys, errs = [], [], []
                    for run in common_runs:
                        vals_low = run_vals_low[run]
                        vals_high = run_vals_high[run]
                        mean_low = np.mean(vals_low)
                        mean_high = np.mean(vals_high)
                        err = np.sqrt(
                            np.std(vals_low, ddof=1) ** 2 + np.std(vals_high, ddof=1) ** 2
                        )
                        xs.append(_x_for(group, run, run_to_x.get(run, run)))
                        ys.append(mean_high - mean_low)
                        errs.append(err)

                    line.set_data(xs, ys)
                    meta['xvals'] = xs
                    meta['runs'] = common_runs

                    # Rebuild the shaded ±SD band behind the mean line
                    try:
                        old_band = meta.get("band")
                        if old_band is not None:
                            old_band.remove()
                    except Exception:
                        pass

                    new_band = canvas.ax.fill_between(
                        np.asarray(xs, dtype=float),
                        np.asarray(ys, dtype=float) - np.asarray(errs, dtype=float),
                        np.asarray(ys, dtype=float) + np.asarray(errs, dtype=float),
                        facecolor=line.get_color(),
                        alpha=0.15,
                        edgecolor='none',
                        zorder=line.get_zorder() - 1
                    )
                    meta["band"] = new_band

                if average:
                    data = self.graph_results.get(group, {})
                    run_vals = {}
                    for (e, f), pts in data.items():
                        # Compare as floats—avoid string mismatch (e.g. "10" vs "10.0")
                        if float(f) != float(freq):
                            continue
                        if selected_elec_map and e not in selected_elec_map.get(group, set()):
                            continue
                        for run, val in pts:
                            run_vals.setdefault(run, []).append(val)

                    runs_sorted = sorted(run_vals)
                    x_vals = [_x_for(group, r, run_to_x.get(r, r)) for r in runs_sorted]
                    y_vals = [np.mean(run_vals[r]) for r in runs_sorted]
                    y_errs = [
                        np.std(run_vals[r], ddof=1) if len(run_vals[r]) > 1 else 0
                        for r in runs_sorted
                    ]
                    meta["runs"] = runs_sorted
                    meta["xvals"] = x_vals

                    # Update the main line
                    line.set_data(x_vals, y_vals)

                    # Rebuild the shaded ±SD band behind the mean line
                    try:
                        old_band = meta.get("band")
                        if old_band is not None:
                            old_band.remove()
                    except Exception:
                        pass

                    new_band = canvas.ax.fill_between(
                        np.asarray(x_vals, dtype=float),
                        np.asarray(y_vals, dtype=float) - np.asarray(y_errs, dtype=float),
                        np.asarray(y_vals, dtype=float) + np.asarray(y_errs, dtype=float),
                        facecolor=line.get_color(),
                        alpha=0.15,
                        edgecolor='none',
                        zorder=line.get_zorder() - 1
                    )
                    meta["band"] = new_band

                elif is_kdm and not average:
                    low_freq = meta.get("low_freq")
                    high_freq = meta.get("high_freq")
                    data = self.graph_results.get(group, {})

                    # Pull values for low and high frequencies
                    low_data = data.get((elec, low_freq), [])
                    high_data = data.get((elec, high_freq), [])

                    # Organize into run → value maps
                    low_map = {run: val for run, val in low_data}
                    high_map = {run: val for run, val in high_data}

                    common_runs = sorted(set(low_map) & set(high_map))
                    x_vals = [_x_for(group, run, run_to_x.get(run, run)) for run in common_runs]

                    if freq == low_freq:
                        y_vals = [low_map[run] for run in common_runs]
                    elif freq == high_freq:
                        y_vals = [high_map[run] for run in common_runs]
                    elif freq == "KDM":
                        y_vals = [high_map[run] - low_map[run] for run in common_runs]
                    else:
                        continue

                    line.set_data(x_vals, y_vals)

                    meta['xvals'] = x_vals
                    meta['runs'] = common_runs

                else:
                    # Individual line - update directly
                    run_data = self.graph_results[group].get((elec, freq), [])
                    if not run_data:
                        continue
                    # Extract runs and values in ascending run‐order
                    runs_list = [r for (r, _val) in run_data]
                    x_vals = [_x_for(group, r, run_to_x.get(r, r)) for r in runs_list]
                    y_vals = [v for (_, v) in run_data]
                    line.set_data(x_vals, y_vals)

                    # ─────────── Update the metadata so show_detail_graph can find the right run ───────────
                    meta['xvals'] = x_vals
                    meta['runs']  = runs_list

            canvas.ax.relim()
            canvas.ax.autoscale_view()
            canvas.draw_idle()

        except Exception as e:
            print(f"Error updating graph {graph_num}: {e}")

    def open_color_manager(self, canvas):
        """
        Gather (group, freq) pairs from what's currently plotted on this canvas,
        show a color picker dialog, apply changes immediately, and remember them.
        """
        # 1) Collect pairs present in this axes
        pairs = []
        for line in canvas.ax.lines:
            meta = getattr(line, "_meta", None)
            if not meta:
                continue
            group = meta.get("group")
            freq  = meta.get("frequency")
            if group is None or freq is None:
                continue
            # Store as float for numeric freqs; leave strings like "KDM" as-is
            try:
                freq_key = float(freq)
            except Exception:
                freq_key = freq  # e.g., "KDM"
            key = (str(group), freq_key)
            if key not in pairs:
                pairs.append(key)

        if not pairs:
            QMessageBox.information(self, "No Lines", "There are no lines on this graph to recolor yet.")
            return

        dlg = ColorManagerDialog(self, pairs, self.custom_colors)
        if dlg.exec():
            updates = dlg.result_colors()
            if not updates:
                return

            # 2) Update our global color map
            self.custom_colors.update(updates)

            # 3) Apply colors immediately to existing artists on this canvas
            #    (lines + errorbar components)
            for line in list(canvas.ax.lines):
                meta = getattr(line, "_meta", None)
                if not meta:
                    continue
                g = str(meta.get("group"))
                f = meta.get("frequency")
                try:
                    fkey = float(f)
                except Exception:
                    fkey = f
                hexc = self.custom_colors.get((g, fkey))
                if hexc:
                    try:
                        line.set_color(hexc)
                    except Exception:
                        pass

                band = meta.get("band")
                if band is not None and hexc:
                    try:
                        band.set_facecolor(hexc)
                        band.set_alpha(0.15)
                        band.set_edgecolor('none')
                    except Exception:
                        pass

            # 4) Redraw
            try:
                canvas.draw_idle()
            except Exception:
                pass

        # Rebuild legend so handle colors match
        handles, labels = canvas.ax.get_legend_handles_labels()
        if labels:
            legend = canvas.ax.legend(
                handles, labels,
                loc='center left', bbox_to_anchor=(1.0, 0.5)
            )
            for handle in legend.legendHandles:
                for line in canvas.ax.lines:
                    if line.get_label() == handle.get_label():
                        handle.set_color(line.get_color())


class GraphingWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_Graphing()
        self.setWindowIcon(QIcon(_ICON_PATH))
        self.ui.setupUi(self)        # build the widget tree

        # Dictionary to store the unique calibration window for each graph
        self._calibration_windows = {}

        # Hook up the 4 calibration buttons created in Qt Designer
        for i in range(1, 5):
            btn = getattr(self.ui, f"calib_graph{i}", None)
            if btn:
                # We use partial here to "freeze" the value of i.
                # Otherwise, all buttons would accidentally open Graph 4!
                btn.clicked.connect(partial(self.open_calibration_window, i))

        def showEvent(self, ev):
            super().showEvent(ev)
            # tile after the MDI has its final size
            QTimer.singleShot(0, self.mdi.tileSubWindows)

        old_mdi = self.ui.mdiArea
        new_mdi = AutoTileMdiArea(self)

        self.layout().replaceWidget(old_mdi, new_mdi)
        self.mdi = new_mdi                         # keep a handle

        self.mdi.setStyleSheet(
            """
            QMdiSubWindow {
                font-size: 0.1pt;
            }
            """
        )

        # ---- move every existing sub-window from old -> new ----
        for pane in old_mdi.subWindowList():   # safer than hard-coding names
            old_mdi.removeSubWindow(pane)      # detach from old parent
            self.mdi.addSubWindow(pane)        # re-parent into AutoTileMdiArea
            pane.setWindowFlags(QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowTitleHint | QtCore.Qt.WindowMinMaxButtonsHint)
            pane.show()

        old_mdi.deleteLater()                      # garbage-collect
        # --- postpone the very first tiling until widgets are sized ---
        QTimer.singleShot(0, self.mdi.tileSubWindows)

        # --- Graph tables: auto-populate when groups change ---
        self._graph_tables = [
            (self.ui.graph1_groups_list,
             self.ui.graph1_electrodes_table,
             self.ui.graph1_freq_table),
            (self.ui.graph2_groups_list,
             self.ui.graph2_electrodes_table,
             self.ui.graph2_freq_table),
            (self.ui.graph3_groups_list,
             self.ui.graph3_electrodes_table,
             self.ui.graph3_freq_table),
            (self.ui.graph4_groups_list,
             self.ui.graph4_electrodes_table,
             self.ui.graph4_freq_table),
        ]

        for groups_list, elec_table, freq_table in self._graph_tables:
            # multi-select & stretch for both tables
            for tv in (elec_table, freq_table):
                tv.setSelectionMode(QAbstractItemView.MultiSelection)
                tv.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

            # hook both populate methods to the groups_list signal
            groups_list.setSelectionMode(QAbstractItemView.MultiSelection)
            groups_list.itemSelectionChanged.connect(
                partial(self.populate_graph_electrodes, groups_list, elec_table)
            )
            groups_list.itemSelectionChanged.connect(
                partial(self.populate_graph_frequencies, groups_list, freq_table)
            )

            # start empty
            elec_table.setModel(QStandardItemModel(0, 0, self))
            freq_table.setModel(QStandardItemModel(0, 0, self))

        # Setup Concentration Tables (per-graph)
        self._conc_tables = [
            self.ui.conc_table_graph1,
            self.ui.conc_table_graph2,
            self.ui.conc_table_graph3,
            self.ui.conc_table_graph4,
        ]
        for tv in self._conc_tables:
            tv.setSelectionBehavior(QAbstractItemView.SelectItems)
            tv.setSelectionMode(QAbstractItemView.MultiSelection)
            tv.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            tv.setModel(QStandardItemModel(0, 0, self))  # start empty

        # When group selection changes in a graph -> rebuild its concentrations view
        pairs = (
            (self.ui.graph1_groups_list, self.ui.conc_table_graph1),
            (self.ui.graph2_groups_list, self.ui.conc_table_graph2),
            (self.ui.graph3_groups_list, self.ui.conc_table_graph3),
            (self.ui.graph4_groups_list, self.ui.conc_table_graph4),
        )
        for glw, ctv in pairs:
            glw.itemSelectionChanged.connect(partial(self.populate_graph_concentrations, glw, ctv))


    def populate_graph_electrodes(self, groups_list, table_view):
        """
        Each selected group → one column,
        rows = SWV electrodes in that group.
        """
        # 1) What groups are selected?
        selected = [item.text() for item in groups_list.selectedItems()]

        # 2) Grab your saved data (assumes MainWindow.group_data exists)
        main = self.window()
        all_data = getattr(main, "group_data", {})

        # 3) Build a list-of-lists of electrode names
        columns = []
        for grp in selected:
            swv_map = all_data.get(grp, {}).get("swv", {})
            flat = [e for lst in swv_map.values() for e in lst]
            # remove duplicates & sort by the integer part of "E<n>"
            flat = sorted(set(flat), key=lambda x: int(x[1:])) if flat else []
            columns.append(flat)

        # 4) Create the model: rows = tallest column, cols = number of groups
        row_count = max((len(col) for col in columns), default=0)
        model = QStandardItemModel(row_count, len(selected), self)
        model.setHorizontalHeaderLabels(selected)

        # 5) Fill in the cells
        for c, col in enumerate(columns):
            for r, label in enumerate(col):
                model.setItem(r, c, QStandardItem(label))

        # 6) Attach to the view
        table_view.setModel(model)

    
    def populate_graph_concentrations(self, groups_list, conc_table_view):
        """
        Build a concentration table with columns: Run + one column per *selected* group.
        Rows are aligned by run number so you can select per-group runs (cells).
        """
        selected_groups = [it.text() for it in groups_list.selectedItems()]
        main = self.window()
        by_group = getattr(main._conc_dialog, "_committed_by_group", {})

        # Determine rows: tallest selected group list
        max_len = 0
        for g in selected_groups:
            vals = by_group.get(g, [])
            if vals and len(vals) > max_len:
                max_len = len(vals)

        cols = 1 + len(selected_groups)
        model = QStandardItemModel(max_len + 1, cols, self)  # +1 blank row
        headers = ["Run"] + selected_groups
        model.setHorizontalHeaderLabels(headers)

        # fill rows
        for r in range(max_len):
            # run col (read-only)
            run_item = QStandardItem(str(r + 1))
            run_item.setFlags(run_item.flags() & ~Qt.ItemIsEditable)
            model.setItem(r, 0, run_item)
            # each group col
            for c, g in enumerate(selected_groups, start=1):
                lst = by_group.get(g, [])
                val = lst[r] if r < len(lst) else ""
                model.setItem(r, c, QStandardItem(val))

        # final blank row
        run_blank = QStandardItem("")
        run_blank.setFlags(run_blank.flags() & ~Qt.ItemIsEditable)
        model.setItem(max_len, 0, run_blank)
        for c in range(1, cols):
            model.setItem(max_len, c, QStandardItem(""))

        model.itemChanged.connect(partial(self.on_graph_conc_changed, conc_table_view))
        conc_table_view.setModel(model)

    def on_graph_conc_changed(self, tv, item):
        """
        Whenever the user edits a “Concentration” cell in any conc_table_graphX:
         - If they clear the text, clear the “Run” cell in that row.
         - If they type something non-empty into the last row’s “Concentration”, fill in the “Run”
           (row+1) and append a brand-new blank row at the bottom.
        """
        # We only care if the user changed a group column (anything > 0)
        if item.column() == 0:
            return

        model = tv.model()
        row = item.row()
        text = item.text().strip()

        # The “Run” cell is at column 0
        run_item = model.item(row, 0)

        # If they erased the cell, we don't necessarily want to clear the Run number
        # because other groups in this row might still have data. Just return.
        if not text:
            return

        # 1) If they typed something and the "Run" cell is blank, fill it in
        if not run_item or not run_item.text():
            if not run_item:
                run_item = QStandardItem(str(row + 1))
                run_item.setFlags(run_item.flags() & ~Qt.ItemIsEditable)
                model.setItem(row, 0, run_item)
            else:
                run_item.setText(str(row + 1))

        # 2) If this was the last row, immediately append a new blank row
        if row == model.rowCount() - 1:
            new_row = model.rowCount()
            model.insertRow(new_row)

            # Make the new "Run" cell non-editable and blank
            new_run = QStandardItem("")
            new_run.setFlags(new_run.flags() & ~Qt.ItemIsEditable)
            model.setItem(new_row, 0, new_run)

            # Fill the rest of the group columns with blank editable items
            for c in range(1, model.columnCount()):
                model.setItem(new_row, c, QStandardItem(""))

    def populate_graph_frequencies(self, groups_list, table_view):
        """
        Each selected group → one column,
        rows = unique Hz-values parsed from its SWV filenames,
        with a “KDM” row always at the top. If “KDM” is selected
        in any column, no more than two other rows in that
        column may be selected.
        """

        # 1) Which groups are selected?
        selected = [it.text() for it in groups_list.selectedItems()]
        main     = self.window()
        all_data = getattr(main, "group_data", {})

        # regex to pull out the number before 'Hz'
        pat = re.compile(r"-(\d+(?:\.\d+)?)Hz-")

        # 2) Build a list of (["KDM", freq1, freq2, ...], ["KDM", freqA, freqB, ...], …)
        freq_columns = []
        for grp in selected:
            swv_files_map = all_data.get(grp, {}).get("swv_files", {})
            freqs = set()
            for file_list in swv_files_map.values():
                for fname in file_list:
                    m = pat.search(fname)
                    if m:
                        freqs.add(m.group(1))

            # Sort the numeric frequencies, then prepend “KDM”
            sorted_freqs = sorted(freqs, key=lambda x: float(x))
            col = ["KDM"] + sorted_freqs
            freq_columns.append(col)

        # 3) Build a model whose row-count is the tallest column (including “KDM”)
        rows  = max((len(c) for c in freq_columns), default=0)
        model = QStandardItemModel(rows, len(selected), self)
        model.setHorizontalHeaderLabels(selected)

        # 4) Fill in each column (row 0 will always be “KDM” if that column exists)
        for c, col in enumerate(freq_columns):
            for r, freq in enumerate(col):
                model.setItem(r, c, QStandardItem(freq))

        table_view.setModel(model)

        # 5) Enforce: if “KDM” (row 0) is selected in column X, you may only select
        #    up to two other cells (rows ≠ 0) in that same column. If the user tries
        #    to select a third non-KDM cell, we immediately deselect it and pop up a warning.

        def on_selection_changed(selected_qsel, deselected_qsel):
            sel_model = table_view.selectionModel()
            for idx in selected_qsel.indexes():
                col = idx.column()

                # Is “KDM” in this column already selected?
                idx_kdm = model.index(0, col)
                if sel_model.isSelected(idx_kdm) and idx.row() != 0:
                    # Count how many non-KDM cells in this column are currently selected
                    others = [
                        i for i in sel_model.selectedIndexes()
                        if (i.column() == col and i.row() != 0)
                    ]
                    if len(others) > 2:
                        # Too many: immediately deselect the newly-selected cell
                        sel_model.select(idx, QItemSelectionModel.Deselect)
                        QMessageBox.warning(
                            self,
                            "Selection Limit",
                            "When KDM is selected, you can only choose two other frequencies\n"
                            f"in the \"{model.headerData(col, Qt.Horizontal)}\" column."
                        )

        table_view.selectionModel().selectionChanged.connect(on_selection_changed)

    def open_calibration_window(self, graph_num):
        """Launch or focus the independent calibration window for this specific graph."""

        # 1. Check if the window for this graph ALREADY exists in our dictionary
        if graph_num not in self._calibration_windows:

            # Get a reference to the main window to pass data back and forth
            main_win = self.window()

            # 2. Create the brand new instance of the CalibrationWindow
            calib_win = CalibrationWindow(main_window=main_win, graph_num=graph_num, parent=self)

            # Store it in our dictionary to prevent garbage collection
            self._calibration_windows[graph_num] = calib_win

            # 3. Show it as a modeless (non-blocking) window
            calib_win.show()

        else:
            # 4. If it already exists, just un-hide it and bring it to the front!
            # Because we aren't re-creating it, it perfectly remembers all previous selections.
            win = self._calibration_windows[graph_num]
            win.show()
            win.raise_()
            win.activateWindow()

class FolderCompilerDialog(QDialog, Ui_Compiler):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        # connect the “Add Folder” button
        self.add_folder_comp_button.clicked.connect(self.on_add_folder)

        # Connect the "Remove Folder" button
        self.rm_folder_comp_button.clicked.connect(self.on_remove_folder)

        # Connect Select Folder button
        self.select_folder_comp_button.clicked.connect(self.on_select_save_folder)

        # Connect Okay Button
        self.buttonBox.accepted.connect(self.compile_folders)

        # Make Folder Compiler Folder List Reorganizable
        lw = self.compile_folder_list
        lw.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        lw.setDragEnabled(True)
        lw.setAcceptDrops(True)
        lw.setDropIndicatorShown(True)
        lw.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)

        # Placeholder for folder path
        self.comp_folder_save_location = None

    def on_add_folder(self):
        # getExistingDirectory returns '' if the user cancels
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select a folder to compile",
            ""  # you can supply a default path here
        )
        if folder:
            # add the new folder path as a QListWidgetItem
            self.compile_folder_list.addItem(folder)

    def on_remove_folder(self):
        # grab all selected items
        for item in self.compile_folder_list.selectedItems():
            row = self.compile_folder_list.row(item)
            # remove that item from the widget
            self.compile_folder_list.takeItem(row)

    def on_select_save_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self,
            "Choose where to save the new folder",
            ""
        )
        if folder:
            # save it for later use
            self.comp_folder_save_location = folder
            print(self.comp_folder_save_location)
            # optionally show it somewhere in the UI-
            # for example if you added a QLineEdit named savePathLineEdit:
            try:
                self.savePathLineEdit.setText(folder)
            except AttributeError:
                pass

    def compile_folders(self):
            # 1) source folders from the list widget
            folders = [
                self.compile_folder_list.item(i).text()
                for i in range(self.compile_folder_list.count())
            ]
            # 2) output directory from the user’s selection
            output_dir = self.comp_folder_save_location
            if not folders:
                QMessageBox.warning(self, "No Folders",
                                    "Please add at least one folder to compile.")
                return
            if not output_dir:
                QMessageBox.warning(self, "No Output",
                                    "Please select an output folder.")
                return

            # ensure the output folder exists
            os.makedirs(output_dir, exist_ok=True)

            current_run = 1
            pattern = re.compile(r"(\d+)-(\d+Hz)-([^-]+)-(E\d+)-_(\d+)\.txt$")

            for folder in folders:
                files = [f for f in os.listdir(folder) if pattern.match(f)]
                runs: dict[int, list[tuple[str,str,str,str,str]]] = {}
                for f in files:
                    grp, freq, proto, elec, run_str = pattern.match(f).groups()
                    run = int(run_str)
                    runs.setdefault(run, []).append((f, grp, freq, proto, elec))

                if not runs:
                    continue

                counts = {r: len(v) for r, v in runs.items()}
                expected = max(counts.values())

                # copy only complete runs, renumbering and saving as text
                for run in sorted(runs):
                    if counts[run] != expected:
                        continue  # skip incomplete

                    for fname, grp, freq, proto, elec in runs[run]:
                        new_name = f"{grp}-{freq}-{proto}-{elec}-_{current_run}.txt"
                        src_path = os.path.join(folder, fname)
                        dst_path = os.path.join(output_dir, new_name)
                        # read+write in text mode
                        with open(src_path, 'r', encoding='utf-8') as fin, \
                             open(dst_path, 'w', encoding='utf-8') as fout:
                            fout.write(fin.read())
                    current_run += 1

            QMessageBox.information(self, "Done",
                                    "Folders compiled and runs renumbered successfully.")

class AutoTileMdiArea(QMdiArea):
    """QMdiArea that re-tiles itself whenever a child window is
    minimised, restored, or closed."""
    def __init__(self, parent=None):
        super().__init__(parent)

        # coalesce bursts of signals (e.g. user minimises two windows fast)
        self._retile_timer = QTimer(self, singleShot=True,
                                      timeout=self.tileSubWindows)
        self._retile = QTimer(self)
        self._retile.setSingleShot(True)
        self._retile.timeout.connect(self.tileSubWindows)

    def tileSubWindows(self):
        # 1) tile all non-minimized windows (Qt’s built-in behavior) :contentReference[oaicite:0]{index=0}
        super().tileSubWindows()

        # 2) now handle the minimized ones as “icons”
        icons = [w for w in self.subWindowList() if w.isMinimized()]
        if not icons:
            return

        # compute bottom-aligned Y coordinate
        area_rect = self.viewport().rect()
        icon_h   = icons[0].height()
        y        = area_rect.height() - icon_h

        # step through each icon, position it, and raise it to the top of the stack
        x = 0
        for w in icons:
            w.move(x, y)
            w.raise_()   # bring this icon above all other subwindows :contentReference[oaicite:1]{index=1}
            x += w.width()

    # Hook the moment you create / add a sub-window
    def addSubWindow(self, widget, flags=Qt.WindowFlags()):
        sub = super().addSubWindow(widget, flags)

        # 1) minimised/restored/maximised
        sub.windowStateChanged.connect(self._schedule)   # :contentReference[oaicite:0]{index=0}
        # 2) closed
        sub.destroyed.connect(self._schedule)

        return sub

    def resizeEvent(self, ev):
        super().resizeEvent(ev)
        self._schedule()                        # area just got wider / narrower

    def _schedule(self, *a):
        self._retile.start(0)                   # do it next event-loop cycle

    def _do_tile(self):
        self.tileSubWindows()
        self._retile.start(0)                   # do it next event-loop cycle

    def _maximise_if_single(self):
        live = [w for w in self.subWindowList() if not w.isMinimized()]
        if len(live) == 1:
            live[0].showMaximized()

class CalibrationWindow(QDialog):
    """Independent calibration window assigned to a specific graph."""
    def __init__(self, main_window, graph_num, parent=None):
        super().__init__(parent)
        self.ui = Ui_calib_window()
        self.ui.setupUi(self)

        self.main_window = main_window
        self.graph_num = graph_num  # 1, 2, 3, or 4

        self.setWindowTitle(f"Calibration Parameters - Graph {self.graph_num}")

        self.ui.model_dropdown.currentIndexChanged.connect(self.update_dynamic_inputs)
        self.update_dynamic_inputs()

        self.outputs_layout = QFormLayout(self.ui.calib_outputs)
        self.outputs_layout.addRow(QLabel("Waiting for data input..."))

        self.ui.calib_group.itemSelectionChanged.connect(self.populate_electrodes)
        self.ui.calib_group.itemSelectionChanged.connect(self.populate_frequencies)
        self.ui.calib_freq.itemSelectionChanged.connect(self.limit_freq_selection)
        self.ui.calib_group.itemSelectionChanged.connect(self.populate_concentrations)

        self.ui.calib_group.setSelectionMode(QAbstractItemView.SingleSelection)
        self.ui.calib_freq.setSelectionMode(QAbstractItemView.MultiSelection)
        self.ui.calib_elec.setSelectionMode(QAbstractItemView.MultiSelection)

        self.ui.fit_button.clicked.connect(self.run_fitting)

        self.populate_groups()

        # --- Graph Setup ---
        # Create the figure and canvas
        self.calib_fig = Figure(figsize=(5, 4))
        self.calib_ax = self.calib_fig.add_subplot(111)
        self.calib_canvas = FigureCanvas(self.calib_fig)
        self.calib_toolbar = NavigationToolbar(self.calib_canvas, self)

        # Add them to the calib_graph QFrame
        self.graph_layout = QVBoxLayout(self.ui.calib_graph)
        self.graph_layout.addWidget(self.calib_toolbar)
        self.graph_layout.addWidget(self.calib_canvas)

    def populate_groups(self):
        """Fills the QListWidget with the names of all groups currently in the software."""
        # 1. Clear any existing items (good practice if you ever refresh this list later)
        self.ui.calib_group.clear()

        # 2. Get the group names from the MainWindow's existing list widget
        group_names = [
            self.main_window.ui.group_names_list.item(i).text()
            for i in range(self.main_window.ui.group_names_list.count())
        ]

        # 3. Add them directly to this window's List Widget!
        self.ui.calib_group.addItems(group_names)

    def populate_electrodes(self):
        """Fills the calib_elec list based on the currently selected group(s)."""
        # 1. Clear the old electrodes
        self.ui.calib_elec.clear()

        # 2. Find out which groups are currently highlighted
        selected_groups = [item.text() for item in self.ui.calib_group.selectedItems()]
        if not selected_groups:
            return

        all_electrodes = set()

        # 3. Dig into the main window's data to find the SWV electrodes for these groups
        for grp in selected_groups:
            # Safely get the swv dictionary for this group (if it exists)
            swv_map = self.main_window.group_data.get(grp, {}).get("swv", {})

            # swv_map looks like: {'folder_path': ['E1', 'E2']}
            # We just want the lists of electrodes, so we extract all the values
            for elec_list in swv_map.values():
                all_electrodes.update(elec_list)

        # 4. Sort the electrodes numerically (so E10 comes after E2, not after E1)
        # It strips the "E" off the front, turns it to an integer, and sorts by that.
        try:
            sorted_electrodes = sorted(list(all_electrodes), key=lambda x: int(x[1:]))
        except ValueError:
            # Fallback just in case an electrode is named weirdly (like "Blank")
            sorted_electrodes = sorted(list(all_electrodes))

        # 5. Add them to the UI
        self.ui.calib_elec.addItems(sorted_electrodes)

    def populate_frequencies(self):
        self.ui.calib_freq.clear()
        selected_items = self.ui.calib_group.selectedItems()
        if not selected_items:
            return

        grp = selected_items[0].text()

        group_info = self.main_window.group_data.get(grp, {})
        swv_files_map = group_info.get("swv_files", {})

        # Pattern to pull the number before 'Hz'
        pat = re.compile(r"-(\d+(?:\.\d+)?)Hz-")
        found_freqs = set()

        for folder_path, file_list in swv_files_map.items():
                for fname in file_list:
                    match = pat.search(fname)
                    if match:
                        found_freqs.add(match.group(1))

        if found_freqs:
            # Sort numerically (float) so 100Hz comes after 10Hz
            sorted_freqs = sorted(list(found_freqs), key=lambda x: float(x))

            # Add "KDM" first, then the numeric frequencies
            self.ui.calib_freq.addItem("KDM")
            self.ui.calib_freq.addItems(sorted_freqs)
        else:
            print(f"DEBUG: No frequencies found for group {grp_name} in folders: {list(swv_files_map.keys())}")

    def populate_concentrations(self):
        """Fills the calib_conc table with selectable concentrations for the selected group."""
        from PySide6.QtWidgets import QTableWidgetItem, QAbstractItemView
        from PySide6.QtCore import Qt

        self.ui.calib_conc.clearContents()
        selected_groups = self.ui.calib_group.selectedItems()

        if not selected_groups:
            self.ui.calib_conc.setRowCount(0)
            return

        group_name = selected_groups[0].text().strip()
        conc_list = self.main_window._conc_dialog._committed_by_group.get(group_name, [])

        self.ui.calib_conc.setColumnCount(1)
        self.ui.calib_conc.setHorizontalHeaderLabels(["Concentration"])
        self.ui.calib_conc.setRowCount(len(conc_list))
        self.ui.calib_conc.horizontalHeader().setStretchLastSection(True)

        # Set to MultiSelection so clicking toggles the highlight without needing to hold Ctrl/Shift
        self.ui.calib_conc.setSelectionMode(QAbstractItemView.MultiSelection)

        for row, conc_value in enumerate(conc_list):
            val_str = conc_value.strip()

            item = QTableWidgetItem(val_str)

            # Make the item selectable and enabled, but NOT editable
            item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            self.ui.calib_conc.setItem(row, 0, item)

            # Default to highlighted/selected if there is a real concentration value
            if val_str:
                item.setSelected(True)

    def limit_freq_selection(self):
        """Limits selection to 3 items total if KDM is selected."""
        selected_items = self.ui.calib_freq.selectedItems()
        selected_texts = [it.text() for it in selected_items]

        if "KDM" in selected_texts and len(selected_items) > 3:
            # Block signals to prevent an infinite loop while deselecting
            from PySide6.QtCore import QSignalBlocker
            blocker = QSignalBlocker(self.ui.calib_freq)

            # Deselect the most recently clicked item
            current = self.ui.calib_freq.currentItem()
            if current:
                current.setSelected(False)

            QtWidgets.QMessageBox.warning(
                self,
                "Selection Limit",
                "When KDM is selected, you can only choose 2 additional frequencies (3 total)."
            )

    def update_dynamic_inputs(self):
        """Clears the parameter form and builds new inputs based on the selected model."""
        from PySide6.QtWidgets import QLineEdit

        # 1. Clear existing rows in the form layout from Qt Designer
        while self.ui.param_form.rowCount() > 0:
            self.ui.param_form.removeRow(0)

        # 2. Get the currently selected model
        selected_model = self.ui.model_dropdown.currentText()

        # 3. Create a dictionary to keep track of our active input boxes
        self.active_inputs = {}

        # --- Add the Fit Scale Dropdown at the very top ---
        self.x_scale_dropdown = QComboBox()
        self.x_scale_dropdown.addItems(["Linear", "Logarithmic"])
        self.ui.param_form.addRow("X-Axis Fit Scale:", self.x_scale_dropdown)

        # Helper function to create an input box and add it to the Designer layout
        def create_input(param_name, placeholder="(Auto-calculate)"):
            line_edit = QLineEdit()
            line_edit.setPlaceholderText(placeholder)
            self.active_inputs[param_name] = line_edit
            self.ui.param_form.addRow(f"{param_name}:", line_edit)

        # 4. Add the specific fields based on the model
        if selected_model == "Linear":
            create_input("Slope (m)")
            create_input("Y-Intercept (b)", "(Default: 0)")

        elif selected_model == "Langmuir (1:1)":
            create_input("Bmax")
            create_input("Kd")

        elif selected_model == "Hill Equation":
            create_input("Bmax")
            create_input("Kd")
            create_input("Hill Coefficient (n)", "(Default: 1)")

        elif selected_model == "4-Parameter Logistic (4PL)":
            create_input("Min Asymptote (a)")
            create_input("Max Asymptote (d)")
            create_input("Inflection Point (c)")
            create_input("Hill Slope (b)")

    def get_fitting_parameters(self):
        """
        Returns a dictionary of the chosen parameters.
        Empty strings mean the user wants the software to auto-calculate.
        """
        params = {
            "model_type": self.ui.model_dropdown.currentText(),
            "x_scale": self.x_scale_dropdown.currentText(),  # <-- NEW: Capture the scale
            "user_guesses": {}
        }

        for param_name, line_edit in self.active_inputs.items():
            user_text = line_edit.text().strip()
            if user_text:
                try:
                    params["user_guesses"][param_name] = float(user_text)
                except ValueError:
                    params["user_guesses"][param_name] = None
            else:
                params["user_guesses"][param_name] = None

        return params

    def display_fit_results(self, fit_results):
        """
        Clears the calib_outputs frame and populates it with the fit results, R2, and equation.
        """
        from PySide6.QtWidgets import QLabel

        while self.outputs_layout.rowCount() > 0:
            self.outputs_layout.removeRow(0)

        if not fit_results.get("success"):
            error_msg = fit_results.get("error", "Unknown error occurred.")
            error_label = QLabel(f"Fit Failed: {error_msg}")
            error_label.setStyleSheet("color: red; font-weight: bold;")
            self.outputs_layout.addRow(error_label)
            return

        model = fit_results.get("model_type")
        r2 = fit_results.get("r_squared")

        # --- NEW FORMATTER: Handles optional standard deviations ---
        def fmt(val, sd=None):
            if abs(val) < 0.01 or abs(val) > 1000:
                base_str = f"{val:.2e}"
            else:
                base_str = f"{val:.3f}"

            if sd is not None and sd > 0:
                if abs(sd) < 0.01 or abs(sd) > 1000:
                    sd_str = f"{sd:.2e}"
                else:
                    sd_str = f"{sd:.3f}"
                return f"{base_str} ± {sd_str}"

            return base_str

        # Note if multiple electrodes were averaged
        n_elecs = fit_results.get("n_electrodes")
        if n_elecs is not None:
            self.outputs_layout.addRow("Electrodes fitted:", QLabel(str(n_elecs)))

        if model == "Linear":
            m, b = fit_results["m"], fit_results["b"]
            m_sd = fit_results.get("m_sd")
            b_sd = fit_results.get("b_sd")

            self.outputs_layout.addRow("Slope (m):", QLabel(fmt(m, m_sd)))
            self.outputs_layout.addRow("Y-Intercept (b):", QLabel(fmt(b, b_sd)))
            self.outputs_layout.addRow("Mean R²:", QLabel(f"{r2:.4f}"))

            eq_str = f"y = {fmt(m)}x + {fmt(b)}"
            self.outputs_layout.addRow("Equation:", QLabel(eq_str))

        elif model == "Langmuir (1:1)":
            Bmax, Kd = fit_results["Bmax"], fit_results["Kd"]
            self.outputs_layout.addRow("Bmax (Emax):", QLabel(fmt(Bmax)))
            self.outputs_layout.addRow("Kd (EC50):", QLabel(fmt(Kd)))
            self.outputs_layout.addRow("R²:", QLabel(f"{r2:.4f}"))

            eq_str = f"y = ({fmt(Bmax)} * x) / ({fmt(Kd)} + x)"
            self.outputs_layout.addRow("Equation:", QLabel(eq_str))

        elif model == "Hill Equation":
            Bmax, Kd, n = fit_results["Bmax"], fit_results["Kd"], fit_results["n"]
            self.outputs_layout.addRow("Bmax (Emax):", QLabel(fmt(Bmax)))
            self.outputs_layout.addRow("Kd (EC50):", QLabel(fmt(Kd)))
            self.outputs_layout.addRow("Hill Coeff (n):", QLabel(fmt(n)))
            self.outputs_layout.addRow("R²:", QLabel(f"{r2:.4f}"))

            eq_str = f"y = ({fmt(Bmax)} * x^{fmt(n)}) / ({fmt(Kd)}^{fmt(n)} + x^{fmt(n)})"
            self.outputs_layout.addRow("Equation:", QLabel(eq_str))

        elif model == "4-Parameter Logistic (4PL)":
            a, b, c, d = fit_results["a"], fit_results["b"], fit_results["c"], fit_results["d"]
            self.outputs_layout.addRow("Min (a):", QLabel(fmt(a)))
            self.outputs_layout.addRow("Max (d):", QLabel(fmt(d)))
            self.outputs_layout.addRow("EC50 (c):", QLabel(fmt(c)))
            self.outputs_layout.addRow("Hill Slope (b):", QLabel(fmt(b)))
            self.outputs_layout.addRow("R²:", QLabel(f"{r2:.4f}"))

            eq_str = f"y = {fmt(d)} + ({fmt(a)} - {fmt(d)}) / (1 + (x / {fmt(c)})^{fmt(b)})"
            self.outputs_layout.addRow("Equation:", QLabel(eq_str))

    def run_fitting(self):
        """Extracts X and Y data from the UI and runs the curve fit based on selected concentrations."""
        import numpy as np
        from PySide6.QtWidgets import QMessageBox

        selected_groups = self.ui.calib_group.selectedItems()
        selected_elecs = self.ui.calib_elec.selectedItems()
        selected_freqs = self.ui.calib_freq.selectedItems()
        selected_yaxis = self.ui.calib_yaxis.currentItem()

        if not (selected_groups and selected_elecs and selected_freqs and selected_yaxis):
            QMessageBox.warning(self, "Missing Selection", "Please select a Group, at least one Electrode, Frequency, and Y-axis.")
            return

        group = selected_groups[0].text().strip()
        freq_str = selected_freqs[0].text().strip()
        y_axis_name = selected_yaxis.text().strip()

        if freq_str == "KDM":
            QMessageBox.warning(self, "KDM Fitting", "KDM fitting is complex. Please select a single standard frequency for now.")
            return

        try:
            freq_val = float(freq_str)
        except ValueError:
            freq_val = freq_str

        metric_col = METRIC_COLUMN.get(y_axis_name, "Signal Change (%)")
        structured_data = self.main_window.load_graph_results_from_csv(metric_col)
        conc_list = self.main_window._conc_dialog._committed_by_group.get(group, [])

        params = self.get_fitting_parameters()
        model_type = params["model_type"]
        x_scale = params.get("x_scale", "Linear")
        user_guesses = params["user_guesses"]

        is_avg_data = self.ui.avg_elec.isChecked()
        is_avg_lines = self.ui.avg_lines.isChecked()

        if not is_avg_data and not is_avg_lines:
            is_avg_data = True

        # --- THE NEW FILTER HELPER ---
        def is_run_selected(run_idx):
            """Returns True only if the cell at this run_idx is highlighted by the user."""
            if run_idx < self.ui.calib_conc.rowCount():
                item = self.ui.calib_conc.item(run_idx, 0)
                return item is not None and item.isSelected()
            return False

        # ==========================================
        # METHOD A: Average the Data, Then Fit
        # ==========================================
        if is_avg_data:
            run_y_map = {}
            for elec_item in selected_elecs:
                elec = elec_item.text().strip()
                y_data_tuples = structured_data.get(group, {}).get((elec, freq_val), [])
                for run_number, y_val in y_data_tuples:
                    run_y_map.setdefault(int(run_number), []).append(float(y_val))

            x_data = []
            y_data = []

            for run_number in sorted(run_y_map.keys()):
                run_index = run_number - 1

                # Filter: Skip this run entirely if the user un-highlighted it
                if is_run_selected(run_index):
                    if 0 <= run_index < len(conc_list):
                        x_str = conc_list[run_index].strip()
                        if x_str:
                            try:
                                x_data.append(float(x_str))
                                y_data.append(np.mean(run_y_map[run_number]))
                            except ValueError:
                                pass

            if len(x_data) < 2:
                QMessageBox.warning(self, "Not Enough Data", "Need at least 2 valid, selected data points to fit a curve.")
                return

            fitter = CalibrationFitter(x_data, y_data, x_scale)
            results = fitter.perform_fit(model_type, user_guesses)
            # --- Save the calibration globally ---
            if not hasattr(self.main_window, 'saved_calibrations'):
                self.main_window.saved_calibrations = {}

            # We save it using the Group and Frequency as the key
            self.main_window.saved_calibrations[(self.graph_num, float(freq_val))] = {
                "metric": y_axis_name, # Remember which raw signal we used!
                "results": results     # NOTE: Change 'results' to 'avg_results' when pasting into Method B!
            }
            self.display_fit_results(results)
            self.plot_calibration_curve(x_data, y_data, results, y_axis_name, x_scale)


        # ==========================================
        # METHOD B: Fit Individual Lines, Then Average
        # ==========================================
        elif is_avg_lines:
            successful_fits = []
            all_x_points = []
            all_y_points = []

            for elec_item in selected_elecs:
                elec = elec_item.text().strip()
                y_data_tuples = structured_data.get(group, {}).get((elec, freq_val), [])

                e_x = []
                e_y = []
                for run_number, y_val in y_data_tuples:
                    run_index = int(run_number) - 1

                    # Filter: Skip this run entirely if the user un-highlighted it!
                    if is_run_selected(run_index):
                        if 0 <= run_index < len(conc_list):
                            x_str = conc_list[run_index].strip()
                            if x_str:
                                try:
                                    e_x.append(float(x_str))
                                    e_y.append(float(y_val))
                                    all_x_points.append(float(x_str))
                                    all_y_points.append(float(y_val))
                                except ValueError:
                                    pass

                if len(e_x) >= 2:
                    fitter = CalibrationFitter(e_x, e_y, x_scale)
                    res = fitter.perform_fit(model_type, user_guesses)
                    if res.get("success"):
                        successful_fits.append(res)

            if not successful_fits:
                QMessageBox.warning(self, "Fit Failed", "Could not successfully fit any of the selected electrodes with the chosen concentrations.")
                return

            n_fits = len(successful_fits)
            avg_results = {
                "success": True,
                "model_type": model_type,
                "r_squared": np.mean([r["r_squared"] for r in successful_fits]),
                "n_electrodes": n_fits
            }

            if model_type == "Linear":
                avg_results["m"] = np.mean([r["m"] for r in successful_fits])
                avg_results["b"] = np.mean([r["b"] for r in successful_fits])
                if n_fits > 1:
                    avg_results["m_sd"] = np.std([r["m"] for r in successful_fits], ddof=1)
                    avg_results["b_sd"] = np.std([r["b"] for r in successful_fits], ddof=1)

            # --- Average the Langmuir parameters ---
            elif model_type == "Langmuir (1:1)":
                avg_results["Bmax"] = np.mean([r["Bmax"] for r in successful_fits])
                avg_results["Kd"] = np.mean([r["Kd"] for r in successful_fits])
                if n_fits > 1:
                    avg_results["Bmax_sd"] = np.std([r["Bmax"] for r in successful_fits], ddof=1)
                    avg_results["Kd_sd"] = np.std([r["Kd"] for r in successful_fits], ddof=1)

            # --- Average the Hill parameters ---
            elif model_type == "Hill Equation":
                avg_results["Bmax"] = np.mean([r["Bmax"] for r in successful_fits])
                avg_results["Kd"] = np.mean([r["Kd"] for r in successful_fits])
                avg_results["n"] = np.mean([r["n"] for r in successful_fits])
                if n_fits > 1:
                    avg_results["Bmax_sd"] = np.std([r["Bmax"] for r in successful_fits], ddof=1)
                    avg_results["Kd_sd"] = np.std([r["Kd"] for r in successful_fits], ddof=1)
                    avg_results["n_sd"] = np.std([r["n"] for r in successful_fits], ddof=1)

            elif model_type == "4-Parameter Logistic (4PL)":
                for param in ["a", "aaaaaqqb", "c", "d"]:
                    avg_results[param] = np.mean([r[param] for r in successful_fits])
                    if n_fits > 1:
                        avg_results[f"{param}_sd"] = np.std([r[param] for r in successful_fits], ddof=1)

            # --- NEW: Save the calibration globally! ---
            if not hasattr(self.main_window, 'saved_calibrations'):
                self.main_window.saved_calibrations = {}

            # We save it using the Group and Frequency as the key
            self.main_window.saved_calibrations[(self.graph_num, float(freq_val))] = {
                "metric": y_axis_name, # Remember which raw signal we used!
                "results": avg_results     # NOTE: Change 'results' to 'avg_results' when pasting into Method B!
            }
            self.display_fit_results(avg_results)
            self.plot_calibration_curve(all_x_points, all_y_points, avg_results, y_axis_name, x_scale)

    def plot_calibration_curve(self, x_data, y_data, fit_results, y_axis_name, x_scale):
        """Plots the data points and the fitted mathematical curve using the chosen scale."""
        import numpy as np

        # 1. Clear the old plot
        self.calib_ax.clear()

        # 2. Plot the raw/averaged data points
        self.calib_ax.plot(x_data, y_data, marker='o', linestyle='None', color='black', label="Data Points")

        # 3. Draw the fitted curve (if the fit was successful)
        if fit_results.get("success"):
            model = fit_results.get("model_type")

            if len(x_data) > 0:
                min_x = min(x_data)
                max_x = max(x_data) * 1.05

                # --- NEW: Dynamically generate smooth X points based on scale ---
                if x_scale == "Logarithmic":
                    if min_x <= 0:
                        min_x = 1e-4  # Log scale cannot start at absolute 0
                    x_smooth = np.logspace(np.log10(min_x), np.log10(max_x), 1000)
                else:
                    x_smooth = np.linspace(0 if min_x >= 0 else min_x, max_x, 1000)

                # Plot the specific curve model
                if model == "Linear":
                    m, b = fit_results["m"], fit_results["b"]
                    y_smooth = m * x_smooth + b
                    self.calib_ax.plot(x_smooth, y_smooth, color='red', linewidth=2, label="Linear Fit")

                elif model == "Langmuir (1:1)":
                    Bmax, Kd = fit_results["Bmax"], fit_results["Kd"]
                    y_smooth = (Bmax * x_smooth) / (Kd + x_smooth)
                    self.calib_ax.plot(x_smooth, y_smooth, color='blue', linewidth=2, label="Langmuir Fit")

                elif model == "Hill Equation":
                    Bmax, Kd, n = fit_results["Bmax"], fit_results["Kd"], fit_results["n"]
                    y_smooth = (Bmax * np.power(x_smooth, n)) / (np.power(Kd, n) + np.power(x_smooth, n))
                    self.calib_ax.plot(x_smooth, y_smooth, color='green', linewidth=2, label="Hill Fit")

                elif model == "4-Parameter Logistic (4PL)":
                    a, b_slope, c, d = fit_results["a"], fit_results["b"], fit_results["c"], fit_results["d"]
                    y_smooth = d + (a - d) / (1.0 + np.power((x_smooth + 1e-12) / (c + 1e-12), b_slope))
                    self.calib_ax.plot(x_smooth, y_smooth, color='purple', linewidth=2, label="4PL Fit")

        # 4. Format the plot visually
        conc_unit = self.main_window._conc_dialog.ui.conc_unit.text()
        self.calib_ax.set_xlabel(f"Concentration ({conc_unit})", fontweight="bold")
        self.calib_ax.set_ylabel(y_axis_name, fontweight="bold")
        self.calib_ax.set_title("Calibration Curve", fontweight="bold")

        # --- NEW: Apply the correct visual scale to the X-axis ---
        if x_scale == "Logarithmic":
            self.calib_ax.set_xscale('log')
        else:
            self.calib_ax.set_xscale('linear')

        self.calib_ax.grid(True, linestyle="--", alpha=0.6)
        self.calib_ax.legend()
        self.calib_fig.tight_layout()

        # 5. Redraw the canvas to show the updates
        self.calib_canvas.draw()

class AddConcDialog(QDialog):
    """
    Concentration editor that supports *per-group* concentration lists.

    - Columns: "Run" + one column per group (pulled live from MainWindow's group list)
    - Rows:    Run numbers. Each cell in a group's column is that group's concentration for that run.
    - Normalization point and units stay as-is in the dialog UI.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.setWindowTitle("Add Concentrations (per group)")

        # Snapshot storage for “Cancel”
        # Dict[str, list[str]]  e.g., {"Group A": ["0.1", "0.2", ...], "Group B": ["0.1", ...]}
        self._committed_by_group: dict[str, list[str]] = {}

        # Table wiring
        table = self.ui.conc_table
        table.setRowCount(0)
        # Selection isn't used here; this dialog is for raw editing
        table.cellChanged.connect(self._on_cell_changed)

        # Buttons
        self.ui.buttonBox.accepted.connect(self._on_accept)
        self.ui.buttonBox.rejected.connect(self._on_reject)

        self.ui.importconc.clicked.connect(self._on_import_clicked)
        self.ui.saveconc.clicked.connect(self._on_save_clicked)

        # First build
        self._refresh_columns()
        self._ensure_one_blank_row()
        self._commit()  # start with empty commit

    # ------- UI helpers -------
    def _groups(self) -> list[str]:
        try:
            mw = self.parent()
            glw = mw.ui.group_names_list
            return [glw.item(i).text() for i in range(glw.count())]
        except Exception:
            return []

    def _refresh_columns(self):
        """Rebuild headers: first column 'Run', then one column per group."""
        table = self.ui.conc_table
        with QtCore.QSignalBlocker(table):
            groups = self._groups()
            headers = ["Run"] + groups
            table.setColumnCount(len(headers))
            table.setHorizontalHeaderLabels(headers)
            # repopulate from committed snapshot if any
            self._rollback()

    def showEvent(self, ev):
        # If groups changed while dialog was hidden, refresh columns on show.
        self._refresh_columns()
        super().showEvent(ev)

    def _ensure_one_blank_row(self):
        table = self.ui.conc_table
        # ensure at least one row
        if table.rowCount() == 0:
            table.insertRow(0)
            # run column (read-only)
            item = QTableWidgetItem("")
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            table.setItem(0, 0, item)
            # rest blank
            for c in range(1, table.columnCount()):
                table.setItem(0, c, QTableWidgetItem(""))

    def _on_cell_changed(self, row, col):
        # Keep the "Run" column (col 0) auto-numbered.
        if col == 0:
            return
        table = self.ui.conc_table
        # determine if last row has any non-empty data -> append a new blank row
        last = table.rowCount() - 1
        # set run index for this row if any group cell has text
        any_text = False
        for c in range(1, table.columnCount()):
            it = table.item(row, c)
            if it and it.text().strip():
                any_text = True
                break

        with QtCore.QSignalBlocker(table):
            run_item = table.item(row, 0) or QTableWidgetItem("")
            run_item.setFlags(run_item.flags() & ~Qt.ItemIsEditable)
            table.setItem(row, 0, run_item)
            run_item.setText(str(row + 1) if any_text else "")

            if row == last and any_text:
                # append a new blank row
                nr = table.rowCount()
                table.insertRow(nr)
                # run col
                ritem = QTableWidgetItem("")
                ritem.setFlags(ritem.flags() & ~Qt.ItemIsEditable)
                table.setItem(nr, 0, ritem)
                # blank group cells
                for c in range(1, table.columnCount()):
                    table.setItem(nr, c, QTableWidgetItem(""))

    def _commit(self):
        """Save current table contents as the 'last good' state (per group)."""
        table = self.ui.conc_table
        groups = self._groups()
        snap: dict[str, list[str]] = {g: [] for g in groups}

        # Determine max filled row (any group has text)
        max_row = -1
        for r in range(table.rowCount()):
            has_text_any = False
            for c in range(1, table.columnCount()):
                it = table.item(r, c)
                if it and it.text().strip():
                    has_text_any = True
                    break
            if has_text_any:
                max_row = r

        # Build per-group lists up to max_row
        for gcol, g in enumerate(groups, start=1):
            vals: list[str] = []
            for r in range(max_row + 1):
                it = table.item(r, gcol)
                vals.append(it.text().strip() if it else "")
            snap[g] = vals

        self._committed_by_group = snap

    def _rollback(self):
        """Rebuild table from _committed_by_group snapshot (if any)."""
        table = self.ui.conc_table
        with QtCore.QSignalBlocker(table):
            groups = self._groups()
            table.setRowCount(0)

            # how many rows? tallest group list
            max_len = 0
            for g in groups:
                v = self._committed_by_group.get(g, [])
                if len(v) > max_len:
                    max_len = len(v)

            # create rows
            for r in range(max_len + 1):  # +1 for always-blank row
                row = table.rowCount()
                table.insertRow(row)
                # run col
                run_item = QTableWidgetItem("" if r == max_len else str(r + 1))
                run_item.setFlags(run_item.flags() & ~Qt.ItemIsEditable)
                table.setItem(row, 0, run_item)
                # group cols
                for gcol, g in enumerate(groups, start=1):
                    text = ""
                    lst = self._committed_by_group.get(g, [])
                    if r < len(lst):
                        text = lst[r]
                    table.setItem(row, gcol, QTableWidgetItem(text))

    def _on_accept(self):
        self._commit()
        self.hide()

    def _on_reject(self):
        self._rollback()
        self.hide()

    def _on_import_clicked(self):
            # 1. Open File Dialog for Excel files
            path, _ = QFileDialog.getOpenFileName(
                self,
                "Import Concentrations",
                "",
                "Excel Files (*.xlsx *.xls)"
            )
            if not path:
                return

            try:
                # 2. Read the Excel file using pandas
                df = pd.read_excel(path)

                if df.empty or len(df.columns) < 1:
                    QMessageBox.warning(self, "Invalid File", "The Excel file is empty or missing columns.")
                    return

                # 3. Sort by the first column (Run Number) to ensure rows are in correct order
                first_col = df.columns[0]
                df = df.sort_values(by=first_col).reset_index(drop=True)

                # 4. Get the active groups from the UI
                current_groups = self._groups()
                imported_count = 0

                # 5. Extract data only for groups that exist in our software
                for group in current_groups:
                    # Check if the group name matches a column header in Excel
                    if group in df.columns:
                        vals = []
                        for val in df[group]:
                            if pd.isna(val):
                                vals.append("")  # Handle blank cells
                            else:
                                # Clean up float formatting (e.g., turn 10.0 into "10")
                                if isinstance(val, float) and val.is_integer():
                                    vals.append(str(int(val)))
                                else:
                                    vals.append(str(val))

                        # Update our background dictionary with the new list
                        self._committed_by_group[group] = vals
                        imported_count += 1

                if imported_count > 0:
                    # 6. Rebuild the visual table with the updated data
                    self._rollback()

                    # Make sure we commit the state immediately so it saves properly
                    self._commit()

                    QMessageBox.information(self, "Import Successful", f"Imported concentrations for {imported_count} group(s).")
                else:
                    QMessageBox.warning(self, "No Matches Found",
                                        "None of the column headers in the Excel file matched your current groups.")

            except Exception as e:
                QMessageBox.critical(self, "Import Error", f"Failed to read Excel file:\n{str(e)}")

    def _on_save_clicked(self):
            # 1. Open File Dialog for saving, pre-populated with the requested file name
            path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Concentrations",
                "Titration Concentrations.xlsx",
                "Excel Files (*.xlsx)"
            )

            if not path:
                return

            # Ensure the file gets the correct extension if the user deletes it
            if not path.lower().endswith(".xlsx"):
                path += ".xlsx"

            try:
                # 2. Sync the dictionary with any unsaved typing currently visible in the UI table
                self._commit()

                # 3. Build the data structure for Pandas
                groups = self._groups()
                data = {}

                # Find the maximum number of runs across all groups so we know how many rows to make
                max_runs = 0
                for g in groups:
                    vals = self._committed_by_group.get(g, [])
                    if len(vals) > max_runs:
                        max_runs = len(vals)

                if max_runs == 0:
                    QMessageBox.warning(self, "No Data", "There are no concentrations to save.")
                    return

                # 4. Create the "Run Number" column (1, 2, 3...)
                data["Run Number"] = [i + 1 for i in range(max_runs)]

                # 5. Populate group columns
                for g in groups:
                    vals = self._committed_by_group.get(g, [])
                    # Pandas requires all columns to be the exact same length.
                    # We pad any shorter group lists with empty strings ("").
                    padded_vals = vals + [""] * (max_runs - len(vals))
                    data[g] = padded_vals

                # 6. Create the DataFrame and save to Excel
                df = pd.DataFrame(data)
                df.to_excel(path, index=False)

                QMessageBox.information(self, "Success", f"Concentrations saved successfully to:\n{path}")

            except Exception as e:
                QMessageBox.critical(self, "Save Error", f"Failed to save Excel file:\n{str(e)}")

    def get_normalization_point(self) -> int:
        try:
            return int(self.ui.norm_point.text().strip())
        except Exception:
            return 1

    def get_concentrations_by_group(self) -> dict[str, list[str]]:
        """Return a shallow copy of the committed per-group concentrations."""
        return dict(self._committed_by_group)

class FileParseTask(QRunnable):
    def __init__(self, main_window, group, folder_path, fname):
        super().__init__()
        self.main_window = main_window
        self.group = group
        self.folder_path = folder_path
        self.fname = fname

    @Slot()
    def run(self):
        print(f"[DEBUG] Parsing {self.fname} in background thread...")
        try:
            self.main_window.process_new_swv_file(self.group, self.folder_path, self.fname)
        except Exception as e:
            print(f"Error processing file in background: {e}")
        finally:
            # Only mark as finished after the processing attempt completes
            QtCore.QMetaObject.invokeMethod(
                self.main_window,
                "_on_parse_task_finished",
                Qt.QueuedConnection,
                QtCore.Q_ARG(str, self.group),
                QtCore.Q_ARG(str, self.folder_path),
                QtCore.Q_ARG(str, self.fname)
            )

class ColorManagerDialog(QDialog):
    """
    Simple table of (Group, Freq, Color) with a Pick… button per row.
    Returns a mapping for just the pairs shown.
    """
    def __init__(self, parent, pairs, current_colors):
        super().__init__(parent)
        from PySide6.QtWidgets import (
            QVBoxLayout,
            QTableWidget,
            QTableWidgetItem,
            QPushButton,
            QLabel,
            QDialogButtonBox,
        )
        from PySide6.QtCore import Qt

        self.setWindowTitle("Set Plot Colors")
        self.resize(450, 200)
        self._pairs = pairs
        self._colors = {}           # local edits: (group,freq) -> "#hex"
        self._current = current_colors

        lay = QVBoxLayout(self)

        table = QTableWidget(self)
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["Group", "Frequency", "Color", ""])
        table.setRowCount(len(pairs))
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setStretchLastSection(True)
        self._table = table
        lay.addWidget(table)

        def make_swatch(hexstr: str | None) -> QLabel:
            lbl = QLabel()
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setText("")  # just a colored box
            lbl.setMinimumWidth(60)
            # Use a stylesheet so it wins over the global app stylesheet
            color = hexstr if hexstr else "#cccccc"
            lbl.setStyleSheet(
                f"background-color: {color}; "
                "border: 1px solid #666;"
            )
            return lbl

        for r, (g, f) in enumerate(pairs):
            table.setItem(r, 0, QTableWidgetItem(str(g)))
            table.setItem(r, 1, QTableWidgetItem(str(f)))

            hexc = self._current.get((g, f))
            swatch = make_swatch(hexc)
            table.setCellWidget(r, 2, swatch)

            btn = QPushButton("Pick…", self)
            # Store row + keys on the button, so we always know which row to update
            btn.setProperty("row", r)
            btn.setProperty("group", g)
            btn.setProperty("freq", f)

            def handler(*, button=btn):
                from PySide6.QtWidgets import QColorDialog

                c = QColorDialog.getColor(parent=self)
                if not c.isValid():
                    return

                hexval = c.name()
                row = button.property("row")
                grp = button.property("group")
                fr = button.property("freq")

                # Update the swatch for *this* row only
                sw = self._table.cellWidget(row, 2)
                if sw is not None:
                    sw.setStyleSheet(
                        f"background-color: {hexval}; "
                        "border: 1px solid #666;"
                    )

                # Remember the change
                self._colors[(grp, fr)] = hexval

            btn.clicked.connect(handler)
            table.setCellWidget(r, 3, btn)

        # OK / Cancel (keep your existing code below this)
        bb = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            parent=self,
        )
        bb.accepted.connect(self.accept)
        bb.rejected.connect(self.reject)
        lay.addWidget(bb)

    def result_colors(self):
        """Return mapping for pairs we edited (only changed keys)."""
        return self._colors
