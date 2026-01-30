# Phase 4: Distribution - Research

**Researched:** 2026-01-30
**Domain:** Python application packaging for Windows distribution (PyInstaller + Inno Setup)
**Confidence:** MEDIUM

## Summary

This research covers creating a standalone Windows executable from a Python/Tkinter application that uses ifcopenshell (with native C++ extensions) and distributing it via a Windows installer with Start Menu and Desktop shortcuts.

PyInstaller is the standard tool for bundling Python applications into standalone executables. It supports Python 3.8-3.14, bundles the Python interpreter and all dependencies, and produces executables that run without Python installed. The key challenge for this project is bundling ifcopenshell's native C++ wrapper (`_ifcopenshell_wrapper.pyd`) and its dependent DLLs correctly.

Inno Setup is the recommended tool for creating professional Windows installers. It is free, open-source, mature (since 1997), and provides Start Menu shortcuts, Desktop shortcuts, and uninstaller functionality out of the box.

**Primary recommendation:** Use PyInstaller with `--collect-all ifcopenshell` and `--collect-all ifcpatch` to bundle native libraries, then wrap the output with Inno Setup for professional installation experience.

## Standard Stack

The established libraries/tools for this domain:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| PyInstaller | 6.18.0 | Bundle Python apps to executables | De facto standard, active maintenance, hook ecosystem |
| pyinstaller-hooks-contrib | latest | Community hooks for PyInstaller | Auto-installed with PyInstaller, handles many packages |
| Inno Setup | 6.x | Create Windows installer | Free, open-source, mature, widely trusted |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| UPX | 4.x | Compress executables | Optional - reduces size but can corrupt some DLLs |
| pefile | latest | Debug DLL dependencies | Only if debugging missing DLL issues |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| PyInstaller | cx_Freeze, py2exe | Less active, smaller hook ecosystem |
| Inno Setup | NSIS, InstallForge | NSIS is more complex; InstallForge is simpler but less powerful |
| --onefile | --onedir | onedir is faster to start, easier to debug, but multiple files |

**Installation:**
```bash
pip install pyinstaller pyinstaller-hooks-contrib
# Inno Setup: Download from https://jrsoftware.org/isdl.php (Windows only)
```

## Architecture Patterns

### Recommended Project Structure
```
project/
├── src/
│   ├── main.py          # Entry point
│   ├── model.py
│   ├── view.py
│   └── controller.py
├── build/               # PyInstaller working files (gitignored)
├── dist/                # PyInstaller output (gitignored)
├── installer/           # Inno Setup scripts
│   └── setup.iss        # Inno Setup script
├── ifc_translate.spec   # PyInstaller spec file (version controlled)
└── requirements.txt
```

### Pattern 1: Spec File-Based Build
**What:** Use a `.spec` file for reproducible, configurable builds instead of command-line arguments
**When to use:** Always for production builds; allows version control of build configuration

**Example:**
```python
# ifc_translate.spec
# Source: PyInstaller official documentation
from PyInstaller.utils.hooks import collect_all, collect_dynamic_libs, collect_data_files

datas = []
binaries = []
hiddenimports = []

# Collect all ifcopenshell components including native wrapper
tmp_ret = collect_all('ifcopenshell')
datas += tmp_ret[0]
binaries += tmp_ret[1]
hiddenimports += tmp_ret[2]

# Collect all ifcpatch components including recipes
tmp_ret = collect_all('ifcpatch')
datas += tmp_ret[0]
binaries += tmp_ret[1]
hiddenimports += tmp_ret[2]

a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='IFC Translate Tool',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # Disable UPX to avoid DLL corruption
    console=False,  # Hide console for GUI app
    icon='assets/icon.ico',  # Optional application icon
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name='IFC Translate Tool',
)
```

### Pattern 2: Inno Setup Script
**What:** Configure Windows installer with shortcuts and uninstaller
**When to use:** For professional distribution

**Example:**
```iss
; setup.iss - Inno Setup script
; Source: Inno Setup official documentation
[Setup]
AppName=IFC Translate Tool
AppVersion=1.0.0
AppPublisher=Your Company
DefaultDirName={autopf}\IFC Translate Tool
DefaultGroupName=IFC Translate Tool
OutputBaseFilename=IFC_Translate_Tool_Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\IFC Translate Tool.exe

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\IFC Translate Tool\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs

[Icons]
Name: "{group}\IFC Translate Tool"; Filename: "{app}\IFC Translate Tool.exe"
Name: "{group}\Uninstall IFC Translate Tool"; Filename: "{uninstallexe}"
Name: "{commondesktop}\IFC Translate Tool"; Filename: "{app}\IFC Translate Tool.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\IFC Translate Tool.exe"; Description: "{cm:LaunchProgram,IFC Translate Tool}"; Flags: nowait postinstall skipifsilent
```

