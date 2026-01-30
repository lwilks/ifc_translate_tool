# IFC Coordinate Transform Tool

## What This Is

A standalone Windows desktop application that wraps IfcPatch's OffsetObjectPlacements recipe, enabling users to transform IFC file coordinates from real-world/survey coordinates back to local project coordinate systems. Built for non-technical users who need batch processing and preset management without touching Blender, Bonsai, or command-line tools.

## Core Value

Users can transform IFC coordinates reliably with saved presets, processing single or multiple files without technical knowledge.

## Current State

**Version:** v1.0 MVP (shipped 2026-01-30)
**Status:** Feature complete, ready for Windows build

**Codebase:**
- 1,373 lines of Python
- MVC architecture (model, view, controller, presets_model)
- Tkinter UI with threading for responsiveness

**Tech Stack:**
- Python 3.11
- ifcopenshell 0.7.10 / ifcpatch 0.7.10
- platformdirs for cross-platform preset storage
- PyInstaller for Windows bundling
- Inno Setup for installer

## Requirements

### Validated

- TRAN-01: Apply X/Y/Z coordinate offsets — v1.0
- TRAN-02: Apply rotation values — v1.0
- TRAN-03: Toggle "Rotate First" operation order — v1.0
- FILE-01: Load and process individual IFC files — v1.0
- FILE-02: Batch process multiple IFC files — v1.0
- FILE-03: Configure output directory — v1.0
- FILE-04: Output files keep original filename — v1.0
- PRES-01: Save transformation presets — v1.0
- PRES-02: Load presets to populate fields — v1.0
- PRES-03: Delete saved presets — v1.0
- PRES-04: Auto-load last used preset — v1.0
- DIST-01: Run as standalone Windows executable — v1.0

### Active

(None — v1.0 complete)

### Out of Scope

- macOS/Linux support — client is Windows-only
- Other IfcPatch recipes — focusing on OffsetObjectPlacements only
- File preview/visualization — just transformation, no 3D viewer
- Cloud/web deployment — desktop app only
- IFC file editing beyond coordinate transformation

## Context

**Domain:** BIM (Building Information Modeling) workflows. IFC files often arrive with coordinates in survey/real-world systems that need shifting to local project coordinates for downstream use.

**Current workflow being replaced:** Client currently uses Blender with Bonsai plugin to manually process each file. No batch capability, no preset storage, requires BIM software knowledge.

**End user profile:** Non-technical Windows user at client organization. Needs to run installer/executable and use simple form interface. Cannot be expected to install Python or use command line.

**Technology dependency:** IfcPatch (part of IfcOpenShell ecosystem) provides the underlying transformation capability via the OffsetObjectPlacements recipe.

## Constraints

- **Platform**: Windows — client environment is Windows-only
- **Distribution**: Standalone executable — user cannot install Python
- **Dependency**: IfcOpenShell/IfcPatch — must bundle with application
- **UI Complexity**: Simple form — non-technical users, minimal learning curve

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Desktop app over web | Client needs local file access, no server infrastructure | Good |
| OffsetObjectPlacements only | Scoped to client's actual need, avoid feature creep | Good |
| ifcopenshell 0.7.10 | 0.8.x has circular import bug | Good |
| MVC with Tkinter | Simple, built-in, cross-platform for development | Good |
| platformdirs for presets | Handles OS-specific conventions automatically | Good |
| threading.Event for cancellation | Thread-safe signaling pattern | Good |
| --onedir PyInstaller mode | Better native extension compatibility | Good |
| UPX disabled | Prevents DLL corruption with native extensions | Good |

---
*Last updated: 2026-01-30 after v1.0 milestone*
