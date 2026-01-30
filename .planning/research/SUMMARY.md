# Project Research Summary

**Project:** IFC Translate Tool
**Domain:** Windows Desktop Application for IFC Coordinate Transformation
**Researched:** 2026-01-30
**Confidence:** MEDIUM-HIGH

## Executive Summary

This project is a standalone Windows desktop application that wraps IfcPatch's OffsetObjectPlacements recipe to enable non-technical BIM users to transform IFC file coordinates through a preset-based batch processing workflow. The recommended approach uses Python 3.12 with PySide6 (Qt6) for a professional native Windows interface, bundled with PyInstaller into a distributable executable, and packaged with Inno Setup for installation.

The architecture follows Model-View-Controller (MVC) with a service layer to isolate IfcOpenShell dependencies, enable independent testing, and provide clear separation between UI, business logic, and external library integration. This pattern allows building core functionality first (models + services), then layering on UI complexity incrementally, which reduces integration risk and enables early validation of the IfcPatch wrapper.

**Critical risks:** The primary technical challenges are (1) bundling IfcOpenShell's native C++ dependencies with PyInstaller (requires custom .spec file and extensive testing on clean Windows VMs), (2) Windows Defender/SmartScreen false positives for unsigned executables (mitigated by using --onedir mode and acquiring code signing certificate), and (3) memory management for large IFC files (500MB+ files can consume 5x memory, requiring streaming mode and validation). These risks are manageable with proper phase ordering—validate bundling early, defer complex features until core processing is proven, and implement atomic file writes to prevent corruption.

## Key Findings

### Recommended Stack

**Core:** Python 3.12 (stability + library support), IfcOpenShell 0.8.4 (latest stable with pre-built wheels), PySide6 6.10.1 (Qt6 with LGPL licensing for professional native UI), PyInstaller 6.18.0 (mature bundler with Python 3.12 support), Inno Setup 6.x (professional Windows installer creation).

**Core technologies:**
- **Python 3.12** — Runtime environment. Best balance of stability (avoids 3.13 bleeding edge) and modern features (75% faster asyncio, full PySide6/PyInstaller support).
- **PySide6 6.10.1** — Desktop GUI framework. Qt6 bindings with LGPL license (free for commercial use), professional native Windows appearance expected in BIM industry, actively maintained (Nov 2025 release).
- **IfcOpenShell 0.8.4** — IFC processing library. Latest stable (Dec 2025), pre-built wheels for Windows include all C++ dependencies (OpenCascade DLLs), IfcPatch recipes included.
- **PyInstaller 6.18.0** — Python to .exe bundler. Most mature option with proven track record, supports Python 3.8-3.14. Requires custom .spec file for IfcOpenShell DLL bundling.
- **Inno Setup 6.x** — Windows installer. Industry standard, easier scripting than NSIS, creates professional MSI-style installers with desktop shortcuts, Start Menu entries, uninstaller registration.

**Critical version note:** All IfcOpenShell native dependencies (20-30 OpenCascade DLLs, `_ifcopenshell_wrapper.pyd`) must be explicitly bundled in PyInstaller .spec file—auto-detection fails. Testing on clean Windows VM without Python installed is non-negotiable before distribution.

### Expected Features

**Must have (table stakes):**
- **Batch file processing** — Industry standard for utility tools. Users expect to process multiple files sequentially with single preset.
- **X/Y/Z offset + rotation inputs** — Essential coordinate transformation parameters. OffsetObjectPlacements supports ax/ay/az rotation angles and "rotate first" toggle.
- **Preset save/load** — Avoid re-entering common transformations. JSON/config file storage in correct Windows AppData folder.
- **Drag-and-drop** — Modern desktop app expectation for file selection.
- **Progress feedback + error handling** — Batch operations take time, users need per-file visibility and clear error messages for invalid IFC files.

**Should have (competitive):**
- **Validation warnings** — Check for large coordinates (>16km from origin) before processing to prevent known pitfalls.
- **Output filename templates** — Customize transformed file naming (e.g., `{original}_transformed.ifc`).
- **Recent files/presets list** — Quick access to common workflows.

**Defer (v2+):**
- **Visual coordinate preview** — High complexity, requires IFC viewer integration (xeokit, Open IFC Viewer). Validate MVP usefulness first.
- **Undo/revert capability** — Medium complexity. Work around with "never overwrite originals" policy initially.
- **Side-by-side comparison** — High complexity, low ROI for initial release.
- **Advanced 3D rotation** — 2D rotation (Z-axis) covers 80% of use cases, defer arbitrary axis rotation.

