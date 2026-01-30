# Phase 1: Core Transformation + Basic UI - Research

**Researched:** 2026-01-30
**Domain:** IFC file transformation with Python + Desktop GUI
**Confidence:** HIGH

## Summary

This phase requires building a desktop application that applies geometric transformations (offset and rotation) to IFC files using IfcOpenShell's IfcPatch library. The research covered the IFC transformation domain, Python desktop GUI frameworks, file handling patterns, and error handling strategies.

**Core Technology Stack:** The standard approach is to use IfcOpenShell/IfcPatch (v0.8.4+) for IFC transformations with Python 3.9-3.14. For the desktop GUI, Tkinter is the recommended choice due to its inclusion in Python's standard library, zero installation overhead, and sufficient capabilities for file pickers, forms, and basic error messaging.

**Critical Finding:** The `should_rotate_first` parameter in OffsetObjectPlacements is essential because rotation and translation do not commute mathematically. Rotating first then translating produces different results than translating first then rotating. This directly maps to the TRAN-03 requirement.

**Primary recommendation:** Use IfcOpenShell 0.8.4+ with IfcPatch's OffsetObjectPlacements recipe via Python library API (not CLI), Tkinter for desktop GUI with MVC pattern, pathlib for file path handling, and threading for UI responsiveness during file processing.

## Standard Stack

The established libraries/tools for this domain:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| ifcopenshell | 0.8.4+ | IFC file I/O and manipulation | Industry standard open-source IFC toolkit, actively maintained, supports Python 3.9-3.14 |
| ifcpatch | 0.8.4+ | Predefined IFC transformation recipes | Built into ifcopenshell, provides standardized transformations including OffsetObjectPlacements |
| tkinter | stdlib | Desktop GUI framework | Included with Python, cross-platform, native file dialogs, sufficient for forms and file selection |
| pathlib | stdlib | File path handling | Modern Python standard for cross-platform path operations |
| threading | stdlib | Background processing | Keeps UI responsive during file transformations |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| logging | stdlib | Error and operation logging | All file operations and transformations (always) |
| json | stdlib | Configuration or error reporting | If structured error output needed |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| tkinter | PyQt6/PySide6 | PyQt offers more features but requires separate installation, commercial licensing concerns, steeper learning curve. Only justified for complex UIs with multimedia or advanced widgets |
| tkinter | Kivy | Mobile-focused, non-native look on desktop, overkill for file picker + form interface |
| IfcPatch library API | IfcPatch CLI | CLI requires subprocess management, harder error handling, no programmatic control. Library API is recommended |

**Installation:**
```bash
pip install ifcopenshell
# tkinter, pathlib, threading, logging are in Python stdlib - no installation needed
```

## Architecture Patterns

### Recommended Project Structure
```
ifc_translate_tool/
├── src/
│   ├── main.py              # Entry point, creates controller
│   ├── model.py             # IFC transformation logic (IfcPatch wrapper)
│   ├── view.py              # Tkinter UI components
│   ├── controller.py        # Connects view to model, handles events
│   └── utils/
│       ├── validation.py    # Path and input validation
│       └── errors.py        # Custom exception classes
├── tests/
│   ├── test_model.py
│   └── test_validation.py
└── requirements.txt
```

### Pattern 1: MVC (Model-View-Controller) for Tkinter Desktop Apps
**What:** Separates transformation logic (Model), UI components (View), and user interaction handling (Controller)

**When to use:** Desktop applications with forms and file processing (this phase)

