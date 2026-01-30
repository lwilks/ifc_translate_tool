# Architecture Patterns

**Domain:** Python Desktop Application - IFC File Processing Tool
**Researched:** 2026-01-30
**Confidence:** HIGH

## Recommended Architecture

**Pattern:** Model-View-Controller (MVC) with Service Layer

```
┌──────────────────────────────────────────────────────────┐
│                      View Layer                          │
│  (Tkinter GUI - Forms, Buttons, File Dialogs)           │
└──────────────────────┬───────────────────────────────────┘
                       │
                       │ User Events
                       │
┌──────────────────────▼───────────────────────────────────┐
│                  Controller Layer                        │
│  (Event Handlers, Form Validation, Workflow Control)    │
└──────────────────────┬───────────────────────────────────┘
                       │
                       │ Business Logic Calls
                       │
┌──────────────────────▼───────────────────────────────────┐
│                   Service Layer                          │
│  (PresetManager, FileProcessor, IfcPatchWrapper)        │
└──────────────────────┬───────────────────────────────────┘
                       │
                       │ Data Operations
                       │
┌──────────────────────▼───────────────────────────────────┐
│                    Model Layer                           │
│  (TransformSettings, Preset, ProcessingResult)          │
└──────────────────────────────────────────────────────────┘
```

### Component Boundaries

| Component | Responsibility | Communicates With |
|-----------|---------------|-------------------|
| **View** | Display UI, capture user input, show results/errors | Controller only |
| **Controller** | Handle events, validate input, coordinate workflow | View (receives events), Service (calls operations) |
| **Service** | Business logic, file operations, preset management | Controller (receives calls), Model (CRUD operations), External libraries (IfcPatch) |
| **Model** | Data structures, validation, serialization | Service layer only |
| **IfcPatchWrapper** | Isolate external library, provide typed interface | Service layer only |

### Data Flow

**1. User Input to Transformation:**
```
User fills form → View captures values → Controller validates →
Service.FileProcessor.process() → IfcPatchWrapper.execute() →
IfcPatch library → Output file written → Result returned to View
```

**2. Preset Save Flow:**
```
User enters values → User clicks "Save Preset" → Controller validates →
Service.PresetManager.save() → Model.Preset serialized to JSON →
File written to disk → Success message to View
```

**3. Preset Load Flow:**
```
User selects preset → Controller reads selection →
Service.PresetManager.load() → JSON deserialized to Model.Preset →
Controller populates View fields
```

**4. Batch Processing Flow:**
```
User selects input directory → User clicks "Process Batch" →
Controller validates settings → Service.FileProcessor.process_batch() →
For each .ifc file: IfcPatchWrapper.execute() →
Progress updates sent to View → Results summary displayed
```

## Patterns to Follow

### Pattern 1: MVC with OOP Structure
**What:** Organize application using class-based MVC pattern where each component is a Python class.

**When:** Building maintainable GUI applications with complex workflows.