### Anti-Patterns to Avoid
- **Using --onefile with native extensions:** Can cause DLL loading issues, slower startup, harder to debug
- **UPX compression with Qt/native DLLs:** Corrupts Control Flow Guard (CFG) enabled DLLs
- **Cross-compiling:** PyInstaller cannot cross-compile; must build on target OS
- **Skipping spec file:** Command-line builds are hard to reproduce and maintain

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Executable creation | Manual py2exe scripts | PyInstaller with spec file | Handles dependencies, hooks, native libs |
| DLL discovery | Manual DLL copying | `collect_all()`, `collect_dynamic_libs()` | Recursive dependency analysis |
| Hidden import detection | Trial and error | PyInstaller Analysis + hooks | Community-maintained knowledge base |
| Windows installer | Batch file/ZIP | Inno Setup | Professional UX, Start Menu, uninstaller |
| VC++ Runtime bundling | Manual DLL bundling | PyInstaller auto-bundling | Handles MSVC runtime dependencies |

**Key insight:** PyInstaller's hook system and helper functions (collect_all, collect_dynamic_libs) automate what would otherwise be hours of manual DLL hunting. Trust the tooling.

## Common Pitfalls

### Pitfall 1: Missing ifcopenshell Native Dependencies
**What goes wrong:** Application crashes with "DLL load failed" or "ImportError: No module named '_ifcopenshell_wrapper'"
**Why it happens:** ifcopenshell has a native C++ wrapper (`_ifcopenshell_wrapper.pyd`) that depends on other DLLs
**How to avoid:** Use `collect_all('ifcopenshell')` which gathers all binaries including the native wrapper
**Warning signs:** Works in development but fails when running built executable

### Pitfall 2: Missing ifcpatch Recipes
**What goes wrong:** "Recipe not found" errors when running transformation
**Why it happens:** ifcpatch loads recipes dynamically from its recipes directory
**How to avoid:** Use `collect_all('ifcpatch')` to include all recipe Python files as data
**Warning signs:** Application starts but transformation fails with recipe errors

### Pitfall 3: UPX Corrupting DLLs
**What goes wrong:** Crashes with obscure errors, DLL validation failures
**Why it happens:** UPX compression corrupts DLLs with Control Flow Guard (CFG) enabled
**How to avoid:** Set `upx=False` in spec file, or use `--noupx` command line
**Warning signs:** Random crashes, different behavior on different Windows versions

### Pitfall 4: Console Window Appearing
**What goes wrong:** Black console window appears alongside GUI
**Why it happens:** Default PyInstaller behavior shows console
**How to avoid:** Set `console=False` in EXE() or use `--noconsole`/`--windowed` flag
**Warning signs:** Visible console window when running application

### Pitfall 5: Testing Only on Development Machine
**What goes wrong:** Works on dev machine, fails on clean Windows install
**Why it happens:** Dev machine has Python, Visual C++ runtime, and other dependencies pre-installed
**How to avoid:** Test on clean Windows VM or machine without Python installed
**Warning signs:** "Python DLL not found" or Visual C++ runtime errors on target machine

### Pitfall 6: Relative Path Issues
**What goes wrong:** Application cannot find data files or resources
**Why it happens:** Running from dist folder changes working directory
**How to avoid:** Use `os.path.dirname(__file__)` or PyInstaller's `sys._MEIPASS` for paths
**Warning signs:** FileNotFoundError for bundled resources

### Pitfall 7: VCRUNTIME140.dll Issues
**What goes wrong:** "vcruntime140.dll is missing" errors
**Why it happens:** Visual C++ 2015+ runtime not installed on target machine; or UPX corrupts the DLL
**How to avoid:** Disable UPX with `--noupx` or `--upx-exclude vcruntime140.dll`
**Warning signs:** Missing DLL errors specifically for Visual C++ runtime

## Code Examples

Verified patterns from official sources:

### Building with PyInstaller (Command Line)
```bash
# Source: PyInstaller official documentation
# Initial build to generate spec file
pyinstaller --name "IFC Translate Tool" --windowed --collect-all ifcopenshell --collect-all ifcpatch src/main.py

# Subsequent builds using spec file
pyinstaller ifc_translate.spec
```

### Debugging Import Issues
```bash
# Source: PyInstaller when-things-go-wrong documentation
# Build with import debugging enabled
pyinstaller --debug=imports src/main.py

# Then run the executable to see import trace
./dist/main/main.exe
```

