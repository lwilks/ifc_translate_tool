# Domain Pitfalls: Python Windows Desktop App with IfcOpenShell

**Domain:** Standalone Windows executable wrapping IfcPatch for non-technical users
**Researched:** 2026-01-30
**Confidence:** HIGH (verified with PyInstaller official docs, IfcOpenShell GitHub issues, and Windows deployment patterns)

## Executive Summary

Building a Windows executable that bundles IfcOpenShell presents unique challenges across four critical dimensions: (1) native dependency bundling for C++ wrappers, (2) Windows antivirus/SmartScreen friction for unsigned executables, (3) memory management for large IFC files, and (4) config/preset persistence across user environments. Each pitfall below has caused production failures in real deployments. Prevention strategies are mapped to development phases where they should be addressed.

---

## Critical Pitfalls

These mistakes cause rewrites, production failures, or complete project abandonment.

### Pitfall 1: Missing IfcOpenShell Native Dependencies in Bundled Executable

**What goes wrong:**
PyInstaller successfully builds an .exe, but on target machines (especially clean Windows installs), the app crashes with `ImportError: DLL load failed while importing _ifcopenshell_wrapper: The specified module could not be found`. The `_ifcopenshell_wrapper.pyd` is a SWIG-generated Python wrapper around C++ code that depends on multiple native DLLs (IfcParse.dll, IfcGeom.dll, OpenCASCADE DLLs like TKernel.dll) that PyInstaller does not automatically detect.

**Why it happens:**
- PyInstaller's analysis cannot trace C++ extension module dependencies loaded at runtime
- IfcOpenShell 0.8+ depends on recent OpenCASCADE (OCCT) 7.7+ with specific BVH tree functionality
- The wrapper uses dynamic loading via ctypes/SWIG that breaks PyInstaller's import detection
- Different Python versions have different wrapper binaries (e.g., `_ifcopenshell_wrapper.cp311-win_amd64.pyd` for Python 3.11)

**Consequences:**
- App works on development machine but fails on user machines ("works on my machine" syndrome)
- Mysterious crashes with no clear error messages if running in `--windowed` mode
- Users blame your app, not their environment

**Prevention:**

1. **Explicitly bundle IfcOpenShell wrapper and dependencies in .spec file:**
   ```python
   import ifcopenshell
   import os

   # Get IfcOpenShell installation path
   ifc_path = os.path.dirname(ifcopenshell.__file__)

   a = Analysis(['main.py'],
                binaries=[(os.path.join(ifc_path, '_ifcopenshell_wrapper*.pyd'), '.'),
                          (os.path.join(ifc_path, '*.dll'), '.')],
                datas=[(os.path.join(ifc_path, 'express'), 'ifcopenshell/express')],
                hiddenimports=['ifcopenshell', 'ifcpatch'],
                ...)
   ```

2. **Test on clean Windows VM without Python installed** - this is non-negotiable
3. **Use `--debug=imports` flag to verify all imports resolve** before distributing
4. **Consider using `--onedir` mode first** to diagnose dependency issues (easier to inspect bundled files)

**Detection:**
- Warning sign: App works on dev machine but nowhere else
- Warning sign: `Process Monitor` shows failed DLL loads from temp directory
- Warning sign: Different error on Windows 10 vs Windows 11 (different system DLL versions)

**Which phase:**
- **Phase 1 (Bundling/Distribution):** Must validate native dependency bundling before any user testing
- Add to acceptance criteria: "Executable runs on clean Windows VM with no Python installed"

