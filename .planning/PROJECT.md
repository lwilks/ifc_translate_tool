# IFC Coordinate Transform Tool

## What This Is

A standalone Windows desktop application that wraps IfcPatch's OffsetObjectPlacements recipe, enabling users to transform IFC file coordinates from real-world/survey coordinates back to local project coordinate systems. Built for non-technical users who need batch processing and preset management without touching Blender, Bonsai, or command-line tools.

## Core Value

Users can transform IFC coordinates reliably with saved presets, processing single or multiple files without technical knowledge.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Load and process individual IFC files
- [ ] Batch process multiple IFC files from input directory
- [ ] Configure X/Y/Z offset values
- [ ] Configure rotation values
- [ ] Toggle "Rotate First" operation order
- [ ] Save transformation settings as named presets
- [ ] Load presets to populate form fields
- [ ] Configure input directory for batch processing
- [ ] Configure output directory for processed files
- [ ] Output files keep original filename in output directory
- [ ] Runs as standalone Windows executable (no Python installation required)

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
| Desktop app over web | Client needs local file access, no server infrastructure | — Pending |
| OffsetObjectPlacements only | Scoped to client's actual need, avoid feature creep | — Pending |

---
*Last updated: 2025-01-30 after initialization*
