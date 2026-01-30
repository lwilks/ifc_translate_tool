# Roadmap: IFC Coordinate Transform Tool

## Overview

This roadmap delivers a standalone Windows desktop application that transforms IFC file coordinates through a four-phase journey: establishing core transformation capability with a basic UI, adding preset management for workflow efficiency, enabling batch processing for multiple files, and finally packaging everything into a distributable executable. Each phase builds on proven foundations, with Phase 1 validating the highest technical risks (IfcPatch integration, PyInstaller bundling) before adding UI complexity.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 1: Core Transformation + Basic UI** - Single file processing with coordinate transformation
- [x] **Phase 2: Preset Management** - Save and reuse transformation settings
- [x] **Phase 3: Batch Processing** - Process multiple IFC files at once
- [x] **Phase 4: Distribution** - Package as standalone Windows executable

## Phase Details

### Phase 1: Core Transformation + Basic UI
**Goal**: Users can transform single IFC files with X/Y/Z offsets and rotation
**Depends on**: Nothing (first phase)
**Requirements**: TRAN-01, TRAN-02, TRAN-03, FILE-01, FILE-03, FILE-04
**Success Criteria** (what must be TRUE):
  1. User can select an IFC file and specify output directory through the UI
  2. User can enter X/Y/Z offset values and rotation angle in form fields
  3. User can toggle "Rotate First" to control transformation order
  4. User clicks process button and transformed file appears in output directory with original filename
  5. User sees clear error messages if transformation fails (invalid file, missing values)
**Plans**: 3 plans

Plans:
- [x] 01-01-PLAN.md - Project setup and core IFC transformation model
- [x] 01-02-PLAN.md - Validation utilities and Tkinter view layer
- [x] 01-03-PLAN.md - Controller integration and working application

### Phase 2: Preset Management
**Goal**: Users can save and reuse transformation presets
**Depends on**: Phase 1 (requires working transformation UI)
**Requirements**: PRES-01, PRES-02, PRES-03, PRES-04
**Success Criteria** (what must be TRUE):
  1. User can save current transformation values as a named preset
  2. User can select a preset from dropdown and all form fields populate automatically
  3. User can delete unwanted presets from the application
  4. User reopens application and sees the last used preset already loaded
**Plans**: 2 plans

Plans:
- [x] 02-01-PLAN.md - PresetsModel and platformdirs dependency
- [x] 02-02-PLAN.md - Preset UI and controller wiring

### Phase 3: Batch Processing
**Goal**: Users can process multiple IFC files at once
**Depends on**: Phase 2 (requires presets for batch workflows)
**Requirements**: FILE-02
**Success Criteria** (what must be TRUE):
  1. User can select an input directory containing multiple IFC files
  2. User clicks process button once and all IFC files in directory are transformed with same settings
  3. User sees progress updates showing which file is currently processing and overall completion
  4. User can cancel batch processing mid-operation without corrupting files
**Plans**: 2 plans

Plans:
- [x] 03-01-PLAN.md - Validation utilities and batch mode UI components
- [x] 03-02-PLAN.md - Controller wiring with cancellation and progress tracking

### Phase 4: Distribution
**Goal**: Users can install and run without Python
**Depends on**: Phase 3 (requires feature-complete application)
**Requirements**: DIST-01
**Success Criteria** (what must be TRUE):
  1. User downloads single installer file and runs it on Windows 10 or 11
  2. User launches application from Start Menu or desktop shortcut
  3. Application runs successfully on clean Windows machine with no Python installed
  4. Application properly bundles all IfcOpenShell native dependencies (no DLL errors)
**Plans**: 2 plans

Plans:
- [x] 04-01-PLAN.md - PyInstaller spec file and Inno Setup script configuration
- [x] 04-02-PLAN.md - Windows build and installer verification (checkpoint)

## Progress

**Execution Order:**
Phases execute in numeric order: 1 -> 2 -> 3 -> 4

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Core Transformation + Basic UI | 3/3 | Complete | 2026-01-30 |
| 2. Preset Management | 2/2 | Complete | 2026-01-30 |
| 3. Batch Processing | 2/2 | Complete | 2026-01-30 |
| 4. Distribution | 2/2 | Complete | 2026-01-30 |

---
*Roadmap created: 2026-01-30*
*Last updated: 2026-01-30*