**Example:**
```python
# model.py
class TransformSettings:
    """Data model for transformation parameters."""
    def __init__(self, x=0, y=0, z=0, rotate_first=True,
                 ax=None, ay=None, az=None):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
        self.rotate_first = bool(rotate_first)
        self.ax = float(ax) if ax is not None else None
        self.ay = float(ay) if ay is not None else None
        self.az = float(az) if az is not None else None

    def to_dict(self):
        """Serialize for preset storage."""
        return {
            'x': self.x, 'y': self.y, 'z': self.z,
            'rotate_first': self.rotate_first,
            'ax': self.ax, 'ay': self.ay, 'az': self.az
        }

    @classmethod
    def from_dict(cls, data):
        """Deserialize from preset storage."""
        return cls(**data)

# service.py
class IfcPatchWrapper:
    """Wrapper around IfcPatch library for type safety and error handling."""

    @staticmethod
    def execute(input_path, output_path, settings: TransformSettings):
        """Execute IfcPatch transformation with typed settings."""
        import ifcopenshell
        import ifcpatch

        try:
            # Build arguments array from settings
            args = [settings.x, settings.y, settings.z]
            if settings.ax is not None:
                args.extend([settings.rotate_first, settings.ax])
                if settings.ay is not None and settings.az is not None:
                    args.extend([settings.ay, settings.az])

            # Execute transformation
            output = ifcpatch.execute({
                "input": input_path,
                "file": ifcopenshell.open(input_path),
                "recipe": "OffsetObjectPlacements",
                "arguments": args
            })

            # Write output
            ifcpatch.write(output, output_path)
            return True, None

        except Exception as e:
            return False, str(e)

# controller.py
class MainController:
    """Coordinates between view and services."""

    def __init__(self, view, preset_manager, file_processor):
        self.view = view
        self.preset_manager = preset_manager
        self.file_processor = file_processor

        # Wire up event handlers
        self.view.on_process_clicked = self.handle_process
        self.view.on_save_preset_clicked = self.handle_save_preset

    def handle_process(self):
        """Handle process button click."""
        # Validate input
        if not self.view.validate_input():
            return

        # Get settings from view
        settings = self.view.get_settings()

        # Process file
        success, error = self.file_processor.process_single(
            self.view.input_file,
            self.view.output_directory,
            settings
        )

        # Update view
        if success:
            self.view.show_success("File processed successfully")
        else:
            self.view.show_error(f"Processing failed: {error}")

# view.py
class MainWindow(tk.Tk):
    """Main application window (View)."""

    def __init__(self):
        super().__init__()
        self.title("IFC Coordinate Transform Tool")

        # Build UI
        self._build_ui()

        # Event handlers (set by controller)
        self.on_process_clicked = None
        self.on_save_preset_clicked = None

    def _build_ui(self):
        """Build form UI components."""
        # File selection frame
        self.file_frame = tk.Frame(self)
        # Transform settings frame
        self.settings_frame = tk.Frame(self)
        # Buttons
        self.process_btn = tk.Button(
            self,
            text="Process",
            command=self._on_process_btn
        )

    def _on_process_btn(self):
        """Internal handler that calls controller."""
        if self.on_process_clicked:
            self.on_process_clicked()

    def get_settings(self) -> TransformSettings:
        """Extract settings from form fields."""
        return TransformSettings(
            x=self.x_entry.get(),
            y=self.y_entry.get(),
            z=self.z_entry.get(),
            rotate_first=self.rotate_first_var.get()
        )

# main.py
if __name__ == "__main__":
    # Initialize components
    view = MainWindow()
    preset_manager = PresetManager("presets.json")
    file_processor = FileProcessor(IfcPatchWrapper())
    controller = MainController(view, preset_manager, file_processor)

    # Start application
    view.mainloop()
```

**Why this pattern:** Separates concerns cleanly. View knows nothing about IfcPatch. Service layer can be tested independently. Controller coordinates without business logic.

### Pattern 2: Service Layer Isolation
**What:** Wrap external library (IfcPatch) in a thin service class that provides type-safe interface and error handling.

**When:** Integrating external libraries into application architecture.

**Why:**
- Isolates external dependency (easier to mock in tests)
- Provides typed interface (settings object vs raw arguments)
- Centralizes error handling for IfcPatch operations
- Makes it easier to swap libraries later if needed

### Pattern 3: JSON Configuration with Typed Models
**What:** Store presets as JSON files, but deserialize to typed Python classes (Pydantic or dataclasses) for validation and type safety.

**When:** Managing user configuration that needs persistence and validation.

**Example using dataclasses:**
```python
from dataclasses import dataclass, asdict
import json

@dataclass
class Preset:
    name: str
    settings: TransformSettings
    created: str
    description: str = ""

    def to_json(self):
        return json.dumps({
            'name': self.name,
            'settings': self.settings.to_dict(),
            'created': self.created,
            'description': self.description
        }, indent=2)

    @classmethod
    def from_json(cls, json_str):
        data = json.loads(json_str)
        data['settings'] = TransformSettings.from_dict(data['settings'])
        return cls(**data)

class PresetManager:
    def __init__(self, presets_file):
        self.presets_file = presets_file
        self.presets = self._load_presets()

    def save_preset(self, preset: Preset):
        """Save with validation."""
        self.presets[preset.name] = preset
        self._write_presets()

    def load_preset(self, name: str) -> Preset:
        """Load with type safety."""
        return self.presets.get(name)
```

**Why:** Type safety prevents runtime errors. Validation catches bad data early. Dataclasses provide free serialization.

### Pattern 4: Batch Processing with Progress Feedback
**What:** Process multiple files sequentially with progress updates to GUI.

**When:** Batch processing operations that take time.

