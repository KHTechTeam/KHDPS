# NOTE: 2025-09-03: Updated run_full_analysis to compute reference peaks using peak_minus_baseline
# This Python file uses the following encoding: utf-8

# if __name__ == "__main__":
#     pass
import os
import re
import datetime
import pandas as pd
import numpy as np
import logging
logger = logging.getLogger(__name__)
from PySide6.QtWidgets import QProgressDialog, QApplication
from PySide6.QtCore import Qt
from scipy.signal import find_peaks, savgol_filter
from scipy.interpolate import interp1d
from scipy.integrate import simpson
from scipy.signal import peak_widths
from scipy.optimize import curve_fit
from numpy import trapezoid as trapz

EASA_types = {"EASA Before Roughening", "EASA After Roughening"}

# --- Fourier smoother for SWV analysis ---
def fourier_smooth(y, keep_frac: float = 0.11):
    """
    Low-pass smooth via FFT. keep_frac in (0,1). Returns the SAME length as input.
    """
    y = np.asarray(y, dtype=float)
    n = y.size
    if n < 8 or not (0.0 < keep_frac < 1.0):
        return y.copy()
    Y = np.fft.rfft(y)
    k_keep = max(1, int(len(Y) * keep_frac))
    Y[k_keep:] = 0
    y_s = np.fft.irfft(Y, n)  # <-- preserve length
    return y_s

EPS_DENOM = 1e-12  # small tolerance to avoid divide-by-zero blowups

def safe_signal_change(curr_peak_minus_baseline: float,
                       ref_peak_minus_baseline: float) -> float:
    """
    Returns % signal change or np.nan if the reference is ~0.
    """
    import numpy as np
    ref = float(ref_peak_minus_baseline)
    if not np.isfinite(ref) or abs(ref) < EPS_DENOM:
        return np.nan
    return ((float(curr_peak_minus_baseline) - ref) / ref) * 100.0

# ---- Peak & baseline finder constrained to the middle 80% of potentials ----
def _mid80_window(x: np.ndarray) -> tuple[float, float]:
    """Return (lo, hi) bounds that exclude the first/last 10% of the potential span."""
    xmin = float(np.nanmin(x))
    xmax = float(np.nanmax(x))
    span = xmax - xmin
    lo = xmin + 0.10 * span
    hi = xmax - 0.10 * span
    return lo, hi

def find_peak_and_baseline_mid80(potential_array: np.ndarray,
                                 y_proc: np.ndarray,
                                 *,
                                 min_distance: int = 20):
    """
    Find the peak (max) and baseline line constrained to the middle 80% of potentials.
    Returns dict with {peak_idx, peak_potential, peak_current, slope, intercept, left_idx, right_idx}
    or None if it couldn’t be determined.
    """
    if potential_array.size < 3 or y_proc.size != potential_array.size:
        return None

    lo, hi = _mid80_window(potential_array)
    mid_mask = (potential_array >= lo) & (potential_array <= hi)
    if not np.any(mid_mask):
        return None

    # Candidate indices inside middle 80%
    cand = np.where(mid_mask)[0]
    # Peaks only from the mid window
    mid_y = y_proc[cand]
    peaks, _ = find_peaks(mid_y, distance=min_distance)
    if peaks.size == 0:
        return None
    abs_peaks = cand[peaks]
    peak_idx = int(abs_peaks[np.argmax(y_proc[abs_peaks])])
    peak_potential = float(potential_array[peak_idx])
    peak_current   = float(y_proc[peak_idx])

    # Baseline minima on each side, also constrained to mid window
    left_mask  = (potential_array <  peak_potential) & mid_mask
    right_mask = (potential_array >  peak_potential) & mid_mask
    if not left_mask.any() or not right_mask.any():
        return None

    left_abs_choices  = np.where(left_mask)[0]
    right_abs_choices = np.where(right_mask)[0]
    left_abs  = int(left_abs_choices[np.argmin(y_proc[left_abs_choices])])
    right_abs = int(right_abs_choices[np.argmin(y_proc[right_abs_choices])])

    x1, y1 = float(potential_array[left_abs]),  float(y_proc[left_abs])
    x2, y2 = float(potential_array[right_abs]), float(y_proc[right_abs])
    if x2 == x1:
        return None
    slope     = (y2 - y1) / (x2 - x1)
    intercept = y1 - slope * x1

    return {
        "peak_idx": peak_idx,
        "peak_potential": peak_potential,
        "peak_current": peak_current,
        "slope": float(slope),
        "intercept": float(intercept),
        "left_idx": left_abs,
        "right_idx": right_abs,
    }

def find_peak_and_baseline_dual(potential_array: np.ndarray,
                                y_proc: np.ndarray,
                                *,
                                min_distance: int = 20):
    """
    Try two strategies and return the one whose peak is closest to the
    midpoint of the potential span, but only if the peak-minus-baseline
    is non-zero.

    A) Peak-first, then baseline via minima on each side (middle 80% only).
    B) Baseline-first: split the middle-80% region in half by potential,
       take the minimum on each side, draw the baseline between those minima,
       then find the peak BETWEEN those minima.

    Returns the same dict schema as find_peak_and_baseline_mid80, plus:
      {"method": "A" or "B"}.
    """
    if potential_array.size < 3 or y_proc.size != potential_array.size:
        return None

    # Middle-80% mask
    lo, hi = _mid80_window(potential_array)
    mid_mask = (potential_array >= lo) & (potential_array <= hi)
    if not np.any(mid_mask):
        return None

    # --- Strategy A: reuse existing mid-80% logic ---
    res_A = find_peak_and_baseline_mid80(
        potential_array, y_proc, min_distance=min_distance
    )
    if res_A:
        res_A = dict(res_A)  # copy so we can annotate
        res_A["method"] = "A"

    # --- Strategy B: baseline-first between side minima ---
    res_B = None
    try:
        cand = np.where(mid_mask)[0]
        if cand.size:
            # Split by potential midpoint (not index midpoint)
            v_mid = 0.5 * (float(np.nanmin(potential_array))
                           + float(np.nanmax(potential_array)))
            left_choices  = cand[potential_array[cand] <= v_mid]
            right_choices = cand[potential_array[cand] >= v_mid]

            if left_choices.size and right_choices.size:
                left_idx  = int(left_choices[np.argmin(y_proc[left_choices])])
                right_idx = int(right_choices[np.argmin(y_proc[right_choices])])

                # Ensure order
                i1, i2 = (left_idx, right_idx) if left_idx < right_idx else (right_idx, left_idx)
                if i2 - i1 >= 2:
                    # Search peaks strictly between the two minima
                    seg = slice(i1, i2 + 1)
                    seg_y = y_proc[seg]

                    # local peaks in the segment
                    pk_rel, _ = find_peaks(seg_y, distance=min_distance)
                    if pk_rel.size == 0:
                        # fallback: take absolute max in the segment
                        pk_rel = np.array([int(np.argmax(seg_y))], dtype=int)

                    peak_idx = int(i1 + pk_rel[np.argmax(seg_y[pk_rel])])

                    # Line through the two minima
                    x1, y1 = float(potential_array[left_idx]),  float(y_proc[left_idx])
                    x2, y2 = float(potential_array[right_idx]), float(y_proc[right_idx])
                    if x2 != x1:
                        slope     = (y2 - y1) / (x2 - x1)
                        intercept = y1 - slope * x1
                        res_B = {
                            "peak_idx": peak_idx,
                            "peak_potential": float(potential_array[peak_idx]),
                            "peak_current": float(y_proc[peak_idx]),
                            "slope": float(slope),
                            "intercept": float(intercept),
                            "left_idx": int(left_idx),
                            "right_idx": int(right_idx),
                            "method": "B",
                        }
    except Exception:
        res_B = None

    def _has_nonzero_peak_minus_baseline(res) -> bool:
        if not res:
            return False
        peak_potential = float(res["peak_potential"])
        peak_current   = float(res["peak_current"])
        slope          = float(res["slope"])
        intercept      = float(res["intercept"])
        baseline_current   = slope * peak_potential + intercept
        peak_minus_baseline = peak_current - baseline_current
        # Treat numerically tiny values as zero
        return peak_minus_baseline > 5e-9

    A_ok = _has_nonzero_peak_minus_baseline(res_A)
    B_ok = _has_nonzero_peak_minus_baseline(res_B)

    # If only one has a non-zero peak-minus-baseline, use that one
    if A_ok and not B_ok:
        return res_A
    if B_ok and not A_ok:
        return res_B

    # If neither has a non-zero peak-minus-baseline, treat as no peak
    if not A_ok and not B_ok:
        return None

    # Both succeeded with non-zero peak-minus-baseline → choose the more central
    midV = 0.5 * (float(np.nanmin(potential_array)) + float(np.nanmax(potential_array)))
    dA = abs(res_A["peak_potential"] - midV)
    dB = abs(res_B["peak_potential"] - midV)
    return res_A if dA <= dB else res_B