**Example:**
```python
# model.py - Transformation logic
import ifcopenshell
import ifcpatch

class IFCTransformModel:
    def transform_file(self, input_path, output_path, x, y, z,
                      should_rotate_first, rotation_angle=None):
        """Apply transformation using IfcPatch OffsetObjectPlacements."""
        try:
            # Open IFC file with path (not file object) to capture C++ parse errors
            ifc_file = ifcopenshell.open(input_path)

            # Build arguments for OffsetObjectPlacements
            arguments = [x, y, z, should_rotate_first]
            if rotation_angle is not None:
                arguments.append(rotation_angle)

            # Execute transformation
            output = ifcpatch.execute({
                "input": str(input_path),
                "file": ifc_file,
                "recipe": "OffsetObjectPlacements",
                "arguments": arguments,
            })

            # Write output
            ifcpatch.write(output, str(output_path))
            return True

        except RuntimeError as e:
            # IfcOpenShell raises RuntimeError for invalid IFC files
            raise ValueError(f"Invalid IFC file: {e}")
        except Exception as e:
            raise Exception(f"Transformation failed: {e}")

# controller.py - Event handling
class TransformController:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.view.set_controller(self)

    def on_process_clicked(self):
        """Handle process button click - run transformation in background thread."""
        try:
            # Validate inputs
            self.validate_inputs()

            # Run transformation in thread to keep UI responsive
            thread = threading.Thread(target=self._run_transformation)
            thread.daemon = True
            thread.start()

        except ValueError as e:
            self.view.show_error(str(e))

    def _run_transformation(self):
        """Execute transformation in background thread."""
        try:
            self.view.show_processing()
            self.model.transform_file(...)
            self.view.show_success("Transformation complete")
        except Exception as e:
            self.view.show_error(str(e))

# view.py - Tkinter UI
import tkinter as tk
from tkinter import filedialog, messagebox

class TransformView:
    def __init__(self, root):
        self.root = root
        self.controller = None

        # File selection
        self.input_file_var = tk.StringVar()
        tk.Button(root, text="Select IFC File",
                 command=self._select_input_file).pack()

        # Offset inputs with validation
        self.x_var = tk.StringVar()
        self.x_entry = tk.Entry(root, textvariable=self.x_var,
                               validate="key",
                               validatecommand=self._float_validation)

    def _select_input_file(self):
        """Open file dialog for IFC file selection."""
        filename = filedialog.askopenfilename(
            title="Select IFC File",
            filetypes=[("IFC files", "*.ifc"), ("All files", "*.*")]
        )
        if filename:
            self.input_file_var.set(filename)

    def show_error(self, message):
        """Display error message to user."""
        messagebox.showerror("Error", message)
```

### Pattern 2: Thread-Safe UI Updates
**What:** Run file processing in background thread, update UI from main thread

**When to use:** Any long-running operation (file I/O, IFC transformations)

**Example:**
```python
import threading
import queue

class Controller:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.result_queue = queue.Queue()

        # Check queue periodically for thread results
        self.view.root.after(100, self._check_queue)

    def _check_queue(self):
        """Check for results from background thread (called from main thread)."""
        try:
            result = self.result_queue.get_nowait()
            if result['success']:
                self.view.show_success(result['message'])
            else:
                self.view.show_error(result['message'])
        except queue.Empty:
            pass
        finally:
            self.view.root.after(100, self._check_queue)

    def process_file(self):
        """Start processing in background thread."""
        thread = threading.Thread(target=self._process_in_background)
        thread.daemon = True
        thread.start()

    def _process_in_background(self):
        """Run in worker thread - put results in queue for main thread."""
        try:
            self.model.transform_file(...)
            self.result_queue.put({'success': True, 'message': 'Complete'})
        except Exception as e:
            self.result_queue.put({'success': False, 'message': str(e)})
```

### Pattern 3: File Path Validation with pathlib
**What:** Validate file paths before attempting operations

**When to use:** All file selection and directory configuration (FILE-01, FILE-03, FILE-04)

**Example:**
```python
from pathlib import Path
import os

def validate_input_file(file_path):
    """Validate input IFC file exists and is readable."""
    path = Path(file_path)

    if not file_path:
        raise ValueError("No file selected")

    if not path.exists():
        raise ValueError(f"File does not exist: {file_path}")

    if not path.is_file():
        raise ValueError(f"Path is not a file: {file_path}")

    if path.suffix.lower() != '.ifc':
        raise ValueError(f"File must be .ifc format, got: {path.suffix}")

    if not os.access(path, os.R_OK):
        raise ValueError(f"No read permission for file: {file_path}")

    return path

def validate_output_directory(dir_path):
    """Validate output directory exists and is writable."""
    path = Path(dir_path)

    if not dir_path:
        raise ValueError("No output directory selected")

    if not path.exists():
        raise ValueError(f"Directory does not exist: {dir_path}")

    if not path.is_dir():
        raise ValueError(f"Path is not a directory: {dir_path}")

    if not os.access(path, os.W_OK):
        raise ValueError(f"No write permission for directory: {dir_path}")

    return path

def build_output_path(input_path, output_dir):
    """Construct output file path preserving original filename."""
    input_file = Path(input_path)
    output_directory = Path(output_dir)

    # FILE-04 requirement: retain original filename
    output_path = output_directory / input_file.name

    return output_path
```

### Pattern 4: Float Input Validation for Tkinter Entry
**What:** Validate numeric input in real-time as user types

