# Feature Landscape

**Domain:** IFC Coordinate Transformation Tool (Preset-Based Batch Processing)
**Researched:** 2026-01-30
**Research Focus:** Features for UI wrapper around IfcPatch OffsetObjectPlacements

## Table Stakes

Features users expect. Missing = product feels incomplete.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Single file processing | Core use case - transform one file | Low | Direct IfcPatch wrapper |
| Batch file processing | Industry standard for utility tools | Medium | Must process multiple files sequentially |
| X/Y/Z offset inputs | Required for coordinate transformation | Low | Numeric inputs with validation |
| Rotation support | Essential for alignment (2D/3D rotation) | Medium | OffsetObjectPlacements supports ax/ay/az params |
| "Rotate first" toggle | Correct transformation order matters | Low | OffsetObjectPlacements boolean flag |
| Preset save/load | Avoid re-entering common transformations | Medium | JSON/config file storage |
| Input directory selection | Users need to pick source files | Low | Standard OS file picker |
| Output directory selection | Users need to specify destination | Low | Standard OS directory picker |
| Progress feedback | Batch operations take time, users need visibility | Medium | Per-file progress indicators |
| Error handling for invalid IFC | Not all IFCs are valid, tool must handle gracefully | Medium | Validate before processing, clear error messages |
| Success/failure reporting | Users need to know which files succeeded | Low | Summary after batch completion |
| File drag-and-drop | Non-technical users expect this interaction | Medium | Modern desktop app standard |

## Differentiators

Features that set product apart. Not expected, but valued.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Visual coordinate preview | See transformation before applying | High | Requires IFC viewer integration (e.g., xeokit, Open IFC Viewer) |
| Preset library with common offsets | Pre-populate typical survey-to-local transformations | Low | Reduces setup friction for common scenarios |
| Undo/revert capability | Safety net for incorrect transformations | Medium | Keep backup of original files or track transformation history |
| Validation warnings before processing | Prevent known pitfalls (large coords, broken geometry) | Medium | Check for coordinates >16km from origin, warn user |
| Output filename templates | Customize how transformed files are named | Low | Pattern like "{original}_transformed.ifc" |
| Side-by-side comparison view | Compare original vs transformed coordinates | High | Requires dual IFC viewer instances |
| Batch preset application | Apply different presets to different file groups | Medium | Advanced workflow for multi-building projects |
| Coordinate validation report | Document transformation applied to each file | Low | Generate CSV/log of transformations |
| Recent files/presets list | Quick access to common workflows | Low | Standard desktop app pattern |
| Auto-detect coordinate system issues | Identify files with large GIS coordinates | Medium | Heuristic analysis of coordinate magnitudes |

## Anti-Features

Features to explicitly NOT build. Common mistakes in this domain.

| Anti-Feature | Why Avoid | What to Do Instead |
|--------------|-----------|-------------------|
| In-place file editing | Extremely risky - destroys originals if transformation wrong | Always create new output files, never overwrite input |
| Built-in IFC viewer from scratch | Massive scope creep, not core value | Integrate existing open-source viewers (xeokit, Open IFC Viewer) OR defer to external viewer |
| IFC validation service | buildingSMART already provides this, duplicating effort | Link to external validation tools if needed |
| Format conversion (IFC to OBJ/DWG) | Scope creep beyond coordinate transformation | Out of scope - other tools do this (IfcToolbox, reaConverter) |
| Cloud storage integration | Adds complexity for local-first tool | Focus on local file system, defer cloud to future |
| Multi-user collaboration | Not the use case for a utility tool | Single-user desktop app is sufficient |
| IFC schema editing | Dangerous, requires deep IFC expertise | Only transform placements, never modify schema |
| Automatic coordinate detection | Unreliable - requires user knowledge of correct offsets | Require explicit user input for all transformations |
| Rotation by arbitrary axis | OffsetObjectPlacements supports this but adds UI complexity | Start with 2D rotation (Z-axis), defer 3D rotation to advanced mode |

## Feature Dependencies

```
Core Processing Flow:
  File Selection (drag-drop OR directory picker)
    ↓
  Preset Selection (saved preset OR manual input)
    ↓
  Validation Warnings (optional, checks for known issues)
    ↓
  Batch Processing (single or multiple files)
    ↓
  Progress Feedback (shows current file being processed)
    ↓
  Success/Failure Report (summary of results)

Preset Management:
  Manual Input Fields (X/Y/Z, rotation, rotate-first flag)
    ↓
  Save Preset (stores to config file)
    ↓
  Load Preset (populates input fields)

Advanced Features (post-MVP):
  Visual Preview → Requires IFC Viewer Integration
  Coordinate Validation → Requires IFC file analysis
  Undo/Revert → Requires backup file management
```

## MVP Recommendation

For MVP, prioritize:

1. **Single file processing** - Core value, low complexity
2. **Batch file processing** - Expected by target users
3. **Preset save/load** - High value/complexity ratio
4. **Drag-and-drop** - Modern UX expectation
5. **Progress feedback** - Essential for batch operations
6. **Error handling** - Prevent bad user experiences
7. **Basic validation warnings** - Check for large coordinates (>16km) before processing

Defer to post-MVP:

- **Visual coordinate preview**: High complexity, requires IFC viewer integration. Validate MVP usefulness first
- **Undo/revert**: Medium complexity, can work around with "don't overwrite originals" policy
- **Side-by-side comparison**: High complexity, low ROI for initial release
- **Auto-detect coordinate issues**: Medium complexity, unreliable without domain expertise
- **Advanced 3D rotation**: Medium complexity, 2D rotation covers 80% of use cases

## Feature Sizing for Roadmap

