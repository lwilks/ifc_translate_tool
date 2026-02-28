# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

IFC Translate Tool is a standalone Windows desktop application that wraps IfcPatch's `OffsetObjectPlacements` recipe. It transforms IFC file coordinates (translation + rotation) for non-technical BIM users. v1.0 is feature-complete.

**Tech stack:** Python 3.12, Tkinter, ifcopenshell/ifcpatch 0.7.10, platformdirs, PyInstaller, Inno Setup.

## Commands

```bash
# Run the application (from project root)
python src/main.py

# Build Windows executable (--onedir mode, UPX disabled)
pyinstaller ifc_translate.spec

# Build Windows installer (requires Inno Setup 6.x, run from installer/)
iscc setup.iss

# Install dependencies
pip install -r requirements.txt          # runtime only
pip install -r requirements-dev.txt      # includes pyinstaller
```

There are no tests, linter, or formatter configured in this project.

## Architecture

MVC pattern with four main modules in `src/`:

- **`main.py`** - Entry point. Creates Tk root, instantiates Model/View/PresetsModel/Controller, starts mainloop.
- **`model.py`** (`IFCTransformModel`) - Wraps ifcpatch. Single method `transform_file()` opens IFC, converts metre offsets to project units via `ifcopenshell.util.unit.calculate_unit_scale()`, calls `ifcpatch.execute()` with `OffsetObjectPlacements` recipe.
- **`view.py`** (`TransformView`) - Tkinter UI. File/directory selection, offset fields (X/Y/Z), rotation, rotate-first checkbox, preset dropdown, batch mode toggle, progress bar. Uses `pack()` layout throughout.
- **`controller.py`** (`TransformController`) - Wires model and view. Runs transformations in daemon `threading.Thread`, communicates results back via `queue.Queue` polled every 100ms with `root.after()`. Handles single-file and batch processing with `threading.Event` for cancellation.
- **`presets_model.py`** (`PresetsModel`) - JSON preset persistence in `platformdirs.user_data_dir()`. Atomic writes via temp file + rename. Tracks last-used preset for auto-load on startup.
- **`utils/validation.py`** - Path validation functions (`validate_input_file`, `validate_output_directory`, `validate_input_directory`, `find_ifc_files`, `build_output_path`).

### Data Flow

1. User fills form -> View captures values -> Controller validates via `utils/validation.py`
2. Controller starts background thread -> `model.transform_file()` -> ifcpatch executes
3. Result placed in `queue.Queue` -> Controller polls queue -> Updates View

### Key Design Decisions

- **ifcopenshell 0.7.10** pinned (0.8.x has circular import bug)
- **Unit conversion**: Offsets entered in metres, converted to project units before passing to IfcPatch (`model.py:91-94`)
- **Threading**: Transformations run in daemon threads to keep UI responsive; thread-safe communication via queue
- **Batch cancellation**: Uses `threading.Event.set()` checked between files
- **PyInstaller**: `--onedir` mode with UPX disabled to avoid DLL corruption with native extensions