def extract_timestamp(filepath: str) -> str | None:
    import datetime, re
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            for line in f:
                text = line.strip().replace('\ufeff', '')
                if not text:
                    continue

                # collapse multiple spaces (e.g., "   " → " ")
                text = re.sub(r'\s+', ' ', text)

                # remove trailing periods on abbreviated months (incl. "Sept.")
                text = re.sub(
                    r"\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)\.",
                    r"\1",
                    text,
                )

                # expand abbreviated months to full names, including "Sept"
                month_map = {
                    "Jan": "January", "Feb": "February", "Mar": "March", "Apr": "April",
                    "May": "May", "Jun": "June", "Jul": "July", "Aug": "August",
                    "Sep": "September", "Sept": "September", "Oct": "October",
                    "Nov": "November", "Dec": "December",
                }
                for abbr, full in month_map.items():
                    text = re.sub(rf"\b{abbr}\b", full, text)

                # Try common datetime formats (now with single spaces)
                for fmt in ("%B %d, %Y %H:%M:%S", "%b %d, %Y %H:%M:%S"):
                    try:
                        dt = datetime.datetime.strptime(text, fmt)
                        return dt.strftime("%Y%m%d %H:%M:%S")
                    except ValueError:
                        pass

                # Fallback: numeric epoch (ms or s)
                try:
                    ts_float = float(text)
                    if ts_float > 1e12:
                        ts_float /= 1000.0
                    dt = datetime.datetime.fromtimestamp(ts_float)
                    return dt.strftime("%Y%m%d %H:%M:%S")
                except ValueError:
                    continue
        return None
    except Exception:
        return None


def read_swv_text_file(filename):
    with open(filename, 'r', encoding='utf-8', errors='replace') as f:
        lines = f.readlines()
    data = []
    for line in lines[1:]:
        parts = line.strip().split(',')
        if len(parts) >= 2:
            try:
                data.append((float(parts[0]), abs(float(parts[1]))))
            except ValueError:
                continue
    df = pd.DataFrame(data, columns=["Potential", "Diff"])
    return df

def read_cv_text_file(filename):
    with open(filename, 'r', encoding='utf-8', errors='replace') as f:
        lines = f.readlines()
    data = []
    for line in lines[1:]:
        parts = line.strip().split(',')
        if len(parts) >= 2:
            try:
                data.append((float(parts[0]), float(parts[1])))
            except ValueError:
                continue
    df = pd.DataFrame(data, columns=["Potential", "Current"])
    return df

def extract_frequency(filename):
    match = re.search(r"-(\d+)Hz-", filename)
    return int(match.group(1)) if match else None

def extract_electrode(filename):
    match = re.search(r"(E\d+)", filename)
    if match:
        return match.group(1)
    # Fallback for files that don't use the "E1"/"E2" naming convention and
    # instead use a text label (e.g. "Low"/"High") as the electrode name,
    # like "01-5Hz-Low_1.txt" -> electrode "Low".
    match = re.search(r"\d+Hz-([A-Za-z][A-Za-z0-9]*)_\d+\.txt$", filename)
    return match.group(1) if match else None

def extract_run_number(filename):
    match = re.search(r"_(\d+)\.txt$", filename)
    return int(match.group(1)) if match else None

def extract_device_id(filename):
    """Return the 8-char hex device/session ID used by our internal FC-board
    files (e.g. "0001-120Hz-2ad60366-s1-E2-20260707_165119.txt" -> "2ad60366").
    Files from single/multi-channel potentiostats never have this segment,
    so this returns None for them.
    """
    match = re.search(r"\dHz-([0-9a-fA-F]{8})-s\d+-", filename)
    return match.group(1) if match else None

def extract_segment_number(filename):
    """Return the FC-board's within-cycle segment number (the "s1"/"s2"/"s3"
    in e.g. "...-s2-E2-...") -- this marks which frequency slot of one
    full sweep a scan belongs to, and resetting back down marks the start
    of a new cycle/run.
    """
    match = re.search(r"-s(\d+)-", filename)
    return int(match.group(1)) if match else None

def extract_filename_timestamp_key(filename):
    """Pull the trailing YYYYMMDD_HHMMSS stamp straight out of an FC-board
    filename (no need to open the file) so a batch of files can be sorted
    into chronological order cheaply.
    """
    match = re.search(r"(\d{8}_\d{6})\.txt$", filename)
    return match.group(1) if match else None

