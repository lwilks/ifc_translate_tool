# Technology Stack

**Project:** IFC Translate Tool
**Domain:** Windows Desktop Application for IFC File Processing
**Researched:** 2026-01-30
**Overall Confidence:** MEDIUM-HIGH

---

## Executive Summary

For a standalone Windows desktop application that bundles IfcOpenShell/IfcPatch, the recommended 2025-2026 stack is:

- **UI Framework:** PySide6 (Qt6) for professional native Windows look
- **Bundler:** PyInstaller 6.x for mature IfcOpenShell compatibility
- **Python Version:** Python 3.12 for stability and broad library support
- **Installer:** Inno Setup for professional Windows installer creation

This stack prioritizes:
1. **Native dependencies bundling** - IfcOpenShell has C++ dependencies that must bundle correctly
2. **Non-technical user experience** - Native Windows UI, double-click .exe, standard installer
3. **Development maturity** - Proven tools with established patterns
4. **2025-2026 currency** - All recommendations use actively maintained versions

---

## Recommended Stack

### Core Framework & Language

| Technology | Version | Purpose | Confidence | Why |
|------------|---------|---------|------------|-----|
| **Python** | **3.12.x** | Runtime language | HIGH | Best balance of stability, library support, and performance. Avoids 3.13 bleeding edge (experimental features) and 3.11 EOL concerns. 3.12 has 75% faster asyncio (if needed later), full PySide6 support, and PyInstaller maturity. |
| **IfcOpenShell** | **0.8.4.post1** | IFC file processing | HIGH | Latest stable release (Dec 2025). Provides pre-built wheels for Python 3.9-3.14 on Windows x86-64. Bundles all C++ dependencies (OpenCascade, etc.) in wheel. |
| **IfcPatch** | **(bundled with IfcOpenShell)** | Recipe framework | HIGH | OffsetObjectPlacements recipe included. No separate installation needed. |

### UI Framework

| Technology | Version | Purpose | Confidence | Why |
|------------|---------|---------|------------|-----|
| **PySide6** | **6.10.1** | Desktop GUI framework | HIGH | Qt6 bindings with LGPL license (free for commercial use). Professional native Windows look. Excellent for simple forms (QDialog, QLineEdit, QPushButton, QFileDialog). Actively maintained (Nov 2025 release). PyQt6 alternative rejected due to GPL/commercial licensing. CustomTkinter rejected - less professional appearance for BIM industry users. |

**Key PySide6 components for this project:**
- `QApplication` - Application framework
- `QMainWindow` or `QDialog` - Main window
- `QFileDialog.getOpenFileName()` - IFC file selection
- `QLineEdit` - X/Y/Z offset inputs, rotation angle input
- `QPushButton` - Execute button, file selection trigger
- `QLabel` - Form labels
- `QProgressDialog` - Optional processing feedback

### Executable Bundler

| Technology | Version | Purpose | Confidence | Why |
|------------|---------|---------|------------|-----|
| **PyInstaller** | **6.18.0** | Python to .exe conversion | MEDIUM-HIGH | Most mature bundler with proven track record. Supports Python 3.8-3.14. Handles numpy, matplotlib, PyQt/PySide. **Critical:** IfcOpenShell bundling requires custom handling (see below). PyInstaller chosen over alternatives because: (1) cx_Freeze - no IfcOpenShell patterns found, (2) Nuitka - hour-long compile times impractical for iterative development despite better performance. |
| **pyinstaller-hooks-contrib** | **2025.11** | Community hooks library | MEDIUM | May provide hooks for dependencies. **Note:** No official IfcOpenShell hook found - will require custom spec file. |

**PyInstaller Configuration Requirements:**

IfcOpenShell bundling is NON-TRIVIAL. The library includes:
- `_ifcopenshell_wrapper.pyd` - Binary Python extension (C++ compiled)
- Native DLLs: `IfcParse.dll`, `IfcGeom.dll` (may be statically linked)
- OpenCascade DLLs: `TKernel.dll`, etc.
- MSVC runtime: `msvcrxxx.dll`

**Required approach:**
1. Create custom `.spec` file with manual binary collection
2. Add hidden imports: `ifcopenshell.ifcopenshell_wrapper`
3. Collect data files from IfcOpenShell package directory
4. Bundle all DLLs found in site-packages/ifcopenshell/

**Example spec file structure needed:**
```python
# Custom hook approach
hiddenimports = ['ifcopenshell.ifcopenshell_wrapper']

# Collect IfcOpenShell binaries
import ifcopenshell
ifc_path = os.path.dirname(ifcopenshell.__file__)
binaries = [(os.path.join(ifc_path, '*.dll'), '.')]
datas = [(ifc_path, 'ifcopenshell')]
```