**Example:**
```python
class FileProcessor:
    def process_batch(self, input_dir, output_dir, settings,
                     progress_callback=None):
        """Process all .ifc files in directory."""
        ifc_files = [f for f in os.listdir(input_dir)
                     if f.lower().endswith('.ifc')]
        total = len(ifc_files)
        results = []

        for i, filename in enumerate(ifc_files, 1):
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, filename)

            success, error = self.wrapper.execute(
                input_path, output_path, settings
            )

            results.append({
                'file': filename,
                'success': success,
                'error': error
            })

            # Update progress
            if progress_callback:
                progress_callback(i, total, filename)

        return results

# In controller:
def handle_batch_process(self):
    def update_progress(current, total, filename):
        self.view.update_progress_bar(current / total)
        self.view.update_status(f"Processing {filename}...")

    results = self.file_processor.process_batch(
        input_dir, output_dir, settings, update_progress
    )

    self.view.show_results_summary(results)
```

**Why:** User gets feedback during long operations. Prevents GUI freeze. Clear communication of progress and errors.

## Anti-Patterns to Avoid

### Anti-Pattern 1: Mixing Business Logic in View
**What:** Putting IfcPatch calls, file operations, or preset management directly in Tkinter event handlers.

**Why bad:**
- Impossible to test without GUI
- Violates separation of concerns
- Makes code harder to maintain
- Prevents reuse of logic

**Instead:** Keep view methods focused on UI state only. Delegate all logic to controller/service.

**Example of what NOT to do:**
```python
# BAD - Don't do this
class MainWindow(tk.Tk):
    def on_process_clicked(self):
        # Directly accessing IfcPatch in view - BAD!
        import ifcopenshell
        import ifcpatch

        output = ifcpatch.execute({
            "input": self.input_file.get(),
            "recipe": "OffsetObjectPlacements",
            "arguments": [self.x_var.get(), self.y_var.get()]
        })
        # This is untestable and tightly coupled
```

### Anti-Pattern 2: Global Variables for State
**What:** Using module-level globals to share state between components.

**Why bad:**
- Makes testing difficult (global state persists)
- Hidden dependencies between modules
- Race conditions in future threading scenarios
- Unclear ownership of data

**Instead:** Use instance variables within classes, pass dependencies through constructors.

### Anti-Pattern 3: Mixing grid() and pack() Layout Managers
**What:** Using both `.grid()` and `.pack()` in the same container/frame.

**Why bad:** Tkinter cannot handle mixed geometry managers in same container. Leads to layout errors and unexpected behavior.

**Instead:** Choose one layout manager per container. Use grid() for form layouts (recommended for this app). Nest frames if different layouts needed in different sections.

```python
# GOOD - Consistent layout manager
class MainWindow(tk.Tk):
    def _build_ui(self):
        # Use grid throughout main window
        self.settings_frame = tk.Frame(self)
        self.settings_frame.grid(row=0, column=0, sticky="nsew")

        # Within settings frame, also use grid
        tk.Label(self.settings_frame, text="X:").grid(row=0, column=0)
        self.x_entry = tk.Entry(self.settings_frame)
        self.x_entry.grid(row=0, column=1)
```

### Anti-Pattern 4: Wildcard Imports
**What:** Using `from tkinter import *` or `from ifcopenshell import *`.

**Why bad:**
- Namespace pollution
- Hard to track where functions/classes come from
- Name collisions possible
- Makes code harder to understand

**Instead:** Use explicit imports: `import tkinter as tk` or `from tkinter import ttk`.

### Anti-Pattern 5: PyInstaller --onefile for Large Dependencies
**What:** Using `--onefile` mode when bundling with IfcOpenShell (large library).

**Why bad:**
- Slow startup (unpacks to temp every launch)
- Antivirus may flag temporary extraction
- Harder to debug issues
- No access to inspect bundled dependencies

**Instead:** Use `--onedir` mode and distribute as a ZIP or create installer with NSIS/Inno Setup.

```bash
# GOOD - Create directory bundle
pyinstaller --onedir --windowed main.py

# Then create installer with NSIS/InnoSetup
# Or distribute as .zip file
```

### Anti-Pattern 6: No Error Boundaries Around External Library
**What:** Calling IfcPatch directly without try/except error handling.

**Why bad:**
- Uncaught exceptions crash entire GUI
- No user-friendly error messages
- Cannot distinguish error types (file not found vs invalid IFC vs library bug)

**Instead:** Wrap all external library calls in service layer with comprehensive error handling.