**When to use:** X/Y/Z offset fields, rotation angle field

**Example:**
```python
import tkinter as tk

class TransformView:
    def __init__(self, root):
        self.root = root

        # Register validation function
        float_validate = (root.register(self._validate_float), '%P')

        # Create Entry with validation
        self.x_var = tk.StringVar(value="0")
        self.x_entry = tk.Entry(
            root,
            textvariable=self.x_var,
            validate="key",
            validatecommand=float_validate
        )
        self.x_entry.pack()

    def _validate_float(self, value_if_allowed):
        """Validate that input can be parsed as float."""
        # Allow empty string (user is typing)
        if value_if_allowed == "" or value_if_allowed == "-":
            return True

        # Allow single decimal point
        if value_if_allowed.count('.') > 1:
            return False

        # Try to parse as float
        try:
            float(value_if_allowed)
            return True
        except ValueError:
            return False

    def get_offset_values(self):
        """Get validated float values from entry fields."""
        try:
            x = float(self.x_var.get() or "0")
            y = float(self.y_var.get() or "0")
            z = float(self.z_var.get() or "0")
            return x, y, z
        except ValueError as e:
            raise ValueError("Invalid numeric input for offset values")
```

### Anti-Patterns to Avoid
- **Blocking the main thread:** Never run `ifcpatch.execute()` directly in button click handler - always use threading
- **Updating UI from worker thread:** Never call Tkinter methods from background threads - use queue pattern
- **Using CLI subprocess:** Don't call `python -m ifcpatch` via subprocess when library API is available
- **Ignoring file path validation:** Always validate paths with pathlib before passing to IfcOpenShell - better error messages
- **Catching generic Exception:** Catch specific exceptions (RuntimeError for invalid IFC, OSError for file operations)

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| IFC coordinate transformations | Custom matrix math on IFC entities | IfcPatch OffsetObjectPlacements | Handles all object types correctly, accounts for IFC placement hierarchy, tested on production models |
| File path validation | String operations with os.path | pathlib.Path with .exists(), .is_file(), os.access() | Cross-platform, handles edge cases (symlinks, permissions), cleaner API |
| Float input validation | Custom regex or string parsing | Tkinter validatecommand with try/except float() | Built-in to Tkinter, real-time validation, handles edge cases (negative, decimals) |
| File dialogs | Custom file browser UI | tkinter.filedialog.askopenfilename() | Native OS dialogs, handles filters, remembers last directory, cross-platform |
| Error messages | print() or custom dialog | tkinter.messagebox + Python logging module | Standard UI pattern, logging captures errors for debugging |

**Key insight:** IFC transformations appear simple (just matrix multiplication) but the IFC placement hierarchy is complex. Some elements may have local placements, site placements, or absolute placements. IfcPatch handles all these cases correctly, while a custom implementation would likely miss edge cases and produce incorrect results for certain element types.

## Common Pitfalls

### Pitfall 1: Transformation Order Confusion (should_rotate_first parameter)
**What goes wrong:** Users expect rotation to occur around the object's center after translation, but setting `should_rotate_first=False` rotates around the global origin (0,0,0), causing objects to appear in unexpected locations.

**Why it happens:** Rotation and translation don't commute. Rotating first then translating is mathematically different from translating first then rotating. The rotation always occurs around the IFC coordinate system origin (absolute 0,0,0), not the object's center.

**How to avoid:**
- Default `should_rotate_first=True` (matches most user expectations)
- Provide clear UI labels explaining the parameter: "Apply rotation before translation"
- Document in help text: "Rotation occurs around origin (0,0,0), not object center"

**Warning signs:** User reports "object jumped to wrong location after rotation"

### Pitfall 2: Invalid IFC File Handling
**What goes wrong:** `ifcopenshell.open()` raises a generic RuntimeError with cryptic C++ error messages like "Token $ at 4529 invalid instance name". Users see unhelpful error messages.

**Why it happens:** IfcOpenShell's C++ parser detects syntax errors but the error messages are technical. Additionally, some IFC files may be corrupt or use invalid entity definitions.

**How to avoid:**
- Always wrap `ifcopenshell.open()` in try/except RuntimeError
- Provide user-friendly error messages: "The selected file is not a valid IFC file or is corrupted"
- Optionally: Pre-validate with `ifcopenshell.validate()` before transformation (trade-off: slower but better errors)
- Pass file path string to `ifcopenshell.open()` rather than file object to capture parse errors