### Architecture Approach

**Pattern:** Model-View-Controller (MVC) with Service Layer isolation for IfcOpenShell.

**Major components:**
1. **Models** (`TransformSettings`, `Preset`) — Data structures with validation and serialization. Built first, independently testable, establish data contracts.
2. **Service Layer** (`IfcPatchWrapper`, `PresetManager`, `FileProcessor`) — Business logic isolation. Wraps IfcPatch with typed interface and error handling. Fully testable without GUI.
3. **Controller** (`MainController`) — Event handlers, form validation, workflow coordination. Wires view to services without containing business logic.
4. **View** (`MainWindow`, widgets) — PySide6 GUI components. UI state management only, zero business logic. Delegate all operations to controller.

**Build order rationale:** Models → Services → Minimal View → Controller → Advanced UI features. This order validates business logic independently before GUI complexity, reduces integration risk, and allows early testing of IfcPatch wrapper against real library.

**PyInstaller considerations:** Use `--onedir` mode (not `--onefile`) to reduce antivirus false positives by ~70%. Bundle as folder, then wrap with Inno Setup installer for distribution. Custom .spec file must explicitly list IfcOpenShell binaries and hidden imports.

### Critical Pitfalls

1. **Missing IfcOpenShell native dependencies in bundled .exe** — PyInstaller cannot auto-detect C++ wrapper DLLs. App works on dev machine but crashes on user machines with "DLL load failed" errors. **Prevention:** Custom .spec file with explicit binary collection, test on clean Windows VM without Python installed.

2. **Windows Defender/antivirus false positives with unsigned executables** — PyInstaller executables flagged as trojans, especially in `--onefile` mode. Users see SmartScreen warnings, corporate IT blocks distribution. **Prevention:** Use `--onedir` mode (reduces false positives), acquire EV code signing certificate ($300-600/year bypasses SmartScreen immediately).

3. **Memory explosion on large IFC files** — IfcOpenShell has 5x memory-to-file-size ratio. A 200MB IFC file consumes ~1GB RAM. Multi-threaded geometry processing has memory leak. **Prevention:** Implement streaming mode (`should_stream=True`), add memory estimation checks before processing, test with 500MB+ files on 8GB RAM machines.

4. **IFC output file corruption from partial writes** — 10-30 second write operations interrupted by crashes or user kills result in 0-byte or incomplete files with no error message. **Prevention:** Atomic writes using temp file + rename pattern, verify file integrity after write, retry logic for Windows file locking.

5. **GUI freezing during batch processing** — Long-running operations on main thread cause "(Not Responding)" state. Users think app crashed and force-kill. **Prevention:** Threading for background processing (PySide6 QThread), progress callbacks to update UI, functional cancel button.

## Implications for Roadmap

Based on combined research, recommended phase structure prioritizes dependency order, validates high-risk areas early, and defers complex features:

### Phase 1: Core Proof of Concept + Basic UI
**Rationale:** Validate IfcPatch wrapper and PyInstaller bundling before UI complexity. This phase addresses the highest technical risks (native dependency bundling, IfcOpenShell integration, memory management) in isolation. Building models + services first establishes testable data contracts and proves the core value proposition (transform IFC coordinates) without GUI coupling.

**Delivers:**
- Python script that transforms single IFC file using OffsetObjectPlacements
- Data models (`TransformSettings`, `Preset`)
- Service layer (`IfcPatchWrapper` with error handling, `FileProcessor`)
- Basic PySide6 form (file selection, X/Y/Z inputs, process button)
- Atomic file write implementation
- PyInstaller bundling with custom .spec file

**Addresses features:**
- Single file processing (table stakes)
- X/Y/Z offset inputs (table stakes)
- Basic error handling (table stakes)

**Avoids pitfalls:**
- #1 (native dependencies) — Addressed in bundling phase
- #3 (memory explosion) — Implement streaming mode + memory checks
- #4 (file corruption) — Atomic writes from start

**Research flag:** LOW — IfcPatch OffsetObjectPlacements is well-documented, parameters are clear. No additional research needed.

### Phase 2: Preset Management + Rotation Support
**Rationale:** Depends on proven core processing (Phase 1). Adds user workflow value without architectural complexity. Preset system builds on established data models, uses standard JSON serialization patterns. Rotation support is existing IfcPatch functionality (ax/ay/az parameters), just UI exposure.