def compute_run_numbers(filenames):
    """Resolve a run number for every filename in a group/folder.

    - Files with an explicit run suffix (single/multi-channel potentiostats,
      e.g. "..._3.txt") keep using extract_run_number as before.
    - Files from our internal FC board (device ID present) don't encode a
      run number at all. A "run" for these is one full cycle through the
      device's configured frequencies -- the s1/s2/s3... segment marker
      identifies position within a cycle, and it resetting back down (not
      strictly increasing) marks the start of a new cycle. Time gaps are
      NOT used to detect cycle boundaries: automatic scans can be spaced by
      any configured interval, manual scans can happen in between, and
      disconnects can create large gaps that don't represent a real cycle
      break -- so timing is unreliable here. The resolved run number is
      shared across every electrode/frequency scanned within that cycle.

    Returns: dict[filename] -> int run number (only for filenames that
    could be resolved either way).
    """
    run_map = {}
    device_scans = {}  # device_id -> [(ts_key, segment, filename), ...]

    for fname in filenames:
        device_id = extract_device_id(fname)
        if device_id is None:
            run = extract_run_number(fname)
            if run is not None:
                run_map[fname] = run
            continue
        seg = extract_segment_number(fname)
        ts_key = extract_filename_timestamp_key(fname) or fname
        device_scans.setdefault(device_id, []).append((ts_key, seg, fname))

    for _, items in device_scans.items():
        items.sort(key=lambda item: item[0])
        current_run = 0
        prev_seg = None
        for _, seg, fname in items:
            if prev_seg is None or seg is None or seg <= prev_seg:
                current_run += 1
            run_map[fname] = current_run
            if seg is not None:
                prev_seg = seg

    return run_map

def select_reference_candidates(filenames, run_map, norm_point):
    """Return dict[(electrode, frequency)] -> list of filenames, ordered by
    preference, that could serve as the 0% baseline reference for that
    electrode/frequency combo. The caller should try them in order and use
    the first one where peak detection actually succeeds -- an early scan
    (e.g. before a sensor has equilibrated) may not show a real peak even
    though it's chronologically first, so the reference should fall through
    to the next available scan rather than silently dropping the whole
    frequency.

    - For single/multi-channel potentiostat files (no device ID), the only
      candidate is the file whose run number exactly matches norm_point,
      preserving the existing explicit-normalization-point behavior.
    - For internal FC-board files (device ID present), a frequency can be
      added to a monitoring session partway through (e.g. 300Hz only
      starting at cycle 38), so requiring an exact match to norm_point
      would silently drop it entirely. Candidates are every scan for that
      combo, ordered from earliest to latest cycle.
    """
    exact_matches = {}      # (elec, freq) -> [filename], non-device files at norm_point
    device_candidates = {}  # (elec, freq) -> [(run, filename), ...], device files

    for fname in filenames:
        run = run_map.get(fname)
        if run is None:
            continue
        elec = extract_electrode(fname)
        freq = extract_frequency(fname)
        key = (elec, freq)
        if extract_device_id(fname) is None:
            if run == norm_point:
                exact_matches[key] = [fname]
        else:
            device_candidates.setdefault(key, []).append((run, fname))

    candidates = dict(exact_matches)
    for key, items in device_candidates.items():
        items.sort(key=lambda pair: pair[0])
        candidates.setdefault(key, [fname for _, fname in items])
    return candidates

# Extract CV Electrode List, Scan Rate, Runs
def extract_cv_electrode(fname: str) -> str | None:
    match = re.match(r"(E\d+)-\d+(?:\.\d+)?[_-]\d+", fname)
    return match.group(1) if match else None

def extract_cv_scanrate(fname: str) -> float | None:
    match = re.match(r"E\d+-(\d+(?:\.\d+)?)[_-]\d+", fname)
    return float(match.group(1)) if match else None

def extract_cv_run(fname: str) -> int | None:
    match = re.match(r"E\d+-\d+(?:\.\d+)?[_-](\d+)", fname)
    return int(match.group(1)) if match else None

def analyze_cv_peak_multi_cycle(df: pd.DataFrame,
                                scanrate: float,
                                peak_range=(0.6, 1.1),
                                baseline_ranges=[(0.3, 0.6), (1.1, 1.2)]) -> dict:
    potential = df["Potential"].values
    current = df["Current"].values

    # Detect switching points based on changes in sweep direction
    direction = np.sign(np.diff(potential))
    switches = np.where(np.diff(direction) != 0)[0] + 1
    if len(switches) < 2:
        return {}

    # Split into cycles (or half-cycles)
    cycles = []
    for i in range(len(switches) - 1):
        start, end = switches[i], switches[i+1]
        p_slice = potential[start:end]
        c_slice = current[start:end]
        if len(p_slice) < 10:
            continue

        # Reverse sweep: potential decreases from start to end
        if p_slice[0] > p_slice[-1]:
            cycles.append((p_slice, c_slice))

    if not cycles:
        return {}

    # Interpolate all reverse cycles to common potential grid
    common_pot = np.linspace(min(potential), max(potential))
    interp_currents = []

    for p, c in cycles:
        try:
            f = interp1d(p, c, kind='linear', bounds_error=False, fill_value="extrapolate")
            interp_currents.append(f(common_pot))
        except Exception:
            continue

    if not interp_currents:
        return {}

    avg_current = np.mean(interp_currents, axis=0)

    # Identify peak and baseline regions
    # Find the min point in each baseline region
    baseline_points = []
    for r in baseline_ranges:
        mask = (common_pot > r[0]) & (common_pot < r[1])
        if not np.any(mask):
            continue
        min_idx = np.argmin(avg_current[mask])
        pot_vals = common_pot[mask]
        cur_vals = avg_current[mask]
        baseline_points.append((pot_vals[min_idx], cur_vals[min_idx]))

    if len(baseline_points) != 2:
        return {}

    # Extract x/y from baseline region minima
    (x1, y1), (x2, y2) = baseline_points
    if x1 > x2:
        x1, x2 = x2, x1
        y1, y2 = y2, y1

    # Linear baseline between x1 and x2
    slope = (y2 - y1) / (x2 - x1)
    intercept = y1 - slope * x1

    # Mask for all points between x1 and x2
    integration_mask = (common_pot >= x1) & (common_pot <= x2)
    x_vals = common_pot[integration_mask]
    y_vals = avg_current[integration_mask]
    baseline_y = slope * x_vals + intercept

    # Compute baseline-corrected AUC
    delta_y = y_vals - baseline_y
    auc = simpson(delta_y, x_vals)
    qau_transf = auc/scanrate if scanrate else np.nan
    num_au = qau_transf/0.000385

    # Also update peak current and height
    peak_idx = np.argmax(y_vals)
    peak_current = y_vals[peak_idx]
    baseline_at_peak = baseline_y[peak_idx]
    peak_height = peak_current - baseline_at_peak

    return {
        "Peak_Current": peak_current,
        "Peak_Height": peak_height,
        "AUC": auc,
        "Q_Au": round(qau_transf, 12),
        "Au cm2": round(num_au, 12)
    }

