# Requirements: IFC Coordinate Transform Tool

**Defined:** 2025-01-30
**Core Value:** Users can transform IFC coordinates reliably with saved presets, processing single or multiple files without technical knowledge.

## v1 Requirements

Requirements for initial release. Each maps to roadmap phases.

### Transformation

- [ ] **TRAN-01**: Apply X/Y/Z coordinate offsets to IFC file using IfcPatch OffsetObjectPlacements recipe
- [ ] **TRAN-02**: Apply rotation values to IFC file
- [ ] **TRAN-03**: Toggle "Rotate First" to control operation order (rotate then translate, or translate then rotate)

### File Handling

- [ ] **FILE-01**: Select and process single IFC file
- [ ] **FILE-02**: Batch process multiple IFC files from input directory
- [ ] **FILE-03**: Configure output directory for processed files
- [ ] **FILE-04**: Output files retain original filename in output directory

### Preset Management

- [ ] **PRES-01**: Save current transformation values as named preset
- [ ] **PRES-02**: Load saved preset to populate form fields
- [ ] **PRES-03**: Delete saved presets
- [ ] **PRES-04**: Auto-load last used preset on application startup

### Distribution

- [ ] **DIST-01**: Run as standalone Windows executable (no Python installation required)

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

### User Experience

- **UX-01**: Drag-and-drop file/folder support
- **UX-02**: Progress indication during batch processing
- **UX-03**: Cancel long-running operations

### Validation

- **VAL-01**: Warning for extreme coordinate values (>16km can break geometry)
- **VAL-02**: Warning for zero transformation (user may have forgotten to set values)

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| macOS/Linux support | Client environment is Windows-only |
| Other IfcPatch recipes | Scoped to OffsetObjectPlacements for this client's need |
| IFC file preview/3D viewer | Adds significant complexity, use external viewer if needed |
| In-place file editing | Safety — always output to separate directory to preserve originals |
| Cloud/web deployment | Client needs desktop app with local file access |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| TRAN-01 | TBD | Pending |
| TRAN-02 | TBD | Pending |
| TRAN-03 | TBD | Pending |
| FILE-01 | TBD | Pending |
| FILE-02 | TBD | Pending |
| FILE-03 | TBD | Pending |
| FILE-04 | TBD | Pending |
| PRES-01 | TBD | Pending |
| PRES-02 | TBD | Pending |
| PRES-03 | TBD | Pending |
| PRES-04 | TBD | Pending |
| DIST-01 | TBD | Pending |

**Coverage:**
- v1 requirements: 12 total
- Mapped to phases: 0
- Unmapped: 12 (pending roadmap creation)

---
*Requirements defined: 2025-01-30*
*Last updated: 2025-01-30 after initial definition*