**Testing requirement:** Bundled .exe must run on fresh Windows VM without Python installed to verify all dependencies included.

### Installer Creation

| Technology | Version | Purpose | Confidence | Why |
|------------|---------|---------|------------|-----|
| **Inno Setup** | **6.x** | Windows installer creator | MEDIUM-HIGH | Industry standard for Python desktop apps. Creates professional MSI-style installers. Easier scripting than NSIS for standard use cases. Free and open source. Handles: desktop shortcuts, Start Menu entries, uninstaller registration, version checking. |

**Alternative considered:** NSIS - More flexible but harder for beginners, overkill for this simple app.

### Supporting Libraries

| Library | Version | Purpose | Confidence | When to Use |
|---------|---------|---------|------------|-------------|
| **pathlib** | **(stdlib)** | File path handling | HIGH | Always - use `Path` objects instead of string manipulation |
| **typing** | **(stdlib 3.12)** | Type hints | HIGH | Always - improves code maintainability |

**Explicitly NOT needed:**
- `tkinter` - Using PySide6 instead
- `PyQt6` - Using PySide6 for licensing
- Web frameworks (Flask/FastAPI) - Desktop app, not web app
- Database libraries - No persistence needed for single-file processing
- Async libraries - File processing is synchronous

---

## Alternatives Considered & Rejected

### UI Frameworks

| Rejected | Reason |
|----------|--------|
| **CustomTkinter** | Modern appearance but less professional than Qt. BIM industry expects native Windows look. Learning curve similar to PySide6 anyway. |
| **PyQt6** | Technically superior but GPL license requires commercial license purchase for closed-source distribution. PySide6 is LGPL (free for commercial use). 99.9% identical API to PySide6. |
| **Tkinter** | Outdated appearance. Non-native widgets. Would harm professional credibility for BIM tool. |
| **Kivy** | Touch-oriented, mobile-first. Overkill and wrong paradigm for simple Windows form. |
| **wxPython** | Native widgets but less actively maintained than Qt. Smaller community. |

### Bundlers

| Rejected | Reason |
|----------|--------|
| **cx_Freeze** | Faster load times than PyInstaller but less mature ecosystem. No documented IfcOpenShell bundling patterns found. Requires more manual configuration. Not worth risk for this project. |
| **Nuitka** | Best performance (2-3x faster load) and security but compile times of 1+ hour with large libraries (OpenCascade via IfcOpenShell qualifies). Impractical for iterative development. Consider for v2.0 if performance critical. |
| **PyOxidizer** | Modern Rust-based approach but immature ecosystem for Windows GUI apps. Limited PySide6 documentation. |
| **Auto-py-to-exe** | GUI wrapper around PyInstaller. Adds no value - just learn PyInstaller directly. |

### Python Versions

| Rejected | Reason |
|----------|--------|
| **Python 3.13** | Too new (Oct 2024 release). Experimental free-threaded mode and JIT compiler not needed. Risk of library incompatibilities. IfcOpenShell 0.8.4 supports it but PySide6/PyInstaller ecosystem still stabilizing. |
| **Python 3.11** | Solid choice but 3.12 has better asyncio performance (75% faster) and longer support runway. 3.11 already 2+ years old. |
| **Python 3.9-3.10** | Approaching EOL. 3.9 drops security updates October 2025. No reason to start new project on old version. |

### Installer Tools

| Rejected | Reason |
|----------|--------|
| **NSIS** | More customizable than Inno Setup but harder to learn. Scripting is more complex. Overkill for simple installer needs. Choose if you need UI customization beyond standard installer. |
| **WiX Toolset** | XML-based MSI creation. Professional but steep learning curve. Better for enterprise deployment scenarios. Inno Setup simpler for indie/small team. |
| **No installer (zip distribution)** | Poor user experience for non-technical users. Manual file extraction, no Start Menu entry, no uninstaller. BIM users expect professional installers. |

---

## Installation & Setup

### Development Environment Setup

```bash
# Create virtual environment with Python 3.12
python3.12 -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Install core dependencies
pip install ifcopenshell==0.8.4.post1
pip install PySide6==6.10.1

# Install bundling tools
pip install pyinstaller==6.18.0
pip install pyinstaller-hooks-contrib==2025.11

# Development tools (optional)
pip install black  # Code formatting
pip install mypy   # Type checking
```

### Verify IfcOpenShell Installation

```python
# Test script - verify_ifc.py
import ifcopenshell
import ifcopenshell.ifcopenshell_wrapper

print(f"IfcOpenShell version: {ifcopenshell.version}")
print(f"Wrapper module: {ifcopenshell.ifcopenshell_wrapper}")
print("Installation successful!")
```

### PyInstaller First Build