**Warning signs:** Application crashes with RuntimeError, users complain about "technical error messages"

### Pitfall 3: Blocking UI During File Processing
**What goes wrong:** Clicking "Process" button causes the entire application to freeze until transformation completes (which can take seconds to minutes for large files). User cannot cancel or see progress.

**Why it happens:** IfcPatch operations are CPU-intensive. Running in the main thread blocks the Tkinter event loop, preventing UI updates.

**How to avoid:**
- Always run `model.transform_file()` in a background thread using `threading.Thread`
- Use queue to communicate results back to main thread
- Provide visual feedback (disable button, show "Processing..." status)
- Never call Tkinter methods from worker thread - only from main thread

**Warning signs:** UI appears frozen, "Not Responding" on Windows, spinning cursor on macOS

### Pitfall 4: File Path String vs Path Object Confusion
**What goes wrong:** Passing pathlib.Path objects to `ifcpatch.execute()` can cause type errors or unexpected behavior. Some functions expect strings, not Path objects.

**Why it happens:** IfcOpenShell predates pathlib and expects string paths. While Path objects often work due to __str__() coercion, explicit conversion is safer.

**How to avoid:**
- Always convert Path objects to strings: `str(path)` or `path.as_posix()`
- Document function signatures clearly: `def transform_file(input_path: str, ...)`
- Use pathlib for validation, convert to string for IfcOpenShell

**Warning signs:** TypeError about path arguments, inconsistent behavior across platforms

### Pitfall 5: Missing Numeric Input Validation
**What goes wrong:** User enters "abc" or "" in offset field, application crashes when trying to parse as float, or passes invalid values to IfcPatch causing cryptic errors.

**Why it happens:** Tkinter Entry widgets accept any string input by default. Empty strings and non-numeric values are valid from Tkinter's perspective.

**How to avoid:**
- Use validatecommand on Entry widgets to restrict input to valid floats
- Provide default values (e.g., "0") so fields are never empty
- In controller, validate before calling model: `float(value or "0")`
- Catch ValueError and show user-friendly message: "Please enter valid numbers for offset values"

**Warning signs:** Application crashes on "Process" click, ValueError tracebacks in console

### Pitfall 6: Not Preserving Original Filename (FILE-04 Requirement)
**What goes wrong:** Output files get generic names like "output.ifc" or include timestamps, making it hard to track which input file produced which output.

**Why it happens:** Developer chooses arbitrary output filename without considering user workflow.

**How to avoid:**
- Extract filename from input path: `input_path.name`
- Build output path: `output_dir / input_path.name`
- Handle collision: If output file exists, either overwrite (with warning) or append suffix
- Document behavior clearly in UI

**Warning signs:** User confusion about output files, requests for "better file naming"

## Code Examples

Verified patterns from official sources:

### Basic IfcPatch Transformation (OffsetObjectPlacements)
```python
# Source: https://docs.ifcopenshell.org/autoapi/ifcpatch/recipes/OffsetObjectPlacements/index.html
import ifcopenshell
import ifcpatch

def transform_ifc_file(input_path, output_path, x, y, z, should_rotate_first, rotation_z=None):
    """
    Apply offset and optional rotation to IFC file.

    Args:
        input_path: Path to input IFC file (string)
        output_path: Path for output IFC file (string)
        x, y, z: Translation offsets in project length units (float)
        should_rotate_first: If True, rotate then translate; if False, translate then rotate (bool)
        rotation_z: Optional rotation angle around Z axis in decimal degrees (float or None)

    Returns:
        True on success

    Raises:
        RuntimeError: Invalid IFC file
        Exception: Transformation failed
    """
    # Open IFC file - pass path string to capture C++ parse errors
    ifc_file = ifcopenshell.open(input_path)

    # Build arguments: [x, y, z, should_rotate_first, ax (optional)]
    arguments = [x, y, z, should_rotate_first]
    if rotation_z is not None:
        arguments.append(rotation_z)  # Single angle = 2D rotation around Z axis

    # Execute transformation
    output = ifcpatch.execute({
        "input": input_path,
        "file": ifc_file,
        "recipe": "OffsetObjectPlacements",
        "arguments": arguments,
    })

    # Write transformed model to output path
    ifcpatch.write(output, output_path)

    return True

# Example usage
# Offset 100m in X and Y
transform_ifc_file("input.ifc", "output.ifc", 100.0, 100.0, 0.0, True)

# Rotate 90 degrees (no offset)
transform_ifc_file("input.ifc", "output.ifc", 0.0, 0.0, 0.0, True, 90.0)

# Translate (12.5, 5, 2) then rotate 45 degrees
transform_ifc_file("input.ifc", "output.ifc", 12.5, 5.0, 2.0, False, 45.0)
```