def analyze_cv_initial(df: pd.DataFrame,
                       scanrate: float,
                       baseline_range=(-0.1, -0.5),
                       peak_range=(-0.4, -0.2),
                       smooth_window=31,
                       smooth_polyorder=3,
                       #peak_prominence=1e-9,
                       peak_distance=3,
                       baseline_offset=0.1,
                       baseline_width=0.05) -> dict:
    """
    Analyzes initial CV data by averaging the reduction (forward) sweeps
    where potential decreases (e.g., -0.1 -> -0.5),
    smoothing the result, locating the reduction peak within a window,
    printing all detected peak potentials, fitting a linear baseline around the
    chosen peak, and computing baseline-corrected AUC.

    Parameters:
      df               : DataFrame with 'Potential' and 'Current'
      baseline_range   : unused (retained for compatibility)
      peak_range       : (min_potential, max_potential) to search for peak
      smooth_window    : window length for Savitzky-Golay filter (odd integer)
      smooth_polyorder : polynomial order for Savitzky-Golay filter
      peak_prominence  : min prominence for peak detection
      peak_distance    : min separation (in indices) between peaks
      baseline_offset  : potential offset from peak to start baseline windows
      baseline_width   : width of each baseline window around peak (in V)
    """
    pot = df['Potential'].values
    curr = df['Current'].values

    # 1) Identify direction switches
    direction = np.sign(np.diff(pot))
    switches = np.where(np.diff(direction) != 0)[0] + 1
    if len(switches) < 2:
        return {}

    # 2) Collect reduction (forward) sweeps: potential decreasing
    cycles = []
    for i in range(len(switches) - 1):
        s, e = switches[i], switches[i+1]
        p_slice, c_slice = pot[s:e], curr[s:e]
        if len(p_slice) < 10:
            continue
        # now pick sweeps where potential goes from high to low
        if p_slice[0] > p_slice[-1]:  # forward (reduction) sweep
            cycles.append((p_slice, c_slice))
    if not cycles:
        return {}

    # 3) Interpolate to common grid
    common_pot = np.linspace(pot.min(), pot.max(), 500)
    interp_vals = []
    for p_slice, c_slice in cycles:
        fn = interp1d(p_slice, c_slice, kind='linear',
                      bounds_error=False, fill_value='extrapolate')
        interp_vals.append(fn(common_pot))
    avg_curr = np.mean(interp_vals, axis=0)

    # 4) Smooth the averaged trace
    if smooth_window >= len(avg_curr):
        smooth_window = len(avg_curr) - (1 - len(avg_curr)%2)
    smooth_curr = savgol_filter(avg_curr, smooth_window, smooth_polyorder)

    # 5) Peak detection in specified window
    mask_peak = (common_pot >= peak_range[0]) & (common_pot <= peak_range[1])
    rel = smooth_curr[mask_peak]
    peaks, props = find_peaks(rel,
                               distance=peak_distance)
    if not len(peaks):
        print(f"No peaks in {peak_range}")
        return {}
    # map back to full index and pick highest
    idxs = np.where(mask_peak)[0][peaks]
    peak_idx = idxs[np.argmax(smooth_curr[idxs])]
    V_peak, I_peak = common_pot[peak_idx], smooth_curr[peak_idx]

    # 6) Baseline fitting around peak
    left_win = ((common_pot >= V_peak - baseline_offset - baseline_width)
                & (common_pot <= V_peak - baseline_offset))
    right_win = ((common_pot >= V_peak + baseline_offset)
                 & (common_pot <= V_peak + baseline_offset + baseline_width))
    pot_base = np.concatenate([common_pot[left_win], common_pot[right_win]])
    I_base   = np.concatenate([smooth_curr[left_win],    smooth_curr[right_win]])
    if len(pot_base) < 2:
        print("Insufficient baseline points")
        return {}
    coef = np.polyfit(pot_base, I_base, deg=1)
    baseline_line = np.polyval(coef, common_pot)

    # Compute Peak Height
    cv_peak_height = I_peak - baseline_line[peak_idx]

    # 7) Compute baseline-corrected AUC
    auc = trapz(avg_curr - baseline_line, common_pot)
    qmb_transf = auc/scanrate if scanrate else np.nan
    num_mb = qmb_transf*(3.12e18)

    return {
        'Peak_Current'  : round(I_peak, 12),
        'Peak_Height' : round(cv_peak_height, 12),
        'AUC'           : round(auc, 12),
        'Q_MB': round(qmb_transf, 12),
        'Number MB': round(num_mb, 3)
    }


