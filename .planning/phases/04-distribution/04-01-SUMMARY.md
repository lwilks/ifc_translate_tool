---
phase: 04-distribution
plan: 01
subsystem: build-configuration
tags: [pyinstaller, inno-setup, windows, packaging, distribution]
dependencies:
  requires: [01-03, 02-02, 03-02]
  provides: [distribution-config, installer-script, build-tools]
  affects: [04-02]
tech-stack:
  added: [pyinstaller, inno-setup]
  patterns: [spec-file-configuration, installer-scripting]
key-files:
  created:
    - requirements-dev.txt
    - ifc_translate.spec
    - installer/setup.iss
  modified:
    - .gitignore
decisions:
  - Use --onedir mode for PyInstaller (better native extension compatibility)
  - Disable UPX compression (prevents DLL corruption)
  - Desktop shortcut unchecked by default (reduces desktop clutter)
  - Separate requirements-dev.txt for build tools
metrics:
  duration: 1.7min
  completed: 2026-01-30
---

# Phase 04 Plan 01: Distribution Configuration Summary

**One-liner:** PyInstaller spec with collect_all for ifcopenshell/ifcpatch native libraries, Inno Setup installer with Start Menu shortcuts

## What Was Built

Created complete Windows distribution configuration files for bundling the IFC Translate Tool as a standalone executable with professional installer.

**Key deliverables:**
1. **requirements-dev.txt** - Development dependencies including PyInstaller
2. **ifc_translate.spec** - PyInstaller configuration with native library collection
3. **installer/setup.iss** - Inno Setup installer script with shortcuts
4. **Updated .gitignore** - Build artifact exclusions

## Tasks Completed

| Task | Description | Commit | Files |
|------|-------------|--------|-------|
| 1 | Create development requirements and update gitignore | 8433050 | requirements-dev.txt, .gitignore |
| 2 | Create PyInstaller spec file | 237d1bf | ifc_translate.spec |
| 3 | Create Inno Setup installer script | dea2dfa | installer/setup.iss |

## Technical Approach

### PyInstaller Configuration

**Challenge:** ifcopenshell and ifcpatch use native C++ extensions that require careful bundling.

**Solution:**
- Used `collect_all()` hook for ifcopenshell, ifcpatch, and platformdirs
- Captures native wrappers (`_ifcopenshell_wrapper.pyd`), DLLs, and recipe files
- Disabled UPX compression to prevent DLL corruption (research pitfall #3)
- Used --onedir mode (COLLECT) for better native extension reliability

**Spec file structure:**
```python
# Collect all dependencies with native components
ifcopenshell_datas, ifcopenshell_binaries, ifcopenshell_hiddenimports = collect_all('ifcopenshell')
ifcpatch_datas, ifcpatch_binaries, ifcpatch_hiddenimports = collect_all('ifcpatch')
platformdirs_datas, platformdirs_binaries, platformdirs_hiddenimports = collect_all('platformdirs')

# Combine and pass to Analysis
a = Analysis(
    ['src/main.py'],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    ...
)

# GUI configuration
exe = EXE(
    ...
    console=False,  # No console window
    upx=False,      # Disable UPX
)
```

### Inno Setup Configuration

**Installer features:**
- Modern wizard UI with LZMA compression
- Start Menu program group with application and uninstaller shortcuts
- Optional desktop shortcut (unchecked by default)
- Launch application option after installation
- x64 architecture configuration

**File structure:**
```
installer/
  setup.iss           # Inno Setup script
  Output/             # Generated installer (gitignored)
    IFC_Translate_Tool_Setup.exe
```

### Development Dependencies

**requirements-dev.txt includes:**
- All production dependencies (ifcopenshell, ifcpatch, platformdirs)
- Build tools (pyinstaller, pyinstaller-hooks-contrib)

**Rationale:** Separates build-time from runtime dependencies, keeps production requirements.txt clean.

### Build Artifacts Management

**Updated .gitignore:**
```
*.spec.bak          # PyInstaller backup files
installer/*.exe     # Compiled installer
installer/Output/   # Inno Setup output directory
```

## Decisions Made

**1. Use --onedir mode instead of --onefile**
- **Rationale:** Native extensions (ifcopenshell C++ wrapper) work more reliably in directory mode
- **Impact:** Larger distribution footprint but better compatibility and faster startup
- **Alternative considered:** --onefile mode rejected due to native extension extraction overhead

**2. Disable UPX compression**
- **Rationale:** Research (04-RESEARCH.md pitfall #3) shows UPX can corrupt native DLLs
- **Impact:** Larger executable size but eliminates runtime DLL errors
- **Alternative considered:** Selective UPX exclusion - rejected as overly complex

**3. Desktop shortcut unchecked by default**
- **Rationale:** Reduces desktop clutter, users can opt-in
- **Impact:** Start Menu remains primary access point
- **Pattern:** Standard installer convention

**4. Separate requirements-dev.txt**
- **Rationale:** Build tools shouldn't be in production dependencies
- **Impact:** Clearer dependency separation, smaller production install
- **Alternative considered:** Single requirements.txt - rejected for clarity

## Verification Results

All verification criteria passed:

- [x] requirements-dev.txt includes pyinstaller
- [x] ifc_translate.spec shows collect_all for ifcopenshell, ifcpatch, platformdirs
- [x] installer/setup.iss shows Inno Setup structure
- [x] .gitignore includes installer and spec backup patterns

**File validation:**
- `ifc_translate.spec` - Valid Python syntax with PyInstaller DSL
- `installer/setup.iss` - Valid Inno Setup script syntax
- `requirements-dev.txt` - Valid pip requirements format

## Next Phase Readiness

**Blockers:** None

**Concerns:** None - configuration files can be created on any platform

**What's needed for Phase 04 Plan 02:**
- These configuration files are ready to use
- Build must be performed on Windows (PyInstaller and Inno Setup)
- Will need Windows environment for actual build execution

**Dependencies satisfied:**
- All application code from Phase 01-03 complete
- Entry point (src/main.py) exists
- All dependencies specified in requirements.txt

## Deviations from Plan

None - plan executed exactly as written.

## Files Changed

**Created:**
- `requirements-dev.txt` - Development dependencies
- `ifc_translate.spec` - PyInstaller build configuration
- `installer/setup.iss` - Inno Setup installer script

**Modified:**
- `.gitignore` - Added build artifact patterns

**Total changes:**
- 3 files created
- 1 file modified
- ~150 lines added

## Commit Summary

```
8433050 chore(04-01): add development requirements and build artifacts to gitignore
237d1bf feat(04-01): add PyInstaller spec file for Windows distribution
dea2dfa feat(04-01): add Inno Setup installer script for Windows
```

## Performance

**Duration:** 1.7 minutes (103 seconds)
**Tasks:** 3/3 completed
**Commits:** 3 atomic commits
**Velocity:** ~34 seconds per task

## Key Takeaways

**What worked well:**
- Clean separation of build configuration from application code
- Comprehensive .gitignore patterns prevent artifact commits
- Well-documented configuration files with inline comments
- Atomic commits per task provide clear history

**What was learned:**
- collect_all() hook is essential for packages with native extensions
- UPX compression must be disabled for DLL-heavy applications
- --onedir mode is more reliable than --onefile for complex dependencies

**For future phases:**
- Configuration files are platform-agnostic, can be created anywhere
- Actual build must be done on Windows with PyInstaller + Inno Setup installed
- Test build process will validate these configurations