### Complete MVC Application Structure
```python
# main.py - Application entry point
import tkinter as tk
from controller import TransformController
from model import IFCTransformModel
from view import TransformView

def main():
    root = tk.Tk()
    root.title("IFC Translate Tool")
    root.geometry("500x400")

    # Create MVC components
    model = IFCTransformModel()
    view = TransformView(root)
    controller = TransformController(model, view)

    # Start GUI event loop
    root.mainloop()

if __name__ == "__main__":
    main()
```

### IFC File Validation
```python
# Source: https://docs.ifcopenshell.org/autoapi/ifcopenshell/validate/index.html
import ifcopenshell
import ifcopenshell.validate

def validate_ifc_file(file_path):
    """
    Validate IFC file before processing.

    Returns:
        (bool, str): (is_valid, error_message)
    """
    try:
        # First check if file can be opened (syntax validation)
        ifc_file = ifcopenshell.open(file_path)

        # Optional: Run schema validation (slower but more thorough)
        logger = ifcopenshell.validate.json_logger()
        ifcopenshell.validate.validate(file_path, logger, express_rules=False)

        # Check if validation found errors
        if logger.statements:
            error_count = sum(1 for s in logger.statements if s.get('level') == 'ERROR')
            if error_count > 0:
                return False, f"IFC file has {error_count} validation errors"

        return True, "Valid IFC file"

    except RuntimeError as e:
        return False, f"Invalid IFC file: {str(e)}"
    except Exception as e:
        return False, f"Could not validate file: {str(e)}"
```