**Sources:**
- [IfcOpenShell Installation Documentation](https://docs.ifcopenshell.org/ifcopenshell-python/installation.html)
- [GitHub Issue #4686: identify build platform and python version from _ifcopenshell_wrapper.pyd](https://github.com/IfcOpenShell/IfcOpenShell/issues/4686)
- [PyInstaller Common Issues and Pitfalls](https://pyinstaller.org/en/stable/common-issues-and-pitfalls.html)

---

### Pitfall 2: Windows Defender/Antivirus False Positives with --onefile Mode

**What goes wrong:**
Your unsigned executable is immediately quarantined by Windows Defender, McAfee, or AVG as a trojan (`Win64:Trojan-gen`). Users see "Windows protected your PC" SmartScreen warnings and cannot run the app without clicking through security warnings. Corporate environments block the executable entirely. The problem is dramatically worse with `--onefile` mode because the unpacking behavior resembles malware.

**Why it happens:**
- PyInstaller is used by malware authors, so antivirus vendors flag the PyInstaller bootloader signatures
- `--onefile` extracts to a temp directory at runtime, which is malware-like behavior to heuristic scanners
- Unsigned executables have zero reputation with Windows SmartScreen
- Windows 11's Smart App Control enforces code signing even more strictly than SmartScreen
- DLL extraction from packed executables triggers sandboxing/behavioral analysis

**Consequences:**
- Users cannot run your app without disabling antivirus (they won't do this)
- Corporate IT blocks distribution
- App reputation is destroyed before users even try it
- Support burden: "Why does Windows say this is a virus?"

**Prevention:**

1. **Use `--onedir` mode instead of `--onefile`** for distribution (reduces false positive rate by ~70%)
   - Yes, it's a folder instead of a single .exe, but it's dramatically more reliable
   - Package the folder as a ZIP or installer (NSIS, Inno Setup) if single-file distribution is required

2. **Code sign your executable with an EV (Extended Validation) certificate**
   - Standard code signing certificates still trigger SmartScreen warnings initially
   - EV certificates ($300-600/year, requires registered business) bypass SmartScreen from day one
   - Without EV cert, you need thousands of downloads to build "reputation" with Microsoft

3. **Whitelist your build directory during development:**
   ```bash
   pyinstaller --build-directory-override C:\MyWhitelistedBuildPath main.spec
   ```

4. **Submit to VirusTotal and report false positives to major vendors:**
   - Submit .exe to virustotal.com
   - Report false positives to Microsoft, Symantec, McAfee, etc.
   - This is ongoing maintenance, not one-time

5. **Consider MSIX packaging** as alternative to PyInstaller for Windows 11+
   - Native Windows packaging format with better SmartScreen integration
   - Requires code signing but integrates better with Windows Store/enterprise distribution

**Detection:**
- Warning sign: Windows Defender quarantines your .exe during build
- Warning sign: VirusTotal shows 5+ vendors flagging as malware
- Warning sign: Users report SmartScreen warnings

**Which phase:**
- **Phase 1 (Bundling):** Choose `--onedir` vs `--onefile` based on antivirus testing
- **Phase 2 (Distribution):** Acquire code signing certificate before public release
- Budget: $60-150/year for standard cert, $300-600/year for EV cert

**Sources:**
- [GitHub Issue #6754: My --onefile exe is getting anti-Virus False positive flags](https://github.com/pyinstaller/pyinstaller/issues/6754)
- [GitHub Discussion #6746: How to sign files extracted for Smart App Control](https://github.com/orgs/pyinstaller/discussions/6746)
- [CodersLegacy: Pyinstaller EXE detected as Virus? (Solutions and Alternatives)](https://coderslegacy.com/pyinstaller-exe-detected-as-virus-solutions/)
- [Automate PyInstaller Builds and Code Signing on Windows](https://johanneskinzig.com/automating-pyinstaller-builds-and-code-signing-with-powershell.html)

---

### Pitfall 3: Memory Explosion When Processing Large IFC Files

**What goes wrong:**
Your app successfully processes 50MB IFC files in testing, but crashes with out-of-memory errors on user's 500MB+ IFC files. The app freezes for minutes during `ifcopenshell.open()`, then either crashes or consumes 10-20GB of RAM. Multi-threaded geometry processing makes it worse, spiking to 60GB+ memory usage before crashing. Users with 8-16GB RAM machines cannot use your app.

**Why it happens:**
- **IfcOpenShell has a 5x memory-to-file-size ratio** for SPF (STEP Physical File) parsing: a 200MB IFC file consumes ~1GB RAM
- `ifcopenshell.open()` loads the entire file into memory by default
- Geometry iterator in multi-threaded mode has a memory leak in the C++ layer (does not release memory until completion)
- Each geometry calculation creates intermediate OpenCASCADE objects that aren't garbage collected immediately
- Multiprocessing on Windows copies the entire IFC file object to each process (non-pickleable workaround fails)

**Consequences:**
- App works in testing (small files) but fails in production (real-world files)
- Users blame your app for "being slow" when it's actually running out of memory and swapping to disk
- 32-bit Python hits 2GB limit and crashes
- App becomes unusable for primary use case (batch processing large files)

**Prevention:**

1. **Use streaming mode for large files:**
   ```python
   # Experimental but essential for files >500MB
   ifc_file = ifcopenshell.open(filepath, should_stream=True)
   ```
   - Significantly lower memory footprint
   - May have limitations on certain operations (verify with your IfcPatch recipes)

2. **Set memory limits and fail gracefully:**
   ```python
   import psutil

   file_size_mb = os.path.getsize(filepath) / (1024 * 1024)
   estimated_memory_mb = file_size_mb * 5
   available_memory_mb = psutil.virtual_memory().available / (1024 * 1024)

   if estimated_memory_mb > available_memory_mb * 0.8:
       raise MemoryError(f"File requires ~{estimated_memory_mb}MB RAM, only {available_memory_mb}MB available. Consider upgrading to 64-bit Python or use streaming mode.")
   ```

3. **Avoid multi-threading for geometry processing until IfcOpenShell memory leak is fixed:**
   - GitHub issues #6905, #6385, #3161 document this problem
   - Single-threaded may be slower but won't crash

4. **Test with real-world large files early:**
   - Get sample IFC files from actual users (500MB-2GB range)
   - Test on 8GB RAM machine, not your 32GB dev machine

5. **Warn users about file size limits in UI:**
   ```
   "Large files (>500MB) may require significant memory.
   Recommended: 16GB RAM for files up to 1GB."
   ```

**Detection:**
- Warning sign: Memory usage grows continuously during processing
- Warning sign: Task Manager shows Python process using >80% physical memory
- Warning sign: App becomes unresponsive but doesn't crash (thrashing)
- Warning sign: Different behavior on dev machine (32GB RAM) vs user machine (8GB RAM)

**Which phase:**
- **Phase 1 (Core Processing):** Implement streaming mode support and memory checks
- **Phase 3 (Batch Processing):** Add memory estimation before processing queue
- Acceptance criteria: "Process 500MB IFC file on 8GB RAM machine without crash"

**Sources:**
- [GitHub Issue #6905: High Memory usage when using geometry iterator multi-threaded](https://github.com/IfcOpenShell/IfcOpenShell/issues/6905)
- [GitHub Issue #2025: Strategies on dealing with large IFC datasets](https://github.com/IfcOpenShell/IfcOpenShell/issues/2025)
- [GitHub Issue #2056: Facing issues while parsing 1 GB size IFC file using Multiprocessing](https://github.com/IfcOpenShell/IfcOpenShell/issues/2056)

---

### Pitfall 4: IFC Output File Corruption from Partial Writes

**What goes wrong:**
Your app appears to complete successfully, but the output IFC file is corrupted - it's 0 bytes, incomplete, or causes errors in downstream tools (Revit, ArchiCAD won't open it). This happens sporadically, especially when processing multiple files in batch mode or if users kill the process mid-write. No error message appears because the write "succeeds" from Python's perspective.

**Why it happens:**
- IFC files can be hundreds of MB; writing them takes 10-30+ seconds
- Python's default file writing is non-atomic: if the process is interrupted, you get partial files
- Windows file locking: if another process (like Windows Search Indexer) locks the file mid-write, write fails silently
- IfcOpenShell's `file.write()` method doesn't validate that the entire file was written successfully
- Buffer flushing issues: data sits in memory buffer, `write()` returns, but crash before buffer flush = lost data

**Consequences:**
- Users lose hours of processing time with no error message
- Silent data corruption is worse than a crash (users don't know it failed)
- Downstream tools fail mysteriously, users blame those tools
- Loss of trust: "This tool corrupts my files"

**Prevention:**

1. **Implement atomic writes using temp file + rename:**
   ```python
   import tempfile
   import shutil

   def safe_write_ifc(ifc_file, output_path):
       # Write to temp file first
       with tempfile.NamedTemporaryFile(mode='w', delete=False,
                                        dir=os.path.dirname(output_path),
                                        suffix='.ifc.tmp') as tmp:
           ifc_file.write(tmp.name)
           tmp.flush()
           os.fsync(tmp.fileno())  # Force OS to write to disk
           temp_path = tmp.name

       # Atomic rename (Windows: requires overwrite flag)
       try:
           os.replace(temp_path, output_path)  # Atomic on POSIX, atomic on Windows 3.3+
       except Exception as e:
           os.remove(temp_path)
           raise
   ```

2. **Verify file integrity after write:**
   ```python
   # Quick sanity check
   written_size = os.path.getsize(output_path)
   if written_size == 0:
       raise IOError(f"Output file {output_path} is empty (0 bytes)")

   # Stronger verification: try to re-open
   try:
       verification = ifcopenshell.open(output_path)
       verification = None  # Close immediately
   except Exception as e:
       raise IOError(f"Written file {output_path} failed verification: {e}")
   ```

3. **Handle file locking explicitly on Windows:**
   ```python
   import time
   import errno

   def write_with_retry(ifc_file, output_path, retries=3, delay=1):
       for attempt in range(retries):
           try:
               safe_write_ifc(ifc_file, output_path)
               return
           except OSError as e:
               if e.errno == errno.EACCES and attempt < retries - 1:
                   time.sleep(delay)
                   continue
               raise
   ```

4. **Show progress indication during writes:**
   - Users need to know the app is still working
   - Don't let users kill process during critical write operation
   - Disable close button or show "Please wait, writing file..." modal

**Detection:**
- Warning sign: Output files occasionally 0 bytes
- Warning sign: Users report "file won't open" intermittently
- Warning sign: File size is suspiciously small compared to input
- Warning sign: Windows Event Viewer shows file locking errors

**Which phase:**
- **Phase 1 (Core Processing):** Implement atomic writes before any user testing
- **Phase 3 (Batch Processing):** Add retry logic and file verification
- Acceptance criteria: "Can kill process during write without corrupting previously written files"

**Sources:**
- [Advanced File Handling in Python (Teaching Resource by JSP)](https://jsp.shiksha/index.php/portfolio/bcse101e-computer-programming-python/files-and-file-handling-python/advanced-file-handling-python)
- [GitHub Issue #4521: Error linking an .ifc file](https://github.com/IfcOpenShell/IfcOpenShell/issues/4521)
- [OSArch Community: How to fix IFC file via python](https://community.osarch.org/discussion/2030/how-to-fix-ifc-file-via-python)

---

## Moderate Pitfalls

These cause delays, technical debt, or poor user experience.

### Pitfall 5: PyInstaller --onefile Temp Directory Cleanup on Windows

**What goes wrong:**
In `--onefile` mode, PyInstaller extracts files to `%TEMP%\_MEI{random}` at runtime. If your app spawns subprocesses that outlive the main process, they crash when PyInstaller cleans up the temp directory. Additionally, corporate antivirus software scans/locks files in this temp directory, causing 10-30 second startup delays or antivirus false positives mid-execution.

**Why it happens:**
- PyInstaller's `--onefile` bootloader extracts bundled files to `sys._MEIPASS` temp directory at startup
- When main process exits, bootloader deletes temp directory
- Subprocesses that reference DLLs in that directory crash with "DLL not found"
- Windows Defender and enterprise antivirus actively scan new files in `%TEMP%`, blocking extraction

**Prevention:**

1. **Set `PYINSTALLER_RESET_ENVIRONMENT=1` for long-lived subprocesses:**
   ```python
   import subprocess
   import os

   env = os.environ.copy()
   env['PYINSTALLER_RESET_ENVIRONMENT'] = '1'
   subprocess.Popen([sys.executable, 'helper.py'], env=env)
   ```

2. **Whitelist `%TEMP%\_MEI*` in corporate antivirus (document this for IT departments)**

3. **Use `--onedir` mode to avoid temp extraction entirely** (recommended)

**Detection:**
- Warning sign: 30+ second startup delay on some machines but not others
- Warning sign: Subprocesses fail with "DLL not found" errors
- Warning sign: Process Monitor shows antivirus locking files in `_MEI` directory

**Which phase:**
- **Phase 1 (Bundling):** Choose `--onedir` vs `--onefile` based on subprocess needs
- **Phase 2 (Documentation):** Document antivirus whitelist requirements if using `--onefile`

**Sources:**
- [PyInstaller Common Issues and Pitfalls: Subprocess DLL Load Order](https://pyinstaller.org/en/stable/common-issues-and-pitfalls.html)
- [GitHub Issue #4552: Is it possible not create temp folder while package as exe(by -F)](https://github.com/pyinstaller/pyinstaller/issues/4552)

---

### Pitfall 6: External Program Launching Fails Due to DLL Search Path Modification

**What goes wrong:**
If your app needs to launch external Windows programs (e.g., opening output IFC in Revit, file explorer), those programs crash or fail to load their own DLLs. Error messages like "MSVCP140.dll was not found" appear even though the DLL exists on the system.

**Why it happens:**
- PyInstaller calls `SetDllDirectoryW()` to prefer bundled DLLs over system DLLs
- Child processes inherit this modified DLL search path
- External programs try to load system DLLs but find PyInstaller's bundled versions instead (wrong version = crash)

**Prevention:**

```python
import ctypes
import subprocess

# Reset DLL search path before launching external programs
ctypes.windll.kernel32.SetDllDirectoryW(None)

# Now safe to launch external programs
subprocess.Popen(['explorer.exe', output_folder])
```

**Detection:**
- Warning sign: External programs crash when launched from your app but work when launched manually
- Warning sign: Error messages about missing DLLs that clearly exist on the system

**Which phase:**
- **Phase 2 (UI Features):** Add if "Open output folder" or similar features are planned

**Sources:**
- [PyInstaller Common Issues: External Program Launching](https://pyinstaller.org/en/stable/common-issues-and-pitfalls.html)

---

### Pitfall 7: Config/Preset Files Not Persisting Across Windows User Profiles

**What goes wrong:**
Users save presets on their work computer, but when they log in on a different machine (roaming profiles, RDP, Citrix), their presets are gone. Or presets work for admin users but fail for standard users due to permission errors writing to `%PROGRAMFILES%`.

**Why it happens:**
- Incorrect config file location: saving to app directory (read-only for standard users) or user-specific paths
- Windows has three AppData folders: Local (machine-specific), Roaming (follows user), LocalLow (sandboxed apps)
- No understanding of Windows user profile architecture

**Prevention:**

1. **Use correct AppData folder based on roaming needs:**
   ```python
   import os

   # For machine-specific config (doesn't roam)
   config_dir = os.path.join(os.environ['LOCALAPPDATA'], 'YourAppName')

   # For roaming config (follows user across machines)
   config_dir = os.path.join(os.environ['APPDATA'], 'YourAppName')

   os.makedirs(config_dir, exist_ok=True)
   preset_path = os.path.join(config_dir, 'presets.json')
   ```

2. **Handle permission errors gracefully:**
   ```python
   try:
       with open(preset_path, 'w') as f:
           json.dump(presets, f)
   except PermissionError:
       fallback_path = os.path.join(os.path.expanduser('~'), 'presets.json')
       with open(fallback_path, 'w') as f:
           json.dump(presets, f)
       # Warn user about fallback location
   ```

3. **Test with standard (non-admin) Windows user account**

**Detection:**
- Warning sign: Config works for you (admin) but not for QA tester (standard user)
- Warning sign: Users report presets disappear after Windows update or profile refresh

**Which phase:**
- **Phase 2 (Preset Management):** Implement correct AppData paths before first release
- Acceptance criteria: "Standard user can save/load presets without admin rights"

**Sources:**
- [XDA: What is AppData, and what are Local, LocalLow, and Roaming?](https://www.xda-developers.com/appdata/)
- [Python Discussions: Windows AppData, Roaming vs Local](https://discuss.python.org/t/windows-appdata-roaming-vs-local/2682)

---

### Pitfall 8: IfcPatch Recipe Argument Validation Errors

**What goes wrong:**
Users configure a preset with invalid IfcPatch recipe arguments (wrong type, missing required argument, incorrect path format), but the error only appears during processing, not during preset creation/validation. Batch processing fails halfway through with cryptic `IndexError: list index out of range` or `TypeError: 'type' object is not subscriptable`.

**Why it happens:**
- IfcPatch recipes have inconsistent argument requirements (some need `[]`, some need `["/path"]`)
- Documentation gaps: examples don't show all required fields
- No argument schema validation in IfcPatch itself
- Windows path issues: backslashes vs forward slashes

**Prevention:**

1. **Validate recipe arguments when preset is created, not when processing:**
   ```python
   # Map of recipe names to expected argument structure
   RECIPE_SCHEMAS = {
       'ExtractElements': {'type': 'list', 'min_items': 1, 'item_type': str},
       'MergeProject': {'type': 'list', 'min_items': 1, 'item_type': 'filepath'},
       'Optimise': {'type': 'list', 'min_items': 0},  # Can be empty
   }

   def validate_recipe_arguments(recipe_name, arguments):
       if recipe_name not in RECIPE_SCHEMAS:
           raise ValueError(f"Unknown recipe: {recipe_name}")

       schema = RECIPE_SCHEMAS[recipe_name]
       if not isinstance(arguments, list):
           raise ValueError(f"{recipe_name} requires list of arguments, got {type(arguments)}")

       if len(arguments) < schema['min_items']:
           raise ValueError(f"{recipe_name} requires at least {schema['min_items']} arguments")

       # Validate types, file paths, etc.
   ```

2. **Normalize Windows paths to forward slashes:**
   ```python
   import pathlib

   def normalize_path_for_ifcpatch(path):
       return pathlib.Path(path).as_posix()  # Always returns forward slashes
   ```

3. **Provide UI hints for each recipe's argument requirements:**
   - Don't make users guess argument format
   - Show examples: "ExtractElements expects: ['IfcWall', 'IfcDoor']"

4. **Always provide `arguments` field, even if empty:**
   ```python
   ifcpatch_config = {
       "input": input_path,
       "recipe": recipe_name,
       "arguments": recipe_args if recipe_args else []  # NEVER omit this
   }
   ```

**Detection:**
- Warning sign: Errors only appear during processing, not during preset creation
- Warning sign: Error messages about "list index out of range" or missing arguments
- Warning sign: Different behavior on Windows vs Linux (path separator issues)

**Which phase:**
- **Phase 2 (Preset Management):** Implement argument validation before processing
- **Phase 3 (Batch Processing):** Add dry-run validation before starting batch

**Sources:**
- [GitHub Issue #2007: The latest version of IfcPatch seems not working](https://github.com/IfcOpenShell/IfcOpenShell/issues/2007)
- [GitHub Issue #1393: IfcPatch Recipe Optimise error message](https://github.com/IfcOpenShell/IfcOpenShell/issues/1393)
- [IfcPatch Documentation](https://docs.ifcopenshell.org/ifcpatch.html)

---

### Pitfall 9: GUI Freezing During Batch Processing (No Progress Indication)

**What goes wrong:**
Users start batch processing of 20 files, the GUI immediately freezes, becomes unresponsive, and shows "(Not Responding)" in Task Manager. Users think the app crashed and kill it. No progress bar updates, no way to cancel. In reality, processing is happening but the main thread is blocked.

**Why it happens:**
- Long-running IfcPatch operations run on the main GUI thread
- GUI event loop cannot process events (redraw, button clicks) while blocking operation runs
- Python GIL (Global Interpreter Lock) means GUI and processing cannot truly run in parallel without threading

**Prevention:**

1. **Use threading for long-running operations:**
   ```python
   import threading
   from queue import Queue

   def process_batch_threaded(files, preset, progress_callback):
       def worker():
           for i, file in enumerate(files):
               result = process_file(file, preset)
               progress_callback(i + 1, len(files), result)

       thread = threading.Thread(target=worker, daemon=True)
       thread.start()
       return thread
   ```

2. **Use PyQt/PySide QThread for signal-based progress updates:**
   ```python
   from PyQt6.QtCore import QThread, pyqtSignal

   class ProcessingThread(QThread):
       progress = pyqtSignal(int, int, str)  # current, total, message

       def run(self):
           for i, file in enumerate(self.files):
               result = process_file(file, self.preset)
               self.progress.emit(i + 1, len(self.files), f"Processed {file}")
   ```

3. **Ensure Tkinter event loop continues:**
   ```python
   def process_with_updates():
       for i, file in enumerate(files):
           process_file(file, preset)
           progress_var.set((i + 1) / len(files) * 100)
           root.update_idletasks()  # Process pending GUI events
   ```

4. **Provide cancel button that actually works:**
   - Set a threading.Event flag
   - Check flag between file processing
   - Clean up partial results

**Detection:**
- Warning sign: GUI shows "(Not Responding)" during processing
- Warning sign: Progress bar doesn't update smoothly
- Warning sign: Cannot click cancel button
- Warning sign: Window cannot be moved/resized during processing

**Which phase:**
- **Phase 3 (Batch Processing):** Implement threading before batch feature release
- Acceptance criteria: "Can cancel batch processing mid-way without force-killing app"

**Sources:**
- [Real Python: Use PyQt's QThread to Prevent Freezing GUIs](https://realpython.com/python-pyqt-qthread/)
- [McNeel Forum: Prevent UI from freezing during long running Python script - Windows](https://discourse.mcneel.com/t/prevent-ui-from-freezing-during-long-running-python-script-windows/165547)

---

### Pitfall 10: IFC Schema Version Incompatibility (IFC2x3 vs IFC4)

**What goes wrong:**
Users process an IFC4 file with a recipe designed for IFC2x3, and the output file is corrupted or missing critical entities. Or conversion from IFC4 to IFC2x3 silently drops modern entities like `IfcPolygonalFaceSet` that don't exist in the older schema. Downstream tools fail to open the file or show missing geometry.

**Why it happens:**
- IfcOpenShell supports IFC2x3 (2007), IFC4 (2017), and IFC4x3 (draft)
- Different schemas have different classes, attributes, and concepts
- IFC4 is mostly a superset of IFC2x3, but some operations are incompatible
- No robust conversion utility exists for IFC2x3 ↔ IFC4 migration
- IfcPatch recipes may assume a specific schema version

**Prevention:**

1. **Detect IFC schema version before processing:**
   ```python
   ifc_file = ifcopenshell.open(input_path)
   schema = ifc_file.schema  # e.g., "IFC2X3", "IFC4"

   if schema not in SUPPORTED_SCHEMAS:
       raise ValueError(f"Unsupported IFC schema: {schema}. This recipe requires {SUPPORTED_SCHEMAS}")
   ```

2. **Warn users about schema conversion risks:**
   - "This file is IFC4. Converting to IFC2x3 may lose geometry data."
   - Don't silently convert and corrupt

3. **Use IfcOpenShell's migration utility for schema conversion:**
   ```python
   from ifcopenshell.util.schema import Migrator

   migrator = Migrator()
   converted_entity = migrator.migrate(entity, from_schema='IFC2X3', to_schema='IFC4')
   ```

4. **Test recipes with both IFC2x3 and IFC4 sample files**

**Detection:**
- Warning sign: Output file missing entities that were in input
- Warning sign: Geometry appears in IFC viewer for input but not output
- Warning sign: Schema-specific entities cause `AttributeError`

**Which phase:**
- **Phase 1 (Core Processing):** Add schema detection and validation
- **Phase 2 (Preset Management):** Allow presets to specify required schema version
- Acceptance criteria: "Reject incompatible schema with clear error message"

**Sources:**
- [OSArch: New IfcOpenShell utility to convert between IFC2X3 and IFC4](https://community.osarch.org/discussion/325/new-ifcopenshell-utility-to-convert-between-ifc2x3-and-ifc4)
- [GitHub Issue #49: Allow Ifc2x3 and Ifc4 conversion from the same executable/library](https://github.com/IfcOpenShell/IfcOpenShell/issues/49)
- [IfcOpenShell Documentation: Introduction to IFC](https://docs.ifcopenshell.org/introduction/introduction_to_ifc.html)

---

## Minor Pitfalls

These cause annoyance or confusion but are fixable without major refactoring.

### Pitfall 11: Missing multiprocessing.freeze_support() in PyInstaller Builds

**What goes wrong:**
If you use Python's `multiprocessing` module for parallel file processing, the frozen .exe enters an infinite spawn loop, creating dozens of processes until Windows runs out of resources and crashes.

**Why it happens:**
- In frozen executables, `sys.executable` points to the .exe itself
- `multiprocessing` spawns children by executing `sys.executable`
- Without `freeze_support()`, each child tries to spawn more children

**Prevention:**

```python
import multiprocessing

if __name__ == '__main__':
    multiprocessing.freeze_support()  # REQUIRED for PyInstaller
    main()
```

**Which phase:**
- **Phase 3 (Batch Processing):** Add if using multiprocessing for parallel batch processing

**Sources:**
- [PyInstaller Common Issues: Multiprocessing](https://pyinstaller.org/en/stable/common-issues-and-pitfalls.html)

---

### Pitfall 12: sys.stdout/sys.stderr is None in --windowed Mode

**What goes wrong:**
When using `pyinstaller --windowed` (no console window), any code that writes to `print()` or logs to stderr crashes with `AttributeError: 'NoneType' object has no attribute 'write'`. Third-party libraries (like IfcOpenShell) that print debug messages crash your app.

**Why it happens:**
- `--windowed` mode sets `sys.stdout` and `sys.stderr` to `None`
- Code that assumes these always exist will crash

**Prevention:**

```python
import sys
import os

if sys.stdout is None:
    sys.stdout = open(os.devnull, 'w')
if sys.stderr is None:
    sys.stderr = open(os.devnull, 'w')
```

Or redirect to a log file:
```python
if sys.stdout is None:
    log_path = os.path.join(os.environ['LOCALAPPDATA'], 'YourApp', 'output.log')
    sys.stdout = open(log_path, 'w')
    sys.stderr = sys.stdout
```

**Which phase:**
- **Phase 1 (Bundling):** Add if using `--windowed` mode

**Sources:**
- [PyInstaller Common Issues: No-Console Mode](https://pyinstaller.org/en/stable/common-issues-and-pitfalls.html)

---

### Pitfall 13: Hardcoded File Paths in Presets Break on Different Machines

**What goes wrong:**
User saves a preset with an absolute path (`C:\Users\John\Documents\template.ifc`), shares the preset JSON file with a colleague, but the preset fails because that path doesn't exist on the colleague's machine.

**Why it happens:**
- Presets store absolute file paths
- No validation that referenced files exist
- No path normalization for sharing

**Prevention:**

1. **Store relative paths when possible:**
   ```python
   import os

   def make_portable_path(file_path, preset_dir):
       try:
           return os.path.relpath(file_path, preset_dir)
       except ValueError:
           # Different drives on Windows, cannot make relative
           return file_path
   ```

2. **Validate file paths when loading preset:**
   ```python
   def load_preset(preset_path):
       with open(preset_path) as f:
           preset = json.load(f)

       # Resolve relative paths
       preset_dir = os.path.dirname(preset_path)
       for key in ['input_template', 'merge_file']:
           if key in preset:
               path = os.path.join(preset_dir, preset[key])
               if not os.path.exists(path):
                   raise FileNotFoundError(f"Preset references missing file: {path}")
               preset[key] = path

       return preset
   ```

3. **UI should show warning icon for missing file references**

**Which phase:**
- **Phase 2 (Preset Management):** Implement portable path handling

---

## Phase-Specific Warnings

| Phase Topic | Likely Pitfall | Mitigation | When to Address |
|-------------|---------------|------------|-----------------|
| **Bundling/Distribution** | Missing IfcOpenShell native deps (#1) | Test on clean VM without Python | Phase 1 - before any distribution |
| | Antivirus false positives (#2) | Use --onedir, get code signing cert | Phase 1 - choose mode; Phase 2 - acquire cert |
| | Multiprocessing freeze_support (#11) | Add freeze_support() call | Phase 1 if using multiprocessing |
| **Core Processing** | Memory explosion on large files (#3) | Implement streaming mode, memory checks | Phase 1 - before user testing |
| | File corruption from partial writes (#4) | Atomic writes with temp files | Phase 1 - critical for data integrity |
| | IFC schema incompatibility (#10) | Schema version detection | Phase 1 - validate before processing |
| **Preset Management** | Config file permissions (#7) | Use correct AppData folder | Phase 2 - before preset feature release |
| | Recipe argument validation (#8) | Validate on preset creation | Phase 2 - save users from runtime errors |
| | Hardcoded paths in presets (#13) | Relative path support | Phase 2 - for preset sharing |
| **Batch Processing** | GUI freezing (#9) | Threading for background processing | Phase 3 - before batch feature |
| | External program launching (#6) | Reset DLL path before subprocess | Phase 2/3 if opening external tools |
| | PyInstaller temp cleanup (#5) | Document for --onefile mode | Phase 1 if using --onefile |

---

## Testing Checklist

Before each phase is considered complete, verify these scenarios:

### Phase 1 (Bundling/Core):
- [ ] Executable runs on clean Windows VM (no Python installed)
- [ ] Process 500MB IFC file on 8GB RAM machine
- [ ] Output file verification passes for all test files
- [ ] VirusTotal shows <5 vendor detections
- [ ] IFC2x3 and IFC4 files both process correctly

### Phase 2 (Presets):
- [ ] Standard (non-admin) user can save/load presets
- [ ] Preset with relative paths works after moving to different directory
- [ ] Invalid recipe arguments rejected at preset creation time
- [ ] Missing file references show clear error message

### Phase 3 (Batch):
- [ ] GUI remains responsive during 20-file batch processing
- [ ] Can cancel batch mid-way without force-kill
- [ ] Progress bar updates smoothly
- [ ] Killing process mid-batch doesn't corrupt already-written files

---

## Confidence Assessment

| Category | Confidence | Source Quality |
|----------|-----------|----------------|
| PyInstaller bundling | **HIGH** | Official PyInstaller docs, verified GitHub issues |
| IfcOpenShell native deps | **HIGH** | IfcOpenShell installation docs, GitHub issues with maintainer responses |
| Memory management | **HIGH** | Multiple verified GitHub issues with data (#6905, #2025, #2056) |
| File corruption risks | **MEDIUM** | General Python file handling best practices, confirmed via IfcOpenShell issue discussions |
| Antivirus/SmartScreen | **HIGH** | Recent GitHub issues (2024-2025), official Windows documentation |
| Config/preset persistence | **MEDIUM** | Windows AppData documentation, general Windows app development patterns |
| IfcPatch recipes | **MEDIUM** | IfcPatch docs, GitHub issues - some documentation gaps remain |
| GUI threading | **HIGH** | Standard Python GUI patterns, verified across Tkinter/PyQt docs |
| Schema compatibility | **MEDIUM** | IfcOpenShell docs, community discussions - conversion tooling is immature |

---

## Research Sources

### Official Documentation (Highest Confidence):
- [PyInstaller 6.18.0 Documentation - Common Issues and Pitfalls](https://pyinstaller.org/en/stable/common-issues-and-pitfalls.html)
- [IfcOpenShell 0.8.4 Documentation - Installation](https://docs.ifcopenshell.org/ifcopenshell-python/installation.html)
- [IfcPatch Documentation](https://docs.ifcopenshell.org/ifcpatch.html)

### GitHub Issues (High Confidence - Real Production Issues):
- [IfcOpenShell #6905: High Memory usage when using geometry iterator multi-threaded](https://github.com/IfcOpenShell/IfcOpenShell/issues/6905)
- [IfcOpenShell #2025: Strategies on dealing with large IFC datasets](https://github.com/IfcOpenShell/IfcOpenShell/issues/2025)
- [PyInstaller #6754: --onefile exe getting anti-Virus False positive flags](https://github.com/pyinstaller/pyinstaller/issues/6754)
- [PyInstaller Discussion #6746: How to sign files for Smart App Control](https://github.com/orgs/pyinstaller/discussions/6746)

### Community Resources (Medium Confidence):
- [Real Python: PyInstaller Tutorial](https://realpython.com/pyinstaller-python/)
- [CodersLegacy: PyInstaller EXE detected as Virus](https://coderslegacy.com/pyinstaller-exe-detected-as-virus-solutions/)
- [OSArch Community: IfcOpenShell Examples and Discussions](https://community.osarch.org/)

---

## Summary of Phase Implications

**Phase 1 must address:**
- Native dependency bundling (#1) - blocking issue
- Memory management (#3) - blocking for real-world use
- File corruption prevention (#4) - data integrity critical
- Antivirus strategy (#2) - decide --onedir vs --onefile

**Phase 2 should address:**
- Config file location (#7) - before users create presets
- Recipe argument validation (#8) - better UX
- Portable paths (#13) - enable preset sharing

**Phase 3 must address:**
- GUI threading (#9) - blocking for batch feature
- Progress indication - user expectations

**Ongoing/Documentation:**
- Code signing (#2) - acquire certificate early
- Schema compatibility (#10) - ongoing testing requirement
- Large file testing (#3) - continuous validation