```bash
# Simple test - will likely fail on first attempt
pyinstaller --onefile --windowed main.py

# Proper approach - create spec file
pyinstaller --onefile --windowed --name IFCTranslateTool main.py

# Edit IFCTranslateTool.spec to add IfcOpenShell binaries
# Then rebuild
pyinstaller IFCTranslateTool.spec
```

---

## Special Considerations for IfcOpenShell

### 1. Native Dependency Bundling

**Problem:** IfcOpenShell is C++ library with Python bindings. PyInstaller auto-detection often misses DLLs.

**Solution approach:**
- IfcOpenShell distributes as pre-built wheels with bundled C++ libraries
- These are in site-packages/ifcopenshell/ directory after pip install
- PyInstaller spec file must explicitly collect these binaries
- **Testing on clean Windows install is mandatory**

**Known dependencies to bundle:**
- `_ifcopenshell_wrapper.pyd` - Main binary extension
- OpenCascade DLLs (TKernel, TKMath, TKBRep, etc.) - ~20-30 DLLs
- MSVC runtime (usually auto-included by PyInstaller)

### 2. File Path Handling in Bundled App

**Problem:** PyInstaller creates temporary directory when running, changing file paths.

**Solution:**
```python
import sys
import os

def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and PyInstaller"""
    try:
        # PyInstaller creates temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
```

### 3. Error Handling for Missing Dependencies

**Problem:** IfcOpenShell import failures show generic errors, hiding DLL issues.

**Solution:**
```python
try:
    import ifcopenshell
except ImportError as e:
    # Show user-friendly error before crashing
    from PySide6.QtWidgets import QMessageBox
    QMessageBox.critical(None, "Installation Error",
                        f"Failed to load IFC library: {e}\n\n"
                        "Please reinstall the application.")
    sys.exit(1)
```

### 4. IFC File Size Considerations

**Problem:** Large IFC files (100MB+) may cause UI freezing during processing.

**Solution for v1.0:** Accept UI freeze (simple synchronous processing)
**Solution for v2.0:** Consider QThread for background processing with QProgressDialog

---

## Architecture Patterns for This Stack

### Application Structure

```
ifc_translate_tool/
├── main.py                 # Entry point, QApplication setup
├── ui/
│   ├── __init__.py
│   └── main_window.py     # QDialog/QMainWindow subclass
├── core/
│   ├── __init__.py
│   └── processor.py       # IfcPatch wrapper, business logic
├── utils/
│   ├── __init__.py
│   └── paths.py           # get_resource_path helper
├── requirements.txt       # pip dependencies
├── IFCTranslateTool.spec  # PyInstaller configuration (generated, then customized)
└── installer/
    └── inno_setup.iss     # Inno Setup script
```

### Separation of Concerns

**UI Layer (PySide6):**
- Form validation (numeric inputs)
- File dialog handling
- User feedback (success/error messages)
- NO business logic

**Core Layer (IfcPatch):**
- IFC file loading
- OffsetObjectPlacements execution
- File writing
- NO UI code

**Benefits:**
- Testable core logic without UI
- Easy to add CLI version later
- Clear dependencies (core → IfcOpenShell, UI → PySide6)

---

## Version Compatibility Matrix

| Component | Minimum | Recommended | Maximum Tested |
|-----------|---------|-------------|----------------|
| Python | 3.9 | **3.12** | 3.14 |
| IfcOpenShell | 0.8.0 | **0.8.4.post1** | 0.8.4.post1 |
| PySide6 | 6.5 | **6.10.1** | 6.10.1 |
| PyInstaller | 6.0 | **6.18.0** | 6.18.0 |
| Windows | 10 | **10/11** | 11 |

**Note:** All components support Python 3.9-3.14, providing flexibility if version conflicts arise.

---

## Development Workflow Recommendations

### Phase 1: Core Development
```bash
# Run directly in Python during development
python main.py
```
Fast iteration, full debugging capabilities.

### Phase 2: Bundling Testing
```bash
# Build executable
pyinstaller IFCTranslateTool.spec

# Test on development machine
dist/IFCTranslateTool.exe
```
Verify bundling works, identify missing dependencies.

### Phase 3: Clean Install Testing
```bash
# Copy dist/IFCTranslateTool.exe to Windows VM without Python
# Run and verify all functionality
```
**Critical step** - catches DLL issues before release.

### Phase 4: Installer Creation
```bash
# Run Inno Setup compiler on .iss script
iscc installer/inno_setup.iss
```
Produces setup.exe for distribution.

---

## Risk Assessment

### High Confidence Areas
- Python 3.12 stability ✓
- PySide6 maturity for simple forms ✓
- IfcOpenShell installation via pip ✓
- Inno Setup installer creation ✓