### Tkinter File Selection with Validation
```python
# Source: https://www.pythonguis.com/tutorials/input-validation-tkinter/
from tkinter import filedialog, messagebox
from pathlib import Path
import os

def select_input_file(parent, current_value=""):
    """
    Open file dialog and validate selected IFC file.

    Returns:
        str: Selected file path or empty string if cancelled
    """
    # Determine initial directory
    initial_dir = "/"
    if current_value:
        initial_dir = str(Path(current_value).parent)

    # Open file dialog
    filename = filedialog.askopenfilename(
        parent=parent,
        title="Select IFC File",
        initialdir=initial_dir,
        filetypes=[
            ("IFC files", "*.ifc"),
            ("All files", "*.*")
        ]
    )

    # User cancelled
    if not filename:
        return ""

    # Validate selection
    path = Path(filename)

    if not path.exists():
        messagebox.showerror("Error", f"File does not exist:\n{filename}")
        return ""

    if not path.is_file():
        messagebox.showerror("Error", f"Selected path is not a file:\n{filename}")
        return ""

    if not os.access(path, os.R_OK):
        messagebox.showerror("Error", f"No read permission for file:\n{filename}")
        return ""

    return filename

def select_output_directory(parent, current_value=""):
    """
    Open directory dialog and validate selected output directory.

    Returns:
        str: Selected directory path or empty string if cancelled
    """
    # Determine initial directory
    initial_dir = current_value or "/"

    # Open directory dialog
    directory = filedialog.askdirectory(
        parent=parent,
        title="Select Output Directory",
        initialdir=initial_dir
    )

    # User cancelled
    if not directory:
        return ""

    # Validate selection
    path = Path(directory)

    if not path.exists():
        messagebox.showerror("Error", f"Directory does not exist:\n{directory}")
        return ""

    if not path.is_dir():
        messagebox.showerror("Error", f"Selected path is not a directory:\n{directory}")
        return ""

    if not os.access(path, os.W_OK):
        messagebox.showerror("Error", f"No write permission for directory:\n{directory}")
        return ""

    return directory
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Using os.path for file operations | pathlib.Path | Python 3.4+ (2014), standard since 3.6 | Cleaner API, better cross-platform support, OOP approach |
| PySimpleGUI for rapid GUI dev | Tkinter or PyQt/PySide | 2024 | PySimpleGUI no longer developed, PySide6 recommended as replacement |
| ifcopenshell.api.aggregate | ifcopenshell.api.run | IfcOpenShell 0.7.0+ | Consolidated API structure |
| Separate ifcpatch package | Bundled with ifcopenshell | IfcOpenShell 0.8.0+ | Simpler installation, single pip install |

**Deprecated/outdated:**
- **PySimpleGUI**: No longer maintained as of 2024, use Tkinter for simple UIs or PySide6 for complex ones
- **IfcPatch CLI for programmatic use**: CLI still supported but library API is preferred for better error handling and integration
- **Python 3.8 and below**: IfcOpenShell 0.8.4 requires Python 3.9+

## Open Questions

Things that couldn't be fully resolved:

1. **3D Rotation Behavior (ax, ay, az parameters)**
   - What we know: When all three angles (ax, ay, az) are provided, OffsetObjectPlacements performs 3D rotation. Single angle performs 2D rotation around Z axis.
   - What's unclear: The exact rotation order (XYZ? ZYX?), gimbal lock handling, whether Euler angles or quaternions are used internally
   - Recommendation: For Phase 1, only implement single-angle Z-axis rotation (2D rotation). Defer 3D rotation to later phase when requirements are clearer. Document in code that 3D rotation is possible but not exposed in UI.

2. **Large File Performance**
   - What we know: IfcPatch can be slow on large files (100MB+ files may take minutes). Some element types may not transform correctly.
   - What's unclear: Specific performance characteristics, whether streaming transformations are possible
   - Recommendation: For Phase 1, accept that large files will be slow. Show "Processing..." message. Add basic progress indication if feasible (thread callback). Defer optimization to later phase if needed.

3. **Output File Collision Handling**
   - What we know: FILE-04 requires preserving original filename in output directory
   - What's unclear: User expectation when output file already exists (overwrite? append timestamp? error?)
   - Recommendation: For Phase 1, silently overwrite existing file (simplest). Add confirmation dialog in later phase if users request it.

4. **IFC Validation Performance Trade-off**
   - What we know: `ifcopenshell.validate()` provides better error messages but is slow (can double processing time)
   - What's unclear: Whether basic validation (just `ifcopenshell.open()`) is sufficient for user needs
   - Recommendation: For Phase 1, skip pre-validation. Catch RuntimeError from `ifcopenshell.open()` and show user-friendly message. Add optional validation in later phase if users request better error diagnostics.

## Sources

### Primary (HIGH confidence)
- IfcOpenShell 0.8.4 Official Documentation - OffsetObjectPlacements Recipe: https://docs.ifcopenshell.org/autoapi/ifcpatch/recipes/OffsetObjectPlacements/index.html
- IfcOpenShell 0.8.4 Official Documentation - IfcPatch Usage: https://docs.ifcopenshell.org/ifcpatch.html
- IfcOpenShell 0.8.4 Official Documentation - Installation: https://docs.ifcopenshell.org/ifcopenshell-python/installation.html
- IfcOpenShell 0.8.4 Official Documentation - Validation Module: https://docs.ifcopenshell.org/autoapi/ifcopenshell/validate/index.html
- Python 3.14 Official Documentation - pathlib: https://docs.python.org/3/library/pathlib.html
- Python Tkinter Validation Tutorial: https://www.pythonguis.com/tutorials/input-validation-tkinter/

### Secondary (MEDIUM confidence)
- GitHub Issue #2028 - OffsetObjectPlacements transformation order: https://github.com/IfcOpenShell/IfcOpenShell/issues/2028
- Which Python GUI library should you use in 2026: https://www.pythonguis.com/faq/which-python-gui-library/
- Tkinter and Threading Building Responsive Python GUI Applications: https://medium.com/tomtalkspython/tkinter-and-threading-building-responsive-python-gui-applications-02eed0e9b0a7
- Python Error Handling Best Practices (2026): https://techifysolutions.com/blog/error-handling-in-python/
- Tkinter MVC Pattern Tutorial: https://www.pythontutorial.net/tkinter/tkinter-mvc/

### Tertiary (LOW confidence)
- IfcOpenShell community discussions about transformation issues - various GitHub issues and OSArch forum posts

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - IfcOpenShell 0.8.4 documentation verified, Python stdlib tools are standard
- Architecture: HIGH - MVC pattern for Tkinter is well-established, threading patterns verified in multiple sources
- Pitfalls: MEDIUM-HIGH - Transformation order issue verified in GitHub issue, other pitfalls based on documentation and best practices but not all tested

**Research date:** 2026-01-30
**Valid until:** 2026-02-28 (30 days) - IfcOpenShell is stable, Tkinter is standard library (slow-changing)
