import os
import numpy as np
#import pandas as pd

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QDialog, QTabWidget, QFormLayout,
    QDoubleSpinBox, QPushButton, QDialogButtonBox, QFileDialog,
    QTableWidget, QTableWidgetItem, QLabel, QColorDialog
)
from PySide6 import QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.ticker import MultipleLocator, AutoLocator
from data_analysis import read_swv_text_file
from PySide6.QtCore import Qt
from data_analysis import fourier_smooth, find_peak_and_baseline_dual


class GraphToolbar(NavigationToolbar):
    """Custom toolbar that adds a new button for custom settings while preserving native tools."""

    def __init__(self, canvas, parent=None, main_window=None):
        super().__init__(canvas, parent)
        self._canvas = canvas
        self._main_window = main_window

        # Add a separator and our new custom settings button to the far right
        self.addSeparator()
        custom_settings_action = self.addAction("Custom Settings")
        custom_settings_action.setToolTip("Open custom NDL graph settings (Ticks, Colors, Export)")
        custom_settings_action.triggered.connect(self.open_custom_settings)

    # Note: We removed the edit_parameters() override!
    # The default gear icon will now natively open Matplotlib's axis/curve editor again.

    def open_custom_settings(self):
        """Launch our unified custom dialog."""
        self._custom_dlg = UnifiedSettingsDialog(self._canvas, self._main_window, self)
        self._custom_dlg.show()