### Collecting Native Libraries in Hook/Spec
```python
# Source: PyInstaller hooks documentation
from PyInstaller.utils.hooks import collect_all, collect_dynamic_libs

# Method 1: collect_all (recommended - gets everything)
datas, binaries, hiddenimports = collect_all('ifcopenshell')

# Method 2: collect_dynamic_libs (native libs only)
binaries = collect_dynamic_libs('ifcopenshell')
```

### Handling Resource Paths in Bundled App
```python
# Source: PyInstaller operating-mode documentation
import sys
import os

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and bundled."""
    if hasattr(sys, '_MEIPASS'):
        # Running as bundled executable
        return os.path.join(sys._MEIPASS, relative_path)
    # Running in development
    return os.path.join(os.path.dirname(__file__), relative_path)
```

### Inno Setup Desktop Shortcut
```iss
; Source: Inno Setup official documentation
[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Icons]
; Start Menu shortcut (always created)
Name: "{group}\IFC Translate Tool"; Filename: "{app}\IFC Translate Tool.exe"
; Desktop shortcut (optional, based on task selection)
Name: "{commondesktop}\IFC Translate Tool"; Filename: "{app}\IFC Translate Tool.exe"; Tasks: desktopicon
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Manual DLL bundling | collect_all(), collect_dynamic_libs() | PyInstaller 4.x+ | Automatic recursive dependency collection |
| py2exe, cx_Freeze preferred | PyInstaller dominant | ~2018 | Better hook ecosystem, active maintenance |
| --onefile common | --onedir recommended | PyInstaller 5.x+ | Fewer DLL loading issues, faster startup |
| Manual VC++ redist | PyInstaller auto-bundles | PyInstaller 4.x+ | MSVC runtime included automatically |

**Deprecated/outdated:**
- **py2exe:** Largely unmaintained, PyInstaller preferred
- **--onefile for complex apps:** Now discouraged for apps with native extensions
- **UPX by default:** Now disabled by default due to DLL corruption issues

## Open Questions

Things that couldn't be fully resolved:

1. **ifcopenshell PyInstaller Hook Existence**
   - What we know: No dedicated hook found in pyinstaller-hooks-contrib for ifcopenshell
   - What's unclear: Whether collect_all() is sufficient or custom hook needed
   - Recommendation: Try collect_all() first; create custom hook if issues arise

2. **ifcpatch Dynamic Recipe Loading**
   - What we know: ifcpatch loads recipes dynamically from recipes directory
   - What's unclear: Whether collect_all() captures all recipe files properly
   - Recommendation: Verify OffsetObjectPlacements recipe is included; add explicit datas if not

3. **Windows 10 vs Windows 11 Compatibility**
   - What we know: PyInstaller targets Windows 8+ officially
   - What's unclear: Any Windows 11-specific issues
   - Recommendation: Test on both Windows 10 and 11 VMs

4. **Visual C++ Runtime Version**
   - What we know: Python 3.11 uses MSVC 14.x (VS 2015+); Windows 10+ includes Universal CRT
   - What's unclear: Whether additional VC++ redistributable needed on all target machines
   - Recommendation: Test on clean Windows VM; include VC++ redist prerequisite in installer if needed

## Sources

### Primary (HIGH confidence)
- [PyInstaller 6.18.0 Documentation](https://pyinstaller.org/en/stable/) - usage, spec files, hooks, troubleshooting
- [Inno Setup Official Help](https://jrsoftware.org/ishelp/) - icons section, setup section, script syntax

### Secondary (MEDIUM confidence)
- [Real Python PyInstaller Guide](https://realpython.com/pyinstaller-python/) - practical examples, best practices
- [PythonGUIs Tkinter Packaging Tutorial](https://www.pythonguis.com/tutorials/packaging-tkinter-applications-windows-pyinstaller/) - Tkinter-specific workflow
- [Microsoft VC++ Redistributable Docs](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist) - runtime requirements

### Tertiary (LOW confidence)
- WebSearch findings on ifcopenshell + PyInstaller (no specific guides found)
- GitHub issues on pyinstaller-hooks-contrib (no ifcopenshell hook found)

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - PyInstaller and Inno Setup are well-documented industry standards
- Architecture: MEDIUM - spec file patterns are documented; ifcopenshell-specific patterns unverified
- Pitfalls: MEDIUM - general PyInstaller pitfalls well-documented; ifcopenshell-specific issues theoretical

**Research date:** 2026-01-30
**Valid until:** 60 days (PyInstaller stable, ifcopenshell dependency may vary)
