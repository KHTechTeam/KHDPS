# NDL-Data-Processing-Software
A fully integrated Data Processing Program for Electrochemical Aptamer Sensors.

## Setup (run from source)

```
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r "Resource Files\requirements.txt"
python "Python Files\main.py"
```

Logs are written to `logs\app_debug.log` (overwritten on each launch) —
check there first if something isn't working.

## Building the .exe

From the project root (same level as `Python Files` and `Resource Files`):

```
pip install pyinstaller
python -m PyInstaller "Python Files\main.py" --name "KHDPS" --windowed --onefile --icon "Resource Files\khdps_icon.ico" --paths "Resource Files" --add-data "Resource Files;Resource Files" --hidden-import=matplotlib.backends.backend_pdf
```

(Using `python -m PyInstaller` instead of the bare `pyinstaller` command avoids
PATH issues right after a fresh `pip install`.)

Note the two flags that matter here beyond the basics: `--paths "Resource
Files"` lets PyInstaller's build-time analysis find and bundle `resources.py`
(it lives in a different folder than `main.py`, so a plain build can't find
it without this), and `--add-data "Resource Files;Resource Files"` bundles
the icon/logo files themselves, since the app loads those by file path.

The built app will be in `dist\KHDPS.exe`.

## Recent changes

Fixes for reading and analyzing data from three different file-naming
conventions that can show up in a data folder:

- Single-channel potentiostat: `01-5Hz-Low_1.txt`
- Multi-channel potentiostat: `01-20Hz-Low-E1-_3.txt`
- Internal FC board ("SunVida"): `0001-120Hz-2ad60366-s1-E2-20260707_165119.txt`

1. **Electrode filename matching bug** (pre-existing, affected single-channel
   CHI files): the file-to-electrode matching used to use `\b` word
   boundaries, which don't treat `_` as a boundary in Python's `re` module.
   This silently excluded every file where the electrode label is
   immediately followed by an underscore (e.g. `Low_1.txt`), so
   single-channel folders would produce zero results. Fixed to use an
   alphanumeric-boundary check instead.

2. **FC-board run/cycle numbering**: FC-board filenames don't encode a scan
   number the way potentiostat files do (`..._3.txt`). A "run" for these
   files is now resolved as one full cycle through the device's configured
   frequency sweep, detected by the filename's segment marker (`s1`/`s2`/
   `s3`...) resetting back down — *not* by timing, since automatic scan
   intervals vary, manual scans can happen in between, and device
   disconnects can create large time gaps that don't represent a real cycle
   break. The resolved run number is shared across every electrode/
   frequency scanned within that cycle. Single/multi-channel potentiostat
   files are unaffected — they keep using their existing embedded run
   number.

3. **Per-frequency reference/baseline selection**: a frequency can be added
   to an FC-board monitoring session partway through (e.g. a third
   frequency introduced starting at cycle 38), so requiring an exact match
   to the normalization point would silently drop that frequency's data
   entirely. The 0% baseline reference for FC-board files is now whichever
   cycle a given electrode/frequency combo was *first* scanned in, rather
   than requiring cycle == normalization point exactly. Potentiostat files
   keep the original exact-match behavior, since their normalization point
   is a deliberate, user-set experimental baseline.

4. **Thread-safety on the live reference selection**: the live folder-
   watcher path processes new files on a thread pool, so file-processing
   order isn't guaranteed to match chronological order. Reference-peak
   selection is now guarded by a lock and compared by run number rather
   than by whichever task happens to finish first.

**Known open item:** if a single folder/group ever contains data from more
than one physical FC-board device that happen to share the same electrode
label, reference selection doesn't currently keep them separate (it wasn't
observed in testing, since normal sessions are one device per folder). Flag
it if this comes up and the reference-selection key can be extended to
include the device ID.