```python
# GOOD - Error boundary in service layer
class IfcPatchWrapper:
    @staticmethod
    def execute(input_path, output_path, settings):
        try:
            # Validation before calling library
            if not os.path.exists(input_path):
                return False, f"Input file not found: {input_path}"

            if not input_path.lower().endswith('.ifc'):
                return False, "Input file must be .ifc format"

            # Call library with error handling
            output = ifcpatch.execute({...})
            ifcpatch.write(output, output_path)
            return True, None

        except ifcopenshell.Error as e:
            return False, f"IFC library error: {str(e)}"
        except IOError as e:
            return False, f"File operation error: {str(e)}"
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"
```

## Directory Structure

Recommended project structure for maintainability and PyInstaller compatibility:

```
ifc_translate_tool/
├── main.py                    # Application entry point
├── app/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── transform_settings.py
│   │   └── preset.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ifcpatch_wrapper.py
│   │   ├── preset_manager.py
│   │   └── file_processor.py
│   ├── controllers/
│   │   ├── __init__.py
│   │   └── main_controller.py
│   └── views/
│       ├── __init__.py
│       ├── main_window.py
│       └── widgets/          # Reusable custom widgets
│           ├── __init__.py
│           └── preset_selector.py
├── resources/                # Icons, images (if any)
├── presets/                  # Default preset storage location
├── tests/
│   ├── test_models.py
│   ├── test_services.py
│   └── test_controllers.py
├── requirements.txt
├── pyinstaller.spec         # PyInstaller configuration
└── README.md
```

**Why this structure:**
- Clear separation of concerns (MVC layers)
- Easy to locate code by responsibility
- PyInstaller can easily find all modules
- Tests mirror source structure
- Services layer is independently testable

## PyInstaller Bundling Considerations

### Recommended Approach
**Use --onedir mode with installer creation:**

```python
# pyinstaller.spec
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('resources', 'resources'),      # Include resources
        ('presets/default.json', 'presets'),  # Include default presets
    ],
    hiddenimports=[
        'ifcopenshell',
        'ifcopenshell.geom',
        'ifcpatch',
        'ifcpatch.recipes.OffsetObjectPlacements',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='IFC Transform Tool',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Windowed app
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='resources/icon.ico'  # Application icon
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='IFC Transform Tool'
)
```

### Build Process
```bash
# Install dependencies
pip install -r requirements.txt
pip install pyinstaller

# Build with spec file
pyinstaller pyinstaller.spec

# Output will be in dist/IFC Transform Tool/
# Create installer with NSIS or distribute as .zip
```

### Handling IfcOpenShell in Bundle
IfcOpenShell is a large library with native dependencies. Key considerations:

1. **Hidden imports:** Must explicitly list ifcopenshell modules in spec file
2. **Binary dependencies:** IfcOpenShell includes compiled C++ libraries that PyInstaller should auto-detect
3. **Testing:** Always test bundled .exe on clean Windows VM (no Python installed)
4. **Size:** Expect 200-400MB bundle size due to IfcOpenShell

### Resource File Access in Bundled App
When running as bundled executable, use this pattern to access resources:

```python
import sys
import os

def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and bundled app."""
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# Usage:
icon_path = get_resource_path('resources/icon.png')
default_presets = get_resource_path('presets/default.json')
```

## Build Order Implications

Based on MVC architecture and dependencies, recommended build order:

### Phase 1: Core Models & Services
**Build first:** Independent, no GUI dependencies, fully testable
- `models/transform_settings.py` - Data model for transformation parameters
- `models/preset.py` - Data model for saved presets
- `services/ifcpatch_wrapper.py` - Wrapper around IfcPatch library
- Basic error handling and validation

**Why first:** Establishes data contracts. Can be tested without GUI. Service layer can be validated against real IfcPatch library early.

### Phase 2: Service Layer Completion
**Build second:** Business logic, depends on models
- `services/preset_manager.py` - Load/save presets to JSON
- `services/file_processor.py` - Single and batch file processing
- Comprehensive error handling for file operations

**Why second:** Services can be tested independently with mock data. Validates entire business logic before GUI complexity.

### Phase 3: Minimal View
**Build third:** Basic GUI to test service integration
- `views/main_window.py` - Basic form layout with grid geometry
- Form fields for X, Y, Z, rotation settings
- File selection dialogs
- Process button
- No controller yet - hardcode test values

**Why third:** Validates GUI framework choice (Tkinter). Tests that form capture works. Visual feedback before wiring complexity.

### Phase 4: Controller & Integration
**Build fourth:** Wire view to services via controller
- `controllers/main_controller.py` - Event handlers and workflow coordination
- Connect view events to service calls
- Error display in GUI
- Success/failure feedback