def run_full_analysis(group_data, norm_point, output_dir, parent=None, use_smoothing: bool = False, keep_frac: float = 0.11):
    progress = QProgressDialog("Analyzing data...", "Cancel", 0, 100, parent)
    progress.setWindowModality(Qt.WindowModal)
    progress.setValue(0)

    def pick_number_mb(subdf):
        """
        Choose the best 'Number MB' for a (Group, Electrode) block.

        If the column doesn't exist at all (e.g. EASA-only CVs), return NaN.
        Prefer:
          1) 'CVs With Hydrogel'
          2) 'CVs Without Hydrogel'
          3) any non-NaN value if present
        """
        if "Number MB" not in subdf.columns:
            return np.nan

        for tag in ("CVs With Hydrogel", "CVs Without Hydrogel"):
            mask = subdf["Data Type"] == tag
            if not mask.any():
                continue
            vals = subdf.loc[mask, "Number MB"].dropna()
            if not vals.empty:
                return vals.iloc[0]

        # Fallback: any non-NaN Number MB in this group/electrode
        vals_any = subdf["Number MB"].dropna()
        return vals_any.iloc[0] if not vals_any.empty else np.nan

    def pick_au_cm2(subdf):
        """
        Choose the best 'Au cm2' for a (Group, Electrode) block.

        If the column doesn't exist (e.g. hydrogel-only CVs), return NaN.
        Prefer:
          1) 'EASA After Roughening'
          2) 'EASA Before Roughening'
          3) any non-NaN value if present
        """
        if "Au cm2" not in subdf.columns:
            return np.nan

        for tag in ("EASA After Roughening", "EASA Before Roughening"):
            mask = subdf["Data Type"] == tag
            if not mask.any():
                continue
            vals = subdf.loc[mask, "Au cm2"].dropna()
            if not vals.empty:
                return vals.iloc[0]

        vals_any = subdf["Au cm2"].dropna()
        return vals_any.iloc[0] if not vals_any.empty else np.nan

    total_groups = len(group_data)
    all_results = []
    structured_data = {}

    cv_data_rows = []
    cv_lookup: dict = {}  # (Group, Electrode) -> {'Au cm2', 'Number MB', 'Packing Density (MB/cm²)'}
    for group_raw, details in group_data.items():
        group = str(group_raw)
        cv_files = details.get("cv_files", {})
        print(cv_files)
        for folder, files in cv_files.items():
            cv_meta   = details.get("cv", {}).get(folder, {})
            data_type = cv_meta.get("data_type", "")
            for fname in files:
                filepath = os.path.join(folder, fname)
                df_cv = read_cv_text_file(filepath)
                if df_cv.empty or "Potential" not in df_cv.columns or "Current" not in df_cv.columns:
                    continue
                scanrate = extract_cv_scanrate(fname)
                if data_type in EASA_types:
                    metrics = analyze_cv_peak_multi_cycle(df_cv, scanrate)
                else:
                    metrics = analyze_cv_initial(df_cv, scanrate)
                if not metrics:
                    continue
                elec = extract_cv_electrode(fname)
                run  = extract_cv_run(fname)
                ts   = extract_timestamp(filepath)
                cv_data_rows.append({
                    "Group": group,
                    "Electrode": elec,
                    "Scanrate": scanrate,
                    "Run": run,
                    "Timestamp": ts,
                    "Data Type": data_type,
                    **metrics,
                })

    # Always create a CV CSV if an output directory is provided so that
    # downstream code (watchers, normalization look-ups) can rely on its presence,
    # even in cases where only EASA or only initial CVs were supplied.
    if output_dir:
        out_cv_path = os.path.join(output_dir, "NDL_CV_Data.csv")

        if cv_data_rows:
            df_cv_out = pd.DataFrame(cv_data_rows)
            df_cv_out = df_cv_out.sort_values(by=["Group", "Electrode", "Run"], ignore_index=True)
            # — Prioritize hydrogel CVs for Number MB —
            # — Build a small DataFrame of “best” MB and Au for each electrode —
            grouped = df_cv_out.groupby(["Group", "Electrode"], group_keys=False)
            df_pref = (
                grouped
                .apply(lambda g: pd.Series({
                    "Number MB (best)": pick_number_mb(g),
                    "Au cm2 (best)"   : pick_au_cm2(g),
                }))
                .reset_index()
            )

            # compute packing density
            df_pref["Packing Density (MB/cm²)"] = (
                df_pref["Number MB (best)"] /
                df_pref["Au cm2 (best)"].replace(0, np.nan)
            ).round(3)

            df_pref_lookup = df_pref.set_index(["Group", "Electrode"]).to_dict("index")

            cv_lookup = {}
            for key, row in df_pref_lookup.items():
                grp, elec = key
                cv_lookup[(grp, elec)] = {
                    "Au cm2": row.get("Au cm2 (best)", np.nan),
                    "Number MB": row.get("Number MB (best)", np.nan),
                    "Packing Density (MB/cm²)": row.get("Packing Density (MB/cm²)", np.nan),
                }

            # merge back onto every CV row so that the exported CSV also includes packing density
            df_cv_out = df_cv_out.merge(
                df_pref[["Group", "Electrode", "Packing Density (MB/cm²)"]],
                on=["Group", "Electrode"],
                how="left",
            )

            # Normalize timestamp format
            df_cv_out["Timestamp"] = (
                pd.to_datetime(df_cv_out["Timestamp"], errors='coerce')
                  .dt.strftime('%Y%m%d %H:%M:%S')
                  .fillna('')
            )
        else:
            # No valid CV metrics were extracted (e.g., the data did not meet
            # peak-finding criteria), but callers still expect the CSV file to exist.
            # Create an empty table with the columns that load_cv_lookup relies on.
            base_columns = [
                "Group",
                "Electrode",
                "Scanrate",
                "Run",
                "Timestamp",
                "Data Type",
                "Peak_Current",
                "Peak_Height",
                "AUC",
                "Q_Au",
                "Au cm2",
                "Q_MB",
                "Number MB",
                "Packing Density (MB/cm²)",
            ]
            df_cv_out = pd.DataFrame(columns=base_columns)

        # At this point df_cv_out is defined (possibly empty). Write/overwrite the CSV.
        if os.path.exists(out_cv_path):
            os.remove(out_cv_path)  # Remove stale file so schema changes don't linger
        df_cv_out.to_csv(out_cv_path, index=False, encoding="utf-8-sig")
        print(f"Saved CV analysis to: {out_cv_path}")

    reference_peaks = {}

    for i, (group, details) in enumerate(group_data.items()):
        progress.setLabelText(f"Processing group: {group}")
        progress.setValue(int((i / total_groups) * 100))
        QApplication.processEvents()
        if progress.wasCanceled():
            break

        group_result = {}
        swv_files = details.get("swv_files", {})
        run_maps = {folder: compute_run_numbers(files) for folder, files in swv_files.items()}
        for folder, files in swv_files.items():
            run_map = run_maps[folder]
            ref_candidates = select_reference_candidates(files, run_map, norm_point)
            for (elec, freq), candidate_files in ref_candidates.items():
                for fname in candidate_files:
                    filepath = os.path.join(folder, fname)
                    df = read_swv_text_file(filepath)
                    if df.empty:
                        continue
                    diff_array = df['Diff'].to_numpy()
                    y_proc = fourier_smooth(diff_array, keep_frac) if use_smoothing else diff_array
                    if not use_smoothing:
                        # allow tiny float noise from earlier ops—if any: atol can be 0
                        if not np.allclose(y_proc, diff_array, atol=0, rtol=0):
                            print("[CRITICAL] Smoothing occurred despite use_smoothing=False")

                    potential_array = df["Potential"].to_numpy()
                    res = find_peak_and_baseline_dual(potential_array, y_proc, min_distance=10)
                    if not res:
                        # No real peak in this scan (e.g. sensor still
                        # equilibrating) -- try the next candidate rather
                        # than dropping this electrode/frequency entirely.
                        continue
                    peak_idx        = res["peak_idx"]
                    peak_current    = res["peak_current"]
                    peak_potential  = res["peak_potential"]
                    slope           = res["slope"]
                    intercept       = res["intercept"]
                    baseline_current = slope * peak_potential + intercept
                    peak_minus_baseline_ref = peak_current - baseline_current
                    reference_peaks[(elec, freq)] = peak_minus_baseline_ref
                    break

        for folder, files in swv_files.items():
            run_map = run_maps[folder]
            for fname in files:
                elec = extract_electrode(fname)
                freq = extract_frequency(fname)
                run = run_map.get(fname)
                ref_key = (elec, freq)
                if ref_key not in reference_peaks:
                    continue
                filepath = os.path.join(folder, fname)
                # Grab Timestamp Line
                ts_string = extract_timestamp(filepath)
                df = read_swv_text_file(filepath)
                if df.empty:
                    continue
                diff_array = df['Diff'].to_numpy()
                potential_array = df['Potential'].to_numpy()
                y_proc = fourier_smooth(diff_array, keep_frac) if use_smoothing else diff_array
                if not use_smoothing:
                    # allow tiny float noise from earlier ops—if any: atol can be 0
                    if not np.allclose(y_proc, diff_array, atol=0, rtol=0):
                        print("[CRITICAL] Smoothing occurred despite use_smoothing=False")

                res = find_peak_and_baseline_dual(potential_array, y_proc, min_distance=10)
                if not res:
                    continue
                peak_idx        = res["peak_idx"]
                peak_current    = res["peak_current"]
                peak_potential  = res["peak_potential"]
                slope           = res["slope"]
                intercept       = res["intercept"]
                baseline_current   = slope * peak_potential + intercept
                peak_minus_baseline = peak_current - baseline_current
                ref_peak_minus_baseline = reference_peaks[ref_key]
                signal_change = safe_signal_change(peak_minus_baseline, ref_peak_minus_baseline)
                if np.isnan(signal_change):
                    logger.warning(
                        "Signal change is NaN because reference peak_minus_baseline is ~0 "
                        f"(ref={ref_peak_minus_baseline:.3e}). group={group} elec={elec} freq={freq}Hz file={filepath}"
                    )

                baseline_y = slope * potential_array + intercept
                auc_raw = float(trapz(y_proc, potential_array))
                auc_bline = float(trapz(baseline_y, potential_array))
                auc_combine = auc_raw - auc_bline

                curr_corr = y_proc - baseline_y
                widths, height, left_ips, right_ips = peak_widths(curr_corr, [peak_idx], rel_height=0.5)
                ix = np.arange(len(potential_array))
                left_volt  = float(np.interp(left_ips[0],  ix, potential_array))
                right_volt = float(np.interp(right_ips[0], ix, potential_array))
                fwhm = abs(right_volt - left_volt)

                lowest_pot = potential_array.min()
                target_pot = lowest_pot * 0.9
                iO2 = float(np.interp(target_pot, potential_array, y_proc))

                # Find corresponding normalization values for this electrode
                au_cm2 = None
                num_mb = None
                packing_dens = None

                # Look up in CV summary (previously merged into df_cv_out)
                try:
                    norm_vals = cv_lookup.get((group, elec), {})
                    au_cm2 = norm_vals.get("Au cm2", np.nan)
                    num_mb = norm_vals.get("Number MB", np.nan)
                    packing_dens = norm_vals.get("Packing Density (MB/cm²)", np.nan)
                except Exception:
                    pass

                # Compute normalized values
                def safe_div(val, denom):
                    return round(val / denom, 25) if denom and not pd.isna(denom) and denom != 0 else np.nan

                peak_current_cm2 = safe_div(peak_current, au_cm2)
                peak_current_mb = safe_div(peak_current, num_mb)
                peak_current_pd = safe_div(peak_current, packing_dens)
                peak_height_cm2 = safe_div(peak_minus_baseline, au_cm2)
                peak_height_mb = safe_div(peak_minus_baseline, num_mb)
                peak_height_pd = safe_div(peak_minus_baseline, packing_dens)
                signal_change_cm2 = safe_div(signal_change, au_cm2)
                signal_change_mb = safe_div(signal_change, num_mb)
                signal_change_pd = safe_div(signal_change, packing_dens)
                auc_cm2 = safe_div(auc_combine, au_cm2)
                auc_mb = safe_div(auc_combine, num_mb)
                auc_pd = safe_div(auc_combine, packing_dens)

                group_result.setdefault((elec, freq), []).append(signal_change)
                all_results.append({
                    "Group": group,
                    "Electrode": elec,
                    "Frequency (Hz)": freq,
                    "Run Number": run,
                    "Timestamp": ts_string,
                    "Peak Current (A)": round(peak_current, 12),
                    "Peak Position (V)": round(peak_potential, 6),
                    "Baseline Current (A)": round(baseline_current, 12),
                    "Peak - Baseline (A)": round(peak_minus_baseline, 12),
                    "Signal Change (%)": round(signal_change, 3),
                    "AUC (A·V)": round(auc_raw, 12),
                    "AUC Normalized (A·V)": round(auc_combine, 12),
                    "Peak Current Norm (A/cm²)": f"{peak_current_cm2: .3e}",
                    "Peak Current Norm (A/#Apt)": f"{peak_current_mb: .3e}",
                    "Peak Current Norm (A/PD)": f"{peak_current_pd: .3e}",
                    "Peak Height Norm (A/cm2)": f"{peak_height_cm2: .3e}",
                    "Peak Height Norm (A/#Apt)": f"{peak_height_mb: .3e}",
                    "Peak Height Norm (A/PD)": f"{peak_height_pd: .3e}",
                    "Signal Change Norm (%/cm2)": f"{signal_change_cm2: .3e}",
                    "Signal Change Norm (%/#Apt)": f"{signal_change_mb: .3e}",
                    "Signal Change Norm (%/PD)": f"{signal_change_pd: .3e}",
                    "AUC Norm (A·V/cm2)": f"{auc_cm2: .3e}",
                    "AUC Norm (A·V/#Apt)": f"{auc_mb: .3e}",
                    "AUC Norm(A·V/PD)": f"{auc_pd: .3e}",
                    "FWHM (V)": round(fwhm, 12),
                    "iO2 (A)": round(iO2, 12),
                    "File Name": fname,
                    "Folder Path": folder
                })

        structured_data[group] = {
            "graph_data": all_results,  # this should be your plotting data structure
            "meta": {
                "norm_point": norm_point,
                "num_files": sum(len(flist) for flist in swv_files.values())
            }
        }

    if output_dir:

        df = pd.DataFrame(all_results)
        df = df.sort_values(
            by=["Group", "Electrode", "Frequency (Hz)", "Run Number"],
            ignore_index=True
        )
        df['Timestamp_dt'] = pd.to_datetime(df['Timestamp'], errors='coerce')
        df['dt_seconds'] = (df['Timestamp_dt'] - df.groupby(['Electrode', 'Frequency (Hz)'])['Timestamp_dt'].transform('min')
        ).dt.total_seconds()
        df['dt_hours'] = df['dt_seconds'] / (60*60)
        df['Timestamp'] = (
            pd.to_datetime(df['Timestamp'], errors='coerce')       # parse into Timestamp or NaT
              .dt.strftime('%Y%m%d %H:%M:%S')                                # format as YYYYMMDD
              .fillna('')                                           # replace NaT → blank
        )
        df = df.drop(columns=['Timestamp_dt'])
        if df.empty:
            print("Warning: No data to write. Check if valid peaks and normalization files were found.")
        else:
            out_path = os.path.join(output_dir, "NDL_Data.csv")
            df.to_csv(out_path, index=False, encoding="utf-8-sig")
            print(f"Saved analyzed data to: {out_path}")
            df_avg = (
                df.groupby(["Group", "Frequency (Hz)", "Run Number"])["Signal Change (%)"]
                  .agg(
                      **{
                          "Mean Signal Change (%)": "mean",
                          "SD Signal Change (%)": (lambda x: float(np.std(x, ddof=1)) if len(x) > 1 else 0.0),
                      }
                  )
                  .reset_index()
            )
            # how many electrodes contributed to each mean
            df_n = (
                df.groupby(["Group", "Frequency (Hz)", "Run Number"])["Signal Change (%)"]
                  .size()
                  .reset_index(name="N Electrodes")
            )
            df_avg = (
                df_avg.merge(df_n, on=["Group", "Frequency (Hz)", "Run Number"])
                      .loc[:, ["Group", "Frequency (Hz)", "Run Number",
                               "N Electrodes", "Mean Signal Change (%)",
                               "SD Signal Change (%)"]]
                      .sort_values(["Group", "Frequency (Hz)", "Run Number"], ignore_index=True)
            )
            out_avg_path = os.path.join(output_dir, "NDL_Averages.csv")
            df_avg.to_csv(out_avg_path, index=False, encoding="utf-8-sig")
            print(f"Saved averages to: {out_avg_path}")



    progress.setValue(100)
    return structured_data