| Feature Category | Estimated Complexity | Priority | Phase Recommendation |
|------------------|---------------------|----------|---------------------|
| Core transformation | Low | Critical | Phase 1 |
| Preset management | Medium | Critical | Phase 1 |
| Batch processing | Medium | Critical | Phase 1 |
| Drag-and-drop | Low-Medium | High | Phase 1 |
| Progress/error handling | Medium | High | Phase 1 |
| Validation warnings | Medium | Medium | Phase 2 |
| Visual preview | High | Low | Phase 3+ (or never) |
| Undo/revert | Medium | Low | Phase 2-3 |
| Advanced features | Variable | Low | Post-MVP evaluation |

## Common User Workflows

Based on research, these are the expected workflows:

### Workflow 1: Single Survey-to-Local Transformation
1. User receives IFC from surveyor with large GIS coordinates
2. Drags file into tool
3. Enters known offset values (X: -128900, Y: -1532260, Z: 0)
4. Saves preset as "Site A - Survey to Local"
5. Processes file
6. Receives transformed file ready for Revit/coordination

### Workflow 2: Batch Processing Multiple Buildings
1. User has 10 IFC files from same project, all need same transformation
2. Selects input directory
3. Loads preset "Site A - Survey to Local"
4. Processes all files in batch
5. Reviews success/failure report
6. Outputs go to designated output directory

### Workflow 3: Rotation and Translation
1. User has IFC rotated incorrectly
2. Enters rotation angle (90 degrees)
3. Checks "rotate first" flag (order matters for correct placement)
4. Adds offset values
5. Processes file
6. Validates in external viewer

## Validation Rules (Prevent Known Pitfalls)

Based on research into common IFC coordinate mistakes:

| Validation | Rule | Why | Action |
|------------|------|-----|--------|
| Large coordinates | Warn if input file has coords >16km from origin | Triggers rounding issues, viewer problems | Show warning, suggest transformation |
| Zero transformation | Warn if all offsets = 0 and rotation = 0 | User likely forgot to enter values | Prompt confirmation |
| Extreme rotation | Warn if rotation >360 or <-360 degrees | Likely input error | Prompt correction |
| Missing output directory | Block processing if output dir not set | Would fail during processing | Force selection before processing |
| Output = Input directory | Warn if output directory same as input | Risk of confusion/overwriting | Suggest different directory |
| Non-IFC files | Skip non-.ifc files in batch | Not processable by IfcPatch | Report skipped files in summary |

## Confidence Assessment

| Feature Category | Confidence | Source Basis |
|------------------|------------|--------------|
| Core transformations | HIGH | Official IfcPatch documentation, verified parameters |
| Batch processing patterns | MEDIUM | Industry standards from multiple tools (IfcToolbox, reaConverter, RTV Xporter) |
| Preset management | MEDIUM | Common pattern across tools, no IFC-specific documentation |
| Validation rules | HIGH | Multiple sources documenting coordinate pitfalls (buildingSMART, ThinkMoult, BibLus) |
| User workflows | MEDIUM | Inferred from problem descriptions in forums and documentation |
| Differentiator value | LOW | No user research conducted, based on competitive analysis only |

## Sources

**IFC Coordinate Transformation:**
- [IfcPatch OffsetObjectPlacements Documentation](https://docs.ifcopenshell.org/autoapi/ifcpatch/recipes/OffsetObjectPlacements/index.html) - HIGH confidence
- [IFC Coordinate Reference Systems and Revit](https://thinkmoult.com/ifc-coordinate-reference-systems-and-revit.html) - MEDIUM confidence
- [IFC coordinate system - BibLus](https://biblus.accasoftware.com/en/ifc-coordinate-system/) - MEDIUM confidence
- [Linking IFC to Revit 2026](https://bimcorner.com/linking-ifc-to-revit-2026/) - MEDIUM confidence

**Common Pitfalls:**
- [Common Issues in IFC File Editing](https://biblus.accasoftware.com/en/common-issues-in-ifc-file-editing-and-how-to-address-them/) - MEDIUM confidence
- [How to troubleshoot misaligned IFC coordinate systems](https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/How-to-troubleshoot-misaligned-IFC-coordinate-systems-in-BIM-360-Model-Coordination.html) - MEDIUM confidence
- [10 Common IFC Export Mistakes to avoid](https://bimcorner.com/10-common-ifc-export-mistakes-to-avoid-part-2/) - MEDIUM confidence

**Batch Processing Tools:**
- [IFC Toolbox](https://github.com/youshengCode/IfcToolbox) - MEDIUM confidence
- [RTV Xporter](https://www.rtvtools.com/rtv-xporter/) - MEDIUM confidence
- [reaConverter Batch IFC Converter](https://www.reaconverter.com/convert/ifc.html) - LOW confidence

**IFC Validation:**
- [IFC Validation Service - buildingSMART](https://www.buildingsmart.org/users/services/validation-service/) - HIGH confidence
- [IFC Validation Tools for BIM Projects](https://bimheroes.com/ifc-validation-tools-for-bim-projects/) - MEDIUM confidence

**UI Patterns:**
- [Drag and Drop File Organizer - DropIt](https://pendriveapps.com/dropit-drag-and-drop-file-organizer/) - LOW confidence
- [QGIS Batch Processing Interface](https://docs.qgis.org/3.40/en/docs/user_manual/processing/batch.html) - MEDIUM confidence

**IFC Viewers (for preview features):**
- [xeokit-bim-viewer](https://xeokit.github.io/xeokit-bim-viewer/) - MEDIUM confidence
- [Open IFC Viewer](https://openifcviewer.com/) - MEDIUM confidence
- [ALLPLAN 2026 Model Viewer](https://architosh.com/2025/10/allplan-2026-new-allplan-model-viewer-ai-ifc4-and-more/) - MEDIUM confidence