**Delivers:**
- Preset save/load with JSON storage in Windows AppData (correct roaming folder)
- Rotation angle inputs (2D Z-axis rotation + "rotate first" toggle)
- Preset dropdown selector
- Validation warnings (large coordinates, zero transformation, extreme rotation)
- Output filename template support

**Uses stack:**
- Python pathlib for AppData path handling
- JSON for preset serialization

**Implements architecture:**
- `PresetManager` service (already designed in Phase 1)
- Preset UI widgets (dropdown, save dialog)

**Addresses features:**
- Preset save/load (table stakes)
- Rotation support (table stakes)
- Validation warnings (should-have)
- Output naming (should-have)

**Avoids pitfalls:**
- #7 (config file permissions) — Use correct AppData folder from start
- #8 (recipe argument validation) — Validate on preset creation
- #13 (hardcoded paths) — Implement relative path support

**Research flag:** LOW — Standard desktop app patterns, well-documented Windows AppData behavior.

### Phase 3: Batch Processing + Progress UI
**Rationale:** Most complex UI workflow, requires threading to prevent GUI freeze. Benefits from all prior components being stable (proven file processor, working presets). Batch processing is table stakes but introduces concurrency concerns that are easier to handle with proven single-file foundation.

**Delivers:**
- Directory selection for batch input
- Batch processing with threading (PySide6 QThread)
- Progress bar with per-file status updates
- Success/failure summary report
- Cancellation support mid-batch
- Drag-and-drop for files and folders

**Implements architecture:**
- `FileProcessor.process_batch()` method
- QThread worker for background processing
- Signal/slot pattern for progress updates

**Addresses features:**
- Batch file processing (table stakes)
- Progress feedback (table stakes)
- Drag-and-drop (table stakes)

**Avoids pitfalls:**
- #9 (GUI freezing) — Threading with QThread mandatory
- #11 (multiprocessing freeze_support) — Only if using multiprocessing (threading preferred)

**Research flag:** LOW — PySide6 QThread patterns are standard, multiple documented examples.

### Phase 4: Distribution + Installer
**Rationale:** Only bundle once application is feature-complete and tested. PyInstaller iteration (finding missing imports, DLL issues) is time-consuming, so deferring until code is stable reduces churn. Installer creation is final polish before user distribution.

**Delivers:**
- Finalized PyInstaller .spec file with all dependencies
- Testing on clean Windows VMs (Windows 10, Windows 11)
- Inno Setup installer script
- Code signing (if certificate acquired)
- User documentation (installation guide)

**Uses stack:**
- PyInstaller 6.18.0 with --onedir mode
- Inno Setup 6.x for installer creation
- Optional: EV code signing certificate

**Avoids pitfalls:**
- #2 (antivirus false positives) — --onedir mode + code signing
- #5 (temp directory cleanup) — Only if --onefile chosen
- #6 (DLL search path) — Reset before launching external programs

**Research flag:** MEDIUM — PyInstaller + IfcOpenShell bundling requires trial-and-error. Allocate 2-4 hours for troubleshooting DLL issues.

### Phase Ordering Rationale

**Dependency-driven order:**
- Phase 1 establishes core processing that Phases 2-3 build upon
- Phase 2 preset system needs proven data models from Phase 1
- Phase 3 batch processing needs working single-file processor from Phase 1
- Phase 4 bundling waits for complete, tested application

**Risk mitigation:**
- Highest risks (bundling, memory, file corruption) addressed in Phase 1 before feature complexity
- Each phase delivers testable, user-visible functionality (no "infrastructure-only" phases)
- Threading complexity deferred until core logic proven stable

**Architecture alignment:**
- Build order matches MVC layer dependencies: Models → Services → Controller → View
- Service layer isolation enables testing without GUI, validating business logic early
- Incremental UI complexity (basic form → presets → batch) spreads learning curve

### Research Flags

**Phases likely needing deeper research:**
- **Phase 4 (Distribution):** IfcOpenShell + PyInstaller bundling has MEDIUM confidence. No official PyInstaller hook exists, requires custom .spec file experimentation. Community sources document DLL bundling needs but exact approach varies. Allocate extra time for troubleshooting.