def calculate_concentration_from_signal(signal, fit_results):
    """
    Inverse mathematics: Calculates X (Concentration) given Y (Signal).
    Returns np.nan if the signal falls outside the mathematically possible bounds of the curve.
    """
    import numpy as np
    model = fit_results.get("model_type")

    try:
        if model == "Linear":
            m, b = fit_results["m"], fit_results["b"]
            return (signal - b) / m

        elif model == "Langmuir (1:1)":
            Bmax, Kd = fit_results["Bmax"], fit_results["Kd"]
            # If signal exceeds Bmax, concentration is theoretically infinite
            if signal >= Bmax: return np.nan
            return (signal * Kd) / (Bmax - signal)

        elif model == "Hill Equation":
            Bmax, Kd, n = fit_results["Bmax"], fit_results["Kd"], fit_results["n"]
            if signal >= Bmax or signal <= 0: return np.nan
            return Kd * np.power(signal / (Bmax - signal), 1.0 / n)

        elif model == "4-Parameter Logistic (4PL)":
            a, b, c, d = fit_results["a"], fit_results["b"], fit_results["c"], fit_results["d"]
            # To prevent math domain errors with fractional exponents and negatives:
            ratio = (a - d) / (signal - d)
            if ratio <= 1.0: return np.nan
            return c * np.power(ratio - 1.0, 1.0 / b)

    except Exception:
        return np.nan

    return np.nan