class UnifiedSettingsDialog(QDialog):
    """A unified tabbed dialog for all graph settings."""

    def __init__(self, canvas, main_window, toolbar, parent=None):
        super().__init__(parent)
        self.canvas = canvas
        self.main_window = main_window
        self.toolbar = toolbar
        self.setWindowTitle("Graph Settings")
        self.resize(500, 400)

        layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # --- Setup Tabs ---
        self.setup_colors_tab()
        self.setup_ticks_tab()
        self.setup_export_tab()

        # Close Button
        btn_box = QDialogButtonBox(QDialogButtonBox.Close)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)

    def setup_ticks_tab(self):
        tab = QWidget()
        form = QFormLayout(tab)

        self.x_spin = QDoubleSpinBox()
        self.y_spin = QDoubleSpinBox()

        for spin in (self.x_spin, self.y_spin):
            spin.setDecimals(2)
            spin.setRange(0.0, 1e9)
            spin.setSingleStep(0.1)
            spin.setToolTip("0 = automatic spacing")

        ax0 = self.canvas.figure.get_axes()[0]
        xloc = ax0.xaxis.get_major_locator()
        yloc = ax0.yaxis.get_major_locator()

        self.x_spin.setValue(float(xloc.base) if isinstance(xloc, MultipleLocator) else 0.0)
        self.y_spin.setValue(float(yloc.base) if isinstance(yloc, MultipleLocator) else 0.0)

        btn_apply = QPushButton("Apply Ticks")
        btn_apply.setFixedWidth(120)
        btn_apply.clicked.connect(self.apply_ticks)

        form.addRow("ΔX major ticks (0 = auto):", self.x_spin)
        form.addRow("ΔY major ticks (0 = auto):", self.y_spin)
        form.addRow(btn_apply)

        self.tabs.addTab(tab, "Ticks")

    def apply_ticks(self):
        x_spacing = self.x_spin.value()
        y_spacing = self.y_spin.value()

        for ax in self.canvas.figure.get_axes():
            ax.xaxis.set_major_locator(MultipleLocator(x_spacing) if x_spacing > 0 else AutoLocator())
            ax.yaxis.set_major_locator(MultipleLocator(y_spacing) if y_spacing > 0 else AutoLocator())

        self.canvas.draw()

    def setup_colors_tab(self):
            tab = QWidget()
            lay = QVBoxLayout(tab)

            self.color_table = QTableWidget()
            self.color_table.setColumnCount(4)
            self.color_table.setHorizontalHeaderLabels(["Group", "Frequency", "Color", ""])
            self.color_table.verticalHeader().setVisible(False)
            self.color_table.horizontalHeader().setStretchLastSection(True)
            lay.addWidget(self.color_table)

            # Gather pairs from lines
            pairs = []
            for line in self.canvas.ax.lines:
                meta = getattr(line, "_meta", None)
                if not meta: continue
                group = meta.get("group")
                freq = meta.get("frequency")
                if group is None or freq is None: continue

                try:
                    freq_key = float(freq)
                except Exception:
                    freq_key = freq

                key = (str(group), freq_key)
                if key not in pairs:
                    pairs.append(key)

            self.color_table.setRowCount(len(pairs))

            def make_swatch(hexstr):
                lbl = QLabel()
                lbl.setAlignment(Qt.AlignCenter)
                lbl.setMinimumWidth(60)
                color = hexstr if hexstr else "#cccccc"
                lbl.setStyleSheet(f"background-color: {color}; border: 1px solid #666;")
                return lbl

            for r, (g, f) in enumerate(pairs):
                self.color_table.setItem(r, 0, QTableWidgetItem(str(g)))
                self.color_table.setItem(r, 1, QTableWidgetItem(str(f)))

                hexc = self.main_window.custom_colors.get((g, f))
                self.color_table.setCellWidget(r, 2, make_swatch(hexc))

                btn = QPushButton("Pick…")
                btn.setProperty("row", r)
                btn.setProperty("group", g)
                btn.setProperty("freq", f)
                btn.clicked.connect(lambda checked=False, b=btn: self.pick_color(b))
                self.color_table.setCellWidget(r, 3, btn)

            # --- ADDED: Explicit Apply Button ---
            btn_apply_colors = QPushButton("Apply Colors")
            btn_apply_colors.setFixedWidth(120)
            btn_apply_colors.clicked.connect(self.apply_colors)
            lay.addWidget(btn_apply_colors)

            self.tabs.addTab(tab, "Colors")

    def pick_color(self, button):
        c = QColorDialog.getColor(parent=self)
        if not c.isValid(): return

        hexval = c.name()
        row = button.property("row")
        grp = button.property("group")
        fr = button.property("freq")

        # Update swatch visually in the table
        sw = self.color_table.cellWidget(row, 2)
        if sw:
            sw.setStyleSheet(f"background-color: {hexval}; border: 1px solid #666;")

        # Save globally, but wait for the user to click "Apply Colors" to actually redraw the graph
        self.main_window.custom_colors[(grp, fr)] = hexval

    def apply_colors(self):
        for line in list(self.canvas.ax.lines):
            meta = getattr(line, "_meta", None)
            if not meta: continue

            g = str(meta.get("group"))
            f = meta.get("frequency")
            try: fkey = float(f)
            except: fkey = f

            hexc = self.main_window.custom_colors.get((g, fkey))
            if hexc:
                try: line.set_color(hexc)
                except Exception: pass

            band = meta.get("band")
            if band is not None and hexc:
                try:
                    band.set_facecolor(hexc)
                    band.set_alpha(0.15)
                    band.set_edgecolor('none')
                except Exception: pass

        # Re-sync legend
        handles, labels = self.canvas.ax.get_legend_handles_labels()
        if labels:
            legend = self.canvas.ax.legend(handles, labels, loc='center left', bbox_to_anchor=(1.0, 0.5))
            leg_handles = getattr(legend, 'legend_handles', getattr(legend, 'legendHandles', []))
            for handle in leg_handles:
                for line in self.canvas.ax.lines:
                    if line.get_label() == handle.get_label():
                        handle.set_color(line.get_color())

        self.canvas.draw()

    def setup_export_tab(self):
        tab = QWidget()
        form = QFormLayout(tab)

        orig_w, orig_h = self.canvas.figure.get_size_inches()

        self.w_spin = QDoubleSpinBox()
        self.h_spin = QDoubleSpinBox()
        for spin in (self.w_spin, self.h_spin):
            spin.setDecimals(2)
            spin.setRange(0.1, 100.0)
            spin.setSingleStep(0.1)

        self.w_spin.setValue(round(orig_w, 2))
        self.h_spin.setValue(round(orig_h, 2))

        btn_export = QPushButton("Export PDF")
        btn_export.setFixedWidth(120)
        btn_export.clicked.connect(self.export_pdf)

        form.addRow("Width (inches):", self.w_spin)
        form.addRow("Height (inches):", self.h_spin)
        form.addRow(btn_export)

        self.tabs.addTab(tab, "Export PDF")

    def export_pdf(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save PDF", "", "PDF Files (*.pdf)")
        if not path: return
        if not path.lower().endswith(".pdf"): path += ".pdf"

        fig = self.canvas.figure
        orig_w, orig_h = fig.get_size_inches()
        orig_dpi = fig.dpi

        try:
            fig.set_size_inches(self.w_spin.value(), self.h_spin.value())
            fig.subplots_adjust(left=0.15, right=0.85, bottom=0.16, top=0.85)
            fig.savefig(path, format="pdf", dpi=orig_dpi, bbox_inches="tight", pad_inches=0.0)
            QtWidgets.QMessageBox.information(self, "Success", "PDF Exported Successfully!")
        finally:
            fig.set_size_inches(orig_w, orig_h)
            fig.set_dpi(orig_dpi)
            fig.subplots_adjust(left=0.165, right=0.79, top=0.9, bottom=0.16)
            self.canvas.draw_idle()

class GraphCanvas(FigureCanvas):
    def __init__(self, parent=None, mdi_area=None):
        self.fig = Figure(figsize=(5, 4))
        self.ax = self.fig.add_subplot(111)
        self.fig.subplots_adjust(left=0.165, right=0.79, top=0.9, bottom=0.16)
        super().__init__(self.fig)
        self.setParent(parent)
        self.mdi_area = mdi_area
        self.mpl_connect("button_press_event", self.on_click)

        self._tooltip_annotation = self.ax.annotate(
            "", xy=(20, 20), xytext=(0, 0), textcoords="offset points",
            bbox=dict(boxstyle="round", fc="white", ec="black", lw=1),
            arrowprops=dict(arrowstyle="->"),
            ha='center', fontsize=10
        )
        self._tooltip_annotation.set_zorder(1000)
        self._tooltip_annotation.set_visible(False)
        self.mpl_connect("motion_notify_event", self.on_hover)

        # Hook up scroll wheel
        self.setMouseTracking(True)
        self.mpl_connect("scroll_event", self.on_scroll)

    def on_click(self, event):
        self._last_click_event = event
        if not event.inaxes:
            return
        click_x = event.xdata
        click_y = event.ydata

        min_dist = float('inf')
        closest_line = None

        for line in self.ax.lines:
            if not hasattr(line, "_meta"):
                        continue
            xdata = line.get_xdata()
            ydata = line.get_ydata()
            for x, y in zip(xdata, ydata):
                dist = (x - click_x) ** 2 + (y - click_y) ** 2
                if dist < min_dist:
                    min_dist = dist
                    closest_line = line

        threshold = 0.6 ** 2
        if min_dist > threshold:
            return

        if closest_line and hasattr(closest_line, '_meta'):
            meta = closest_line._meta
            # ————— If this was a KDM‐derived line, skip any subwindow—————
            if meta.get("frequency") == "KDM":
                return
            self.show_detail_graph(meta)


    def show_detail_graph(self, meta):
        if meta.get("average"):
            return self.show_avg_voltammogram(meta)

        group = meta["group"]
        electrode = meta["electrode"]
        freq = meta["frequency"]
        xvals = meta.get("xvals", [])
        runs = meta.get("runs", [])

        main_win = find_main_window(self)
        use_smooth = main_win.fourier_enabled()
        kf = main_win.fourier_keep_frac()

        last_evt = self._last_click_event
        if last_evt is None or last_evt.xdata is None:
            return
        clicked_x = last_evt.xdata
        idx = min(range(len(xvals)), key=lambda i: abs(xvals[i] - clicked_x))
        print(runs)
        run_clicked = runs[idx]
        if isinstance(freq, list):
            freq = freq[idx]
        main_win = find_main_window(self)
        swv_folders = main_win.group_data.get(group, {}).get("swv", {}).keys()
        target_substring = f"_{run_clicked}.txt"
        freq_substring = f"{int(freq)}Hz"

        for folder in swv_folders:
            try:
                files = os.listdir(folder)
            except Exception as e:
                print(f"[WARN] Could not read folder {folder}: {e}")
                continue

            for f in files:
                if electrode in f and freq_substring in f and target_substring in f:
                    fname = f
                    folder_path = folder
                    break
            if fname:
                break

        if not fname or not folder_path:
            print("Voltammogram file not found.")
            return

        file_path = os.path.join(folder_path, fname)
        group      = meta["group"]
        frequency  = meta["frequency"]
        electrode  = meta["electrode"]
        title_text = f"Voltammogram – {group}, {electrode}, {int(freq)} Hz, Run {run_clicked}"

        df = read_swv_text_file(file_path)
        if df.empty or "Potential" not in df or "Diff" not in df:
            return

        potentials = df["Potential"].to_numpy()
        currents   = df["Diff"].to_numpy()

        currents_s = fourier_smooth(currents, keep_frac=kf) if use_smooth else currents

        from scipy.signal import peak_widths
        res = find_peak_and_baseline_dual(potentials, currents_s, min_distance=10)
        if not res:
            return
        peak_idx   = res["peak_idx"]
        peak_pot   = res["peak_potential"]
        peak_cur   = res["peak_current"]
        slope      = res["slope"]
        intercept  = res["intercept"]

        baseline_y       = slope * potentials + intercept
        baseline_at_peak = slope * peak_pot + intercept
        peak_minus_base  = peak_cur - baseline_at_peak

        # AUC on smoothed minus baseline
        from numpy import trapezoid as trapz
        auc_raw = float(trapz(currents_s, potentials))
        auc_bln = float(trapz(baseline_y, potentials))
        auc_net = auc_raw - auc_bln

        # FWHM on baseline-corrected smoothed curve
        corr = currents_s - baseline_y
        widths, heights, left_ips, right_ips = peak_widths(corr, [peak_idx], rel_height=0.5)
        idxs = np.arange(potentials.size)
        left_v  = float(np.interp(left_ips[0],  idxs, potentials))
        right_v = float(np.interp(right_ips[0], idxs, potentials))
        fwhm_v  = abs(right_v - left_v)

        # --------- Plot popup ----------
        win = QWidget()
        lay = QVBoxLayout(win)
        fig = Figure(figsize=(5.0, 3.8))
        fig.subplots_adjust(left=0.165, right=0.79, top=0.9, bottom=0.16)
        ax  = fig.add_subplot(111)
        canvas = FigureCanvas(fig)
        # expose an 'ax' attribute so helper code (and future features) can treat it like GraphCanvas
        canvas.ax = ax
        lay.addWidget(canvas)
        lay.addWidget(GraphToolbar(canvas, win))

        # Raw (thin), Smoothed (thicker), Baseline (dashed)
        if use_smooth:
            ax.plot(potentials, currents, linewidth=1.0, label="Raw", color="tab:blue")
            ax.plot(potentials, currents_s, linewidth=1.0, label="Smoothed (FFT)", color="orange")
        else:
            ax.plot(potentials, currents, linewidth=1.0, label="Raw", color="tab:blue")
        ax.plot(potentials, baseline_y, linestyle="--", linewidth=1.0, color="black", label="Baseline")

        # Peak marker (Δ)
        ax.vlines(peak_pot, baseline_at_peak, peak_cur, linestyle="--", color="black", label="Peak Δ")

        # Annotation box with metrics
        txt = (
            f"Peak current: {peak_cur:.3e} A\n"
            f"Δ(peak–baseline): {peak_minus_base:.3e} A\n"
            f"AUC (net): {auc_net:.3e} A·V\n"
            f"FWHM: {fwhm_v:.4f} V"
        )
        ann = ax.annotate(
            txt, xy=(peak_pot, peak_cur), xytext=(40, -40), textcoords="offset points",
            bbox=dict(boxstyle="round", fc="white", ec="black"), arrowprops=dict(arrowstyle="->"), fontsize=9
        )
        try:
            ann.draggable(True)
        except Exception:
            pass

        ax.set_title(title_text)
        ax.set_xlabel("Potential (V)")
        ax.set_ylabel("Current (A)")
        ax.legend(loc="best")
        canvas.draw()

        if self.mdi_area:
            sub = self.mdi_area.addSubWindow(win)
            sub.setWindowTitle(f"Voltammogram – {group}, {electrode}, {int(freq)} Hz, Run {run_clicked}")
            sub.resize(560, 420)
            sub.show()
        else:
            win.resize(560, 420)
            win.show()

    
    def show_avg_voltammogram(self, meta):
            group       = meta["group"]
            freq        = meta["frequency"]
            xvals       = meta.get("xvals", [])
            runs        = meta.get("runs", [])
            electrodes  = meta.get("electrodes", [])
            graph_num   = meta.get("graph_num")

            main_win = find_main_window(self)
            use_smooth = main_win.fourier_enabled()
            kf = main_win.fourier_keep_frac()

            last_evt = self._last_click_event
            if last_evt is None or last_evt.xdata is None:
                return
            clicked_x = last_evt.xdata
            idx = min(range(len(xvals)), key=lambda i: abs(xvals[i] - clicked_x))
            run_clicked = runs[idx]
            if isinstance(freq, list):
                freq = freq[idx]
            main_win = find_main_window(self)
            graph_widget = main_win._graph_widget
            ui = graph_widget.ui
            selected_electrodes = set()
            if graph_num:
                elec_table = getattr(ui, f"graph{graph_num}_electrodes_table")
                model = elec_table.model()
                group_col = None
                for col in range(model.columnCount()):
                    header = model.headerData(col, Qt.Horizontal)
                    if header and header.strip().lower() == str(group).strip().lower():
                        group_col = col
                        break
                if group_col is not None:
                    for row in range(model.rowCount()):
                        idx2 = model.index(row, group_col)
                        if elec_table.selectionModel().isSelected(idx2):
                            name = idx2.data()
                            if name:
                                selected_electrodes.add(str(name))

            swv_folders = main_win.group_data.get(group, {}).get("swv", {}).keys()
            target_substring = f"_{run_clicked}.txt"
            freq_substring   = f"{int(freq)}Hz"

            file_paths = []
            for folder in swv_folders:
                try:
                    files = os.listdir(folder)
                except Exception:
                    continue
                for f in files:
                    if freq_substring in f and target_substring in f:
                        for elec in selected_electrodes:
                            elec_str = f"E{elec}" if isinstance(elec, int) else str(elec)
                            if elec_str in f:
                                file_paths.append(os.path.join(folder, f))
                                break
            if not file_paths:
                print("No matching SWV files found for averaged voltammogram.")
                return

            dfs = []
            for fp in file_paths:
                df_i = read_swv_text_file(fp)
                if not df_i.empty and "Potential" in df_i.columns and "Diff" in df_i.columns:
                    dfs.append(df_i[["Potential", "Diff"]].copy())
            if not dfs:
                print("No valid voltammogram data to average.")
                return

            potentials = dfs[0]["Potential"].to_numpy()
            for df_i in dfs[1:]:
                if not (df_i["Potential"].to_numpy() == potentials).all():
                    print("Potential mismatch — skipping plot.")
                    return

            diff_matrix = np.vstack([df_i["Diff"].to_numpy() for df_i in dfs])
            mean_diff   = np.mean(diff_matrix, axis=0)
            std_diff    = np.std(diff_matrix, axis=0, ddof=1)

            mean_diff_s = fourier_smooth(mean_diff, keep_frac=kf) if use_smooth else mean_diff

            from scipy.signal import find_peaks
            res = find_peak_and_baseline_dual(potentials, mean_diff_s, min_distance=10)
            if not res:
                print("No valid peak/baseline found in averaged data.")
                return
            peak_idx = res["peak_idx"]
            peak_pot = res["peak_potential"]
            peak_current = res["peak_current"]
            slope = res["slope"]
            intercept = res["intercept"]

            baseline_y = slope * potentials + intercept
            baseline_at_peak = slope * peak_pot + intercept
            peak_minus_baseline = peak_current - baseline_at_peak

            from numpy import trapezoid as trapz
            auc_raw  = float(trapz(mean_diff_s, potentials))
            auc_bln  = float(trapz(baseline_y,   potentials))
            auc_norm = auc_raw - auc_bln

            detail_win = QWidget()
            layout     = QVBoxLayout(detail_win)
            fig2       = Figure(figsize=(4.5, 3.5))
            fig2.subplots_adjust(left=0.165, right=0.79, top=0.9, bottom=0.16)
            ax2        = fig2.add_subplot(111)
            canvas2    = FigureCanvas(fig2)
            canvas2.ax = ax2
            layout.addWidget(canvas2)
            layout.addWidget(GraphToolbar(canvas2, detail_win))

            lower_band = mean_diff - std_diff
            upper_band = mean_diff + std_diff
            ax2.fill_between(potentials, lower_band, upper_band, color="tab:blue", alpha=0.3, label="±1 σ", zorder=1)

            if use_smooth:
                ax2.plot(potentials, mean_diff, linewidth=1.0, label="Raw Mean", color="tab:blue")
                ax2.plot(potentials, mean_diff_s, linewidth=1.0, label="Smoothed Mean (FFT)", color="orange")
            else:
                ax2.plot(potentials, mean_diff, linewidth=1.0, label="Raw Mean", color="tab:blue")
            ax2.plot(potentials, baseline_y,  linestyle="--", color="black", label="Baseline")
            ax2.vlines(peak_pot, baseline_at_peak, peak_current, color="black", linestyle="--", label="Peak Δ")

            ann_text = (
                f"Peak Current: {peak_current:.3e} A\n"
                f"Δ (Peak-Baseline): {peak_minus_baseline:.3e} A\n"
                f"AUC Norm: {auc_norm:.3e} A·V"
            )
            ann = ax2.annotate(
                ann_text, xy=(peak_pot, peak_current), xytext=(40, -40), textcoords="offset points",
                bbox=dict(boxstyle="round", fc="white", ec="black"), arrowprops=dict(arrowstyle="->"), fontsize=9
            )
            ann.draggable(True)

            ax2.set_title(f"{group} Avg Voltammogram @ {int(freq)} Hz (Run {run_clicked})")
            ax2.set_xlabel("Potential (V)")
            ax2.set_ylabel("Current (A)")
            ax2.legend(loc="upper right")
            canvas2.draw()

            if self.mdi_area:
                sub = self.mdi_area.addSubWindow(detail_win)
                sub.setWindowTitle(f"{group} Avg Voltammogram – {int(freq)} Hz – Run {run_clicked}")
                sub.resize(500, 360)
                sub.show()
    def on_hover(self, event):
        # 1) If the mouse is outside the plotting area, hide any existing tooltip and return
        if event.inaxes != self.ax or event.xdata is None or event.ydata is None:
            if self._tooltip_annotation.get_visible():
                self._tooltip_annotation.set_visible(False)
                try:
                    self.fig.canvas.draw_idle()
                except RuntimeError:
                    # the widget has already been destroyed; skip
                    pass
            return

        hover_x = event.xdata
        hover_y = event.ydata

        # 2) Find the closest point among all lines+points
        min_sq_dist = float("inf")
        closest_line = None
        closest_x = None
        closest_y = None

        closest_idx = 0 # Track the index

        # Exactly the same pattern as on_click(): loop through each Line2D that has _meta
        for line in self.ax.lines:
            if not hasattr(line, "_meta"):
                continue

            xdata = line.get_xdata()
            ydata = line.get_ydata()
            # ---> ADD enumerate to track the index
            for i, (x_pt, y_pt) in enumerate(zip(xdata, ydata)):
                dx = x_pt - hover_x
                dy = y_pt - hover_y
                sq_dist = dx*dx + dy*dy
                if sq_dist < min_sq_dist:
                    min_sq_dist = sq_dist
                    closest_line = line
                    closest_x = x_pt
                    closest_y = y_pt
                    closest_idx = i # Save the index

        # 3) Use the same threshold as on_click() did (0.6^2)
        threshold_sq = 0.6 ** 2
        if closest_line is None or min_sq_dist > threshold_sq:
            # No point is “close enough” → hide any existing tooltip
            if self._tooltip_annotation.get_visible():
                self._tooltip_annotation.set_visible(False)
                try:
                    self.fig.canvas.draw_idle()
                except RuntimeError:
                    # the widget has already been destroyed; skip
                    pass
            return

        # 4) Build and display tooltip for that closest point
        meta = closest_line._meta
        freq_val = meta['frequency'][closest_idx] if isinstance(meta.get('frequency'), list) else meta.get('frequency')
        tooltip_text = f"Group: {meta['group']}\nFreq: {freq_val} Hz"
        if meta.get("average"):
            tooltip_text += "\nType: Avg"
        else:
            tooltip_text += f"\nElec: {meta['electrode']}"

        # If we have explicit xvals in the metadata, show the x‐coordinate
        if "xvals" in meta:
            tooltip_text += f"\nx-axis: {closest_x:.1f}"

        # Format the y‐value according to whether it's “Signal Change (%)” or something else
        if meta.get("y_label") == "Signal Change (%)":
            tooltip_text += f"\ny-axis: {closest_y:.3f}%"
        else:
            tooltip_text += f"\ny-axis: {closest_y:.3e}"

        # Position the annotation at the exact data point:
        self._tooltip_annotation.xy = (closest_x, closest_y)
        self._tooltip_annotation.set_text(tooltip_text)
        self._tooltip_annotation.set_visible(True)
        self._tooltip_annotation.set_fontsize(10)

        # Finally, redraw so that the tooltip appears
        try:
            self.fig.canvas.draw_idle()
        except RuntimeError:
            # the widget has already been destroyed; skip
            pass

    def on_scroll(self, event):
        """Zoom in or out around the mouse position."""
        ax = self.ax
        # ignore scrolling outside the axes
        if event.inaxes != ax or event.xdata is None or event.ydata is None:
            return

        base_scale = 1.1
        # get current limits
        xleft, xright = ax.get_xlim()
        ybottom, ytop = ax.get_ylim()
        xdata, ydata = event.xdata, event.ydata

        # choose zoom direction
        if event.button == 'up':
            # zoom in
            scale_factor = 1 / base_scale
        elif event.button == 'down':
            # zoom out
            scale_factor = base_scale
        else:
            # no-op
            return

        # compute new width and height
        new_width  = (xright - xleft) * scale_factor
        new_height = (ytop   - ybottom) * scale_factor

        # compute relative position of cursor within axes
        relx = (xdata - xleft) / (xright - xleft)
        rely = (ydata - ybottom) / (ytop   - ybottom)

        # set new limits so that (xdata, ydata) stays under the cursor
        ax.set_xlim([
            xdata - new_width  * relx,
            xdata + new_width  * (1 - relx)
        ])
        ax.set_ylim([
            ydata - new_height * rely,
            ydata + new_height * (1 - rely)
        ])

        # trigger a redraw
        try:
            self.draw_idle()
        except RuntimeError:
            # the widget has already been destroyed; skip
            pass


def find_main_window(widget):
    while widget is not None:
        if hasattr(widget, "group_data") and hasattr(widget, "graph_results"):
            return widget
        widget = widget.parent()
    return None