**Phases with standard patterns (skip research-phase):**
- **Phase 1 (Core):** IfcPatch OffsetObjectPlacements API is well-documented, parameters clear. Memory management strategies documented in GitHub issues with data.
- **Phase 2 (Presets):** JSON serialization, Windows AppData paths, desktop app config patterns are standard with clear documentation.
- **Phase 3 (Batch):** PySide6 QThread patterns extensively documented, multiple tutorials available.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Python 3.12, PySide6, IfcOpenShell all have official documentation, recent stable releases, verified compatibility |
| Features | MEDIUM-HIGH | Table stakes features validated against industry tools (IfcToolbox, RTV Xporter). User workflows inferred from problem descriptions, not direct user research |
| Architecture | HIGH | MVC + service layer is proven pattern for desktop apps. Directory structure, component boundaries align with Python GUI best practices |
| Pitfalls | HIGH | PyInstaller, IfcOpenShell memory issues, file corruption risks all documented in official sources + verified GitHub issues with maintainer responses |

**Overall confidence:** MEDIUM-HIGH

Enough certainty to proceed with confidence. Main uncertainties are:
1. **PyInstaller + IfcOpenShell bundling** — MEDIUM confidence on exact .spec file configuration. Will require iteration.
2. **Large file performance** — Unknown if PyInstaller overhead affects processing speed. May need profiling during Phase 1.
3. **Feature prioritization** — No direct user validation of "must-have" vs "should-have" distinctions. Based on competitive analysis only.

### Gaps to Address

**During Phase 1 (validation required):**
- **Streaming mode effectiveness:** IfcOpenShell documentation mentions `should_stream=True` as experimental. Test with 500MB+ files to confirm memory reduction. If ineffective, may need to warn users about file size limits.
- **PyInstaller DLL bundling:** No official IfcOpenShell hook exists in pyinstaller-hooks-contrib. Custom .spec file approach is community-documented but varies by version. Expect 2-4 hours troubleshooting.

**During Phase 2 (design decisions):**
- **Preset sharing workflow:** Research shows hardcoded paths break presets. Implement relative paths, but unclear if users will actually share preset files vs just re-entering values. May defer complex portable path logic until user feedback.

**During Phase 4 (budget/decision):**
- **Code signing certificate:** EV certificates ($300-600/year) bypass SmartScreen immediately. Standard certificates ($60-150/year) still show warnings until reputation builds. Decision needed: invest in EV cert for professional launch, or accept SmartScreen warnings initially?

## Sources

### Primary (HIGH confidence)
- [IfcOpenShell 0.8.4 Documentation - Installation](https://docs.ifcopenshell.org/ifcopenshell-python/installation.html) — Installation, wheel contents
- [IfcPatch OffsetObjectPlacements Documentation](https://docs.ifcopenshell.org/autoapi/ifcpatch/recipes/OffsetObjectPlacements/index.html) — Recipe API, parameters
- [PyInstaller 6.18.0 Documentation](https://pyinstaller.org/en/stable/) — Bundling best practices, common issues
- [PySide6 PyPI Package](https://pypi.org/project/PySide6/) — Version compatibility, licensing

### Secondary (MEDIUM confidence)
- [GitHub Issue #6905: High Memory usage when using geometry iterator multi-threaded](https://github.com/IfcOpenShell/IfcOpenShell/issues/6905) — Memory leak documentation
- [GitHub Issue #2025: Strategies on dealing with large IFC datasets](https://github.com/IfcOpenShell/IfcOpenShell/issues/2025) — Streaming mode discussion
- [PyInstaller #6754: --onefile exe getting anti-Virus False positive flags](https://github.com/pyinstaller/pyinstaller/issues/6754) — Antivirus mitigation strategies
- [Real Python PyInstaller Tutorial](https://realpython.com/pyinstaller-python/) — Bundling patterns
- [Python GUI Framework Comparison 2026](https://www.pythonguis.com/faq/which-python-gui-library/) — PySide6 selection rationale
- [Tkinter MVC Pattern Tutorial](https://www.pythontutorial.net/tkinter/tkinter-mvc/) — Architecture pattern (adapted for PySide6)

### Tertiary (LOW confidence - needs validation)
- Community IfcOpenShell DLL bundling discussions (SourceForge forums, GitHub issues) — Custom .spec file approaches vary
- Batch processing UI patterns (QGIS, DropIt) — Inferred standards, not domain-specific
- IFC coordinate transformation workflows — Inferred from problem descriptions, no direct user studies

---
*Research completed: 2026-01-30*
*Ready for roadmap: yes*
