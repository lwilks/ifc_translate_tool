# IFC Translate Tool

A desktop application for transforming IFC file coordinates. Wraps [IfcPatch's OffsetObjectPlacements](https://docs.ifcopenshell.org/autoapi/ifcpatch/recipes/OffsetObjectPlacements/index.html) recipe in a simple GUI, allowing you to apply translation offsets and rotation to IFC files without needing Blender, Bonsai, or the command line.

Built for BIM workflows where IFC files arrive in survey/real-world coordinates and need shifting to local project coordinate systems.

## Features

- **Translation offsets** - Apply X, Y, Z coordinate offsets (entered in metres, automatically converted to project units)
- **Rotation** - Rotate around the Z axis with configurable operation order (rotate-first or translate-first)
- **Batch processing** - Process an entire directory of IFC files at once with progress tracking and cancellation
- **Presets** - Save, load, and delete transformation presets; last-used preset auto-loads on startup
- **Windows installer** - Distributable as a standalone Windows executable (no Python required)

## Installation

### Download (Windows)

Download the latest installer from [Releases](../../releases) and run `IFC_Translate_Tool_Setup.exe`.

### Run from source

Requires Python 3.9+.

```bash
git clone https://github.com/lwilks/ifc_translate_tool.git
cd ifc_translate_tool

python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

pip install -r requirements.txt
python src/main.py
```

## Usage

1. Select an input IFC file (single mode) or input directory (batch mode)
2. Select an output directory
3. Enter translation offsets in metres (X, Y, Z)
4. Optionally enter a rotation angle in degrees and choose whether to rotate before or after translating
5. Click **Process**

Output files keep their original filenames and are written to the output directory.

### Presets

Save frequently used transformation values as named presets using the **Save** button. Select a preset from the dropdown to load its values. The last-used preset is automatically restored when the application starts.

## Building

### Windows executable

```bash
pip install -r requirements-dev.txt
pyinstaller ifc_translate.spec
```

Output: `dist/IFC Translate Tool/`

### Windows installer

Requires [Inno Setup 6.x](https://jrsoftware.org/isinfo.php). Build the executable first, then:

```bash
cd installer
iscc setup.iss
```

Output: `installer/Output/IFC_Translate_Tool_Setup.exe`

## Dependencies

- [ifcopenshell](https://ifcopenshell.org/) / [ifcpatch](https://docs.ifcopenshell.org/autoapi/ifcpatch/index.html) 0.7.10 (LGPL-3.0) - IFC file processing and transformation
- [platformdirs](https://github.com/tox-dev/platformdirs) - Cross-platform user data directory for preset storage
- [PyInstaller](https://pyinstaller.org/) - Executable bundling (dev dependency)

## License

[MIT](LICENSE)

This project uses [IfcOpenShell](https://ifcopenshell.org/) and [IfcPatch](https://docs.ifcopenshell.org/autoapi/ifcpatch/index.html), which are licensed under LGPL-3.0-or-later.