class CalibrationFitter:
    """
    Handles mathematical curve fitting for calibration.
    """
    def __init__(self, x_data, y_data, x_scale="Linear"):
        # Convert to numpy arrays to ensure the math functions work smoothly
        self.x = np.asarray(x_data, dtype=float)
        self.y = np.asarray(y_data, dtype=float)
        self.x_scale = x_scale

    def _prepare_fit_data(self, base_equation):
        """
        Wraps the equation and transforms the data if a Logarithmic fit is requested.
        This prevents clustering at low concentrations from biasing the fit.
        """
        if self.x_scale == "Logarithmic":
            # 1. Filter out 0 or negative concentrations (can't take log10 of 0!)
            valid_idx = self.x > 0
            x_fit = np.log10(self.x[valid_idx])
            y_fit = self.y[valid_idx]

            # 2. Wrap the equation so the optimizer sees log(X), but the math uses linear(X)
            def fit_wrapper(x_log, *args):
                x_lin = np.power(10.0, x_log)
                return base_equation(x_lin, *args)

            return x_fit, y_fit, fit_wrapper
        else:
            return self.x, self.y, base_equation

    def _calculate_r_squared(self, y_predicted):
        """Helper method to calculate the R^2 value for any fit."""
        ss_res = np.sum((self.y - y_predicted) ** 2)
        ss_tot = np.sum((self.y - np.mean(self.y)) ** 2)

        # Prevent division by zero if all y-values are identical
        if ss_tot == 0:
            return 0.0

        return 1 - (ss_res / ss_tot)

    def perform_fit(self, model_type, user_guesses):
        """
        Routes the data to the correct mathematical model based on the UI selection.
        """
        if len(self.x) < 2:
            return {"success": False, "error": "Not enough data points to fit a curve (minimum 2)."}

        if model_type == "Linear":
            return self._fit_linear(user_guesses)
        elif model_type == "Langmuir (1:1)":
            return self._fit_langmuir(user_guesses)
        elif model_type == "Hill Equation":
            return self._fit_hill(user_guesses)
        elif model_type == "4-Parameter Logistic (4PL)":
            return self._fit_4pl(user_guesses)
        else:
            return {"success": False, "error": f"Model '{model_type}' is not yet implemented."}

    # ==========================================
    # MATHEMATICAL MODELS
    # ==========================================

    @staticmethod
    def _linear_equation(x, m, b):
        return m * x + b

    def _fit_linear(self, user_guesses):
        """
        Fits data to y = mx + b.
        user_guesses: dict e.g., {'Slope (m)': None, 'Y-Intercept (b)': 0}
        """
        try:
            # 1. Automate initial guesses (Heuristics)
            # A good guess for slope is just the rise over run between the first and last points
            auto_m = (self.y[-1] - self.y[0]) / (self.x[-1] - self.x[0]) if (self.x[-1] - self.x[0]) != 0 else 1.0
            auto_b = self.y[0] - auto_m * self.x[0]

            # 2. Check if the user provided overrides
            final_m = user_guesses.get("Slope (m)")
            if final_m is None:
                final_m = auto_m

            final_b = user_guesses.get("Y-Intercept (b)")
            if final_b is None:
                final_b = auto_b

            initial_guesses = [final_m, final_b]

            # 3. Perform the Curve Fit
            popt, pcov = curve_fit(self._linear_equation, self.x, self.y, p0=initial_guesses)

            # popt[0] is m, popt[1] is b
            m_fit, b_fit = popt[0], popt[1]

            # 4. Calculate R^2
            y_pred = self._linear_equation(self.x, m_fit, b_fit)
            r_squared = self._calculate_r_squared(y_pred)

            # 5. Return the packaged results for the UI
            return {
                "success": True,
                "model_type": "Linear",
                "m": m_fit,
                "b": b_fit,
                "r_squared": r_squared
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Linear fit failed: {str(e)}"
            }

    @staticmethod
    def _langmuir_equation(x, Bmax, Kd):
        return (Bmax * x) / (Kd + x)

    def _fit_langmuir(self, user_guesses):
        """ Fits data to the Langmuir 1:1 binding isotherm. """
        try:
            # 1. Automate initial guesses (Heuristics)
            # Max signal is a great guess for Bmax
            auto_Bmax = np.max(self.y)

            # Find the X concentration where Y is closest to 50% of Bmax
            half_y = auto_Bmax / 2.0
            idx_closest_to_half = np.argmin(np.abs(self.y - half_y))
            auto_Kd = self.x[idx_closest_to_half]

            # Prevent an auto-guess of 0 or negative for Kd
            if auto_Kd <= 0:
                auto_Kd = 1e-6

            # 2. Apply user overrides if provided
            final_Bmax = user_guesses.get("Bmax")
            if final_Bmax is None:
                final_Bmax = auto_Bmax

            final_Kd = user_guesses.get("Kd")
            if final_Kd is None:
                final_Kd = auto_Kd

            initial_guesses = [final_Bmax, final_Kd]

            # --- Prepare the data based on the chosen scale ---
            x_fit, y_fit, fit_func = self._prepare_fit_data(self._langmuir_equation)

            # --- Pass x_fit, y_fit, and fit_func to the optimizer ---
            popt, pcov = curve_fit(
                fit_func,
                x_fit,
                y_fit,
                p0=initial_guesses,
                bounds=(0, np.inf)
            )

            Bmax_fit, Kd_fit = popt[0], popt[1]

            # 4. Calculate R^2
            y_pred = self._langmuir_equation(self.x, Bmax_fit, Kd_fit)
            r_squared = self._calculate_r_squared(y_pred)

            # 5. Return the packaged results
            return {
                "success": True,
                "model_type": "Langmuir (1:1)",
                "Bmax": Bmax_fit,
                "Kd": Kd_fit,
                "r_squared": r_squared
            }

        except Exception as e:
            return {"success": False, "error": f"Langmuir fit failed: {str(e)}"}

    @staticmethod
    def _hill_equation(x, Bmax, Kd, n):
        # We use np.power to safely handle array exponentiation
        # Adding a tiny epsilon to the denominator prevents divide-by-zero errors
        return (Bmax * np.power(x, n)) / (np.power(Kd, n) + np.power(x, n) + 1e-12)

    def _fit_hill(self, user_guesses):
        """ Fits data to the Hill equation (cooperative binding). """
        try:
            # 1. Automate initial guesses
            auto_Bmax = np.max(self.y)

            # Find the X concentration where Y is closest to 50% of Bmax
            half_y = auto_Bmax / 2.0
            idx_closest_to_half = np.argmin(np.abs(self.y - half_y))
            auto_Kd = self.x[idx_closest_to_half]

            # Prevent an auto-guess of 0 for Kd
            if auto_Kd <= 0:
                auto_Kd = 1e-6

            auto_n = 1.0 # Default to Langmuir-like behavior (n=1) as a safe starting point

            # 2. Apply user overrides if provided
            final_Bmax = user_guesses.get("Bmax")
            if final_Bmax is None:
                final_Bmax = auto_Bmax

            final_Kd = user_guesses.get("Kd")
            if final_Kd is None:
                final_Kd = auto_Kd

            final_n = user_guesses.get("Hill Coefficient (n)")
            if final_n is None:
                final_n = auto_n

            initial_guesses = [final_Bmax, final_Kd, final_n]

            # --- Prepare the data based on the chosen scale ---
            x_fit, y_fit, fit_func = self._prepare_fit_data(self._hill_equation)

            # --- Pass x_fit, y_fit, and fit_func to the optimizer ---
            popt, pcov = curve_fit(
                fit_func,
                x_fit,
                y_fit,
                p0=initial_guesses,
                bounds=([0, 0, 0], [np.inf, np.inf, 10.0])
            )

            Bmax_fit, Kd_fit, n_fit = popt[0], popt[1], popt[2]

            # 4. Calculate R^2
            y_pred = self._hill_equation(self.x, Bmax_fit, Kd_fit, n_fit)
            r_squared = self._calculate_r_squared(y_pred)

            # 5. Return the packaged results
            return {
                "success": True,
                "model_type": "Hill Equation",
                "Bmax": Bmax_fit,
                "Kd": Kd_fit,
                "n": n_fit,
                "r_squared": r_squared
            }

        except Exception as e:
            return {"success": False, "error": f"Hill fit failed: {str(e)}"}

    @staticmethod
    def _4pl_equation(x, a, b, c, d):
        # a = Min Asymptote
        # b = Hill Slope
        # c = Inflection Point (EC50)
        # d = Max Asymptote
        # We add 1e-12 to x and c to prevent divide-by-zero errors if a concentration is exactly 0
        return d + (a - d) / (1.0 + np.power((x + 1e-12) / (c + 1e-12), b))

    def _fit_4pl(self, user_guesses):
            """ Fits data to the 4-Parameter Logistic (sigmoidal) equation, allowing for locked parameters. """
            try:
                # 1. Automate initial guesses
                auto_a = np.min(self.y)
                auto_d = np.max(self.y)

                half_y = (auto_a + auto_d) / 2.0
                idx_closest_to_half = np.argmin(np.abs(self.y - half_y))
                auto_c = self.x[idx_closest_to_half]

                if auto_c <= 0:
                    auto_c = 1e-6

                auto_b = 1.0 # Default positive slope

                # --- THE NEW BOUNDS LOGIC ---
                # Default bounds: [a, b, c, d]
                # 'c' (EC50) is forced to be > 0. The rest can float anywhere initially.
                lower_bounds = [-np.inf, -np.inf, 1e-10, -np.inf]
                upper_bounds = [np.inf, np.inf, np.inf, np.inf]

                # 2. Apply user overrides and LOCK them using tight bounds

                # Parameter A (Min Asymptote)
                user_a = user_guesses.get("Min Asymptote (a)")
                if user_a is not None:
                    final_a = user_a
                    # Lock 'a' by giving it a microscopic window to move
                    lower_bounds[0] = final_a - 1e-8
                    upper_bounds[0] = final_a + 1e-8
                else:
                    final_a = auto_a

                # Parameter B (Hill Slope)
                user_b = user_guesses.get("Hill Slope (b)")
                if user_b is not None:
                    final_b = user_b
                    lower_bounds[1] = final_b - 1e-8
                    upper_bounds[1] = final_b + 1e-8
                else:
                    final_b = auto_b

                # Parameter C (Inflection Point)
                user_c = user_guesses.get("Inflection Point (c)")
                if user_c is not None:
                    final_c = user_c
                    lower_bounds[2] = final_c - 1e-8
                    upper_bounds[2] = final_c + 1e-8
                else:
                    final_c = auto_c

                # Parameter D (Max Asymptote)
                user_d = user_guesses.get("Max Asymptote (d)")
                if user_d is not None:
                    final_d = user_d
                    lower_bounds[3] = final_d - 1e-8
                    upper_bounds[3] = final_d + 1e-8
                else:
                    final_d = auto_d

                initial_guesses = [final_a, final_b, final_c, final_d]

                # --- Prepare the data based on the chosen scale ---
                x_fit, y_fit, fit_func = self._prepare_fit_data(self._4pl_equation)

                # --- Pass x_fit, y_fit, and fit_func to the optimizer ---
                popt, pcov = curve_fit(
                    fit_func,
                    x_fit,
                    y_fit,
                    p0=initial_guesses,
                    bounds=(lower_bounds, upper_bounds)
                )

                a_fit, b_fit, c_fit, d_fit = popt[0], popt[1], popt[2], popt[3]

                # 4. Calculate R^2
                y_pred = self._4pl_equation(self.x, a_fit, b_fit, c_fit, d_fit)
                r_squared = self._calculate_r_squared(y_pred)

                # 5. Return the packaged results
                return {
                    "success": True,
                    "model_type": "4-Parameter Logistic (4PL)",
                    "a": a_fit,
                    "b": b_fit,
                    "c": c_fit,
                    "d": d_fit,
                    "r_squared": r_squared
                }

            except Exception as e:
                return {"success": False, "error": f"4PL fit failed: {str(e)}"}