**Why fourth:** Now that view and services are validated separately, integration is lower risk. Controller is mostly coordination code.

### Phase 5: Preset Management UI
**Build fifth:** Depends on preset service and base UI
- Preset dropdown/selector widget
- Save preset dialog
- Load preset functionality
- Preset list management

**Why fifth:** Builds on proven foundation. Preset UI is value-add but not core workflow.

### Phase 6: Batch Processing UI
**Build sixth:** Depends on file processor service and base UI
- Directory selection dialogs
- Batch process button
- Progress bar/status updates
- Results summary display

**Why sixth:** Most complex UI workflow. Benefits from all prior components being stable.

### Phase 7: Bundling & Distribution
**Build last:** Depends on complete, tested application
- Create pyinstaller.spec
- Test bundled executable
- Create installer (optional)
- Windows compatibility testing

**Why last:** Only bundle once application is feature-complete and tested. Bundling is iteration-heavy (find missing imports, test on clean system).

## Testing Strategy by Layer

| Layer | Testing Approach | Example |
|-------|------------------|---------|
| **Models** | Unit tests, property validation | Test TransformSettings.from_dict() with invalid data |
| **Services** | Unit tests with mocks, integration tests with real IfcPatch | Mock IfcPatch for unit tests, use real library for integration |
| **Controllers** | Unit tests with mock view and services | Test handle_process() with mock file_processor |
| **Views** | Manual testing (GUI hard to unit test) | Smoke test: click all buttons, enter invalid data |
| **Integration** | End-to-end manual testing | Full workflow: load preset → process file → verify output |

## Scalability Considerations

This application is single-user, local-only desktop tool. Scalability is not a concern, but future extension points:

| Concern | Current Architecture | If Scaling to Multi-User |
|---------|---------------------|--------------------------|
| **File locking** | Not needed (single user) | Add file lock checks before processing |
| **Concurrent processing** | Sequential batch processing | Add threading with queue (Tkinter requires main thread for UI updates) |
| **Preset storage** | JSON file per preset | Move to SQLite database |
| **Distributed processing** | Not applicable | Would require architecture redesign (web service + API) |

## Sources

### High Confidence (Official Documentation & Authoritative Sources)
- [IfcOpenShell OffsetObjectPlacements Documentation](https://docs.ifcopenshell.org/autoapi/ifcpatch/recipes/OffsetObjectPlacements/index.html) - Official API documentation
- [IfcPatch API Documentation](https://docs.ifcopenshell.org/autoapi/ifcpatch/index.html) - Official usage patterns
- [PyInstaller Official Documentation](https://pyinstaller.org/en/stable/operating-mode.html) - Bundling best practices
- [Python Official Tkinter Documentation](https://docs.python.org/3/library/tkinter.html) - Standard library reference
- [Real Python PyInstaller Tutorial](https://realpython.com/pyinstaller-python/) - Practical bundling guide
- [Machinet PyInstaller Best Practices](https://www.machinet.net/tutorial-eng/best-practices-for-pyinstaller-in-python-projects) - Security and build recommendations

### Medium Confidence (Community Best Practices, Multiple Sources Agreeing)
- [Python GUI Framework Comparison 2026](https://www.pythonguis.com/faq/which-python-gui-library/) - Framework selection rationale
- [Tkinter MVC Pattern Tutorial](https://www.pythontutorial.net/tkinter/tkinter-mvc/) - Architecture pattern implementation
- [Medium: MVC for Tkinter Multi-Frame Apps](https://nazmul-ahsan.medium.com/how-to-organize-multi-frame-tkinter-application-with-mvc-pattern-79247efbb02b) - Structure guidance
- [Tkinter Best Practices](https://medium.com/tomtalkspython/tkinter-best-practices-optimizing-performance-and-code-structure-c49d1919fbb4) - Code organization
- [Python Configuration Files Best Practices](https://tech.preferred.jp/en/blog/working-with-configuration-in-python/) - JSON/config patterns
- [Code-B.dev Desktop App Guide 2025](https://code-b.dev/blog/building-desktop-applications-using-python) - Current practices
- [Hitchhiker's Guide to Python - Freezing Code](https://docs.python-guide.org/shipping/freezing/) - Bundling overview

### Context
- Project requirements from PROJECT.md
- IfcPatch issue discussions on GitHub (Issue #2026, #2007)