### Medium Confidence Areas
- **IfcOpenShell + PyInstaller bundling** - Requires custom spec file, no official hook found. Risk: DLL bundling issues requiring trial-and-error. Mitigation: Allocate 2-4 hours for PyInstaller configuration debugging.
- **First-time PyInstaller users** - Learning curve for spec file customization. Mitigation: Use provided template, test early.

### Low Confidence Areas (Further Research Needed)
- **Large IFC file performance** - Unknown if PyInstaller overhead affects IfcOpenShell processing speed. May need profiling.
- **Windows Defender false positives** - PyInstaller .exes sometimes flagged. May need code signing certificate ($200-400/year).

---

## Confidence Ratings Summary

| Area | Confidence | Source | Notes |
|------|------------|--------|-------|
| Python 3.12 | HIGH | Official docs, PyPI | Stable release, broad support |
| IfcOpenShell 0.8.4 | HIGH | PyPI, official docs | Latest stable, pre-built wheels |
| PySide6 6.10.1 | HIGH | PyPI, Qt docs | Recent release, mature |
| PyInstaller 6.18.0 | HIGH | Official docs | Current version, Python 3.12 support |
| IfcOpenShell bundling approach | MEDIUM | WebSearch (community discussions), GitHub issues | No official hook, requires custom spec file. LOW confidence on exact approach - will need experimentation. |
| Inno Setup | MEDIUM-HIGH | Community consensus, comparison articles | Industry standard but not personally verified |

---

## Sources

### Primary Sources (HIGH Confidence)
- [IfcOpenShell 0.8.4 Documentation - Installation](https://docs.ifcopenshell.org/ifcopenshell-python/installation.html)
- [IfcOpenShell PyPI Package](https://pypi.org/project/ifcopenshell/)
- [PySide6 PyPI Package](https://pypi.org/project/PySide6/)
- [PyInstaller 6.18.0 Documentation](https://pyinstaller.org/en/stable/)
- [IfcPatch OffsetObjectPlacements Recipe](https://docs.ifcopenshell.org/autoapi/ifcpatch/recipes/OffsetObjectPlacements/index.html)

### Secondary Sources (MEDIUM Confidence)
- [How to Build a Desktop Application Using Python in 2025](https://code-b.dev/blog/building-desktop-applications-using-python)
- [10 Best Python GUI Frameworks for Developers in 2025 - GeeksforGeeks](https://www.geeksforgeeks.org/blogs/best-python-gui-frameworks-for-developers/)
- [Tkinter vs. PySide in 2025 | An Honest Comparison](https://tkinterbuilder.com/comparison.html)
- [Which Python GUI library should you use in 2026?](https://www.pythonguis.com/faq/which-python-gui-library/)
- [Python Executable Generators - PyInstaller vs. Nuitka vs. CX Freeze](https://sparxeng.com/blog/software/python-standalone-executable-generators-pyinstaller-nuitka-cx-freeze)
- [The Ultimate Guide to Converting Python Scripts to Executables](https://medium.com/@edarit88/the-ultimate-guide-to-converting-python-scripts-to-executables-pyinstaller-cx_freeze-and-nuitka-d6f548f24ac6)
- [Inno Setup VS NSIS - Feature Comparison (2025)](https://appmus.com/vs/nsis-vs-inno-setup)
- [Top Python Speed Improvements in Recent Versions (3.11 to 3.13)](https://inindiatech.com/next/python-speed-improvements-3-11-to-3-13)

### Community Sources (LOW Confidence - Flagged for Validation)
- IfcOpenShell DLL bundling discussions (SourceForge forums, GitHub issues)
- PyInstaller hooks-contrib repository (no ifcopenshell hook found as of 2026-01-30)
- Community reports on PyInstaller + IfcOpenShell requiring manual spec file configuration

---

## Next Steps for Roadmap

Based on this stack research, recommended roadmap phase structure:

1. **Phase 1: Core Proof of Concept**
   - Python 3.12 + IfcOpenShell basic script (CLI)
   - Verify OffsetObjectPlacements works
   - **No bundling complexity yet**

2. **Phase 2: UI Implementation**
   - Add PySide6 form interface
   - File dialog, input fields, execute button
   - Run as `python main.py` during development

3. **Phase 3: Executable Bundling** (RESEARCH FLAG)
   - PyInstaller spec file configuration
   - IfcOpenShell DLL bundling
   - **Allocate extra time - this is high-risk area**

4. **Phase 4: Installer & Distribution**
   - Inno Setup configuration
   - Clean Windows VM testing
   - Final packaging

**Critical research flag:** Phase 3 will likely require deeper investigation when reached. Current understanding is MEDIUM confidence - enough to proceed but expect troubleshooting.
