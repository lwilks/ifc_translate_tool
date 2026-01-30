# Phase 2: Preset Management - Research

**Researched:** 2026-01-30
**Domain:** Python desktop application settings persistence with Tkinter UI
**Confidence:** HIGH

## Summary

Phase 2 requires implementing preset management for saving, loading, and deleting transformation configurations in a Python Tkinter desktop application. Research confirms the standard approach for this domain is:

1. **Storage format**: JSON files for human-readable, version-controllable presets
2. **Storage location**: Cross-platform user data directory via `platformdirs` library
3. **UI component**: Tkinter `ttk.Combobox` in readonly mode for preset selection
4. **Atomic writes**: Write-to-temp-then-rename pattern to prevent corruption
5. **Auto-load pattern**: Store last-used preset name, load on application startup

The Python ecosystem provides mature, battle-tested solutions for each component. The key insight is to avoid reinventing configuration management and instead use standard library modules (`json`, `pathlib`) combined with the lightweight `platformdirs` package for cross-platform paths.

**Primary recommendation:** Use JSON files stored in platformdirs user_data_dir, with atomic writes via temp files, loaded/saved through a dedicated PresetsModel class that integrates with the existing MVC architecture.

## Standard Stack

The established libraries/tools for persistent settings in Python desktop applications:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| json (stdlib) | 3.x | Serialize/deserialize presets | Built-in, human-readable, supports all Python types needed for this use case |
| pathlib (stdlib) | 3.x | File system operations | Built-in, cross-platform, modern Pythonic API |
| platformdirs | 4.x (latest) | Cross-platform directory paths | Industry standard replacement for deprecated appdirs, handles OS-specific conventions |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| tkinter.ttk.Combobox (stdlib) | 3.x | Dropdown preset selector UI | Built-in widget specifically designed for selection from predefined values |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| JSON | ConfigParser (INI) | INI doesn't support nested structures; JSON is more flexible and familiar |
| JSON | pickle | pickle is Python-specific, binary (not human-readable), security risks |
| JSON | SQLite | Overkill for simple key-value preset storage; adds complexity |
| platformdirs | Hardcoded paths | Would break cross-platform compatibility (macOS vs Windows vs Linux) |
| Combobox | Listbox | Combobox is specifically designed for selection UIs with text display |

**Installation:**
```bash
pip install platformdirs
```

## Architecture Patterns

### Recommended Project Structure
```
src/
├── models/
│   ├── transform_model.py    # Existing IFC transformation model
│   └── presets_model.py       # NEW: Preset persistence model
├── views/
│   └── transform_view.py      # MODIFY: Add preset UI components
├── controllers/
│   └── transform_controller.py # MODIFY: Wire preset operations
└── utils/
    └── validation.py          # Existing validation utilities
```

### Pattern 1: Presets Data Model
**What:** Separate model class for preset persistence operations (save, load, delete, list)
**When to use:** Always separate persistence logic from UI and business logic (MVC principle)
**Example:**
```python
# Source: MVC best practices for Tkinter applications
# https://www.pythontutorial.net/tkinter/tkinter-mvc/

from pathlib import Path
from platformdirs import user_data_dir
import json

class PresetsModel:
    def __init__(self, app_name="IFCTranslateTool", app_author="YourName"):
        """Initialize with cross-platform data directory."""
        self.data_dir = Path(user_data_dir(app_name, app_author))
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.presets_file = self.data_dir / "presets.json"
        self.config_file = self.data_dir / "config.json"

    def load_presets(self) -> dict:
        """Load all presets from JSON file."""
        if not self.presets_file.exists():
            return {}

        with self.presets_file.open('r', encoding='utf-8') as f:
            return json.load(f)

    def save_preset(self, name: str, preset_data: dict):
        """Save a single preset using atomic write."""
        presets = self.load_presets()
        presets[name] = preset_data
        self._atomic_write_json(self.presets_file, presets)

    def delete_preset(self, name: str):
        """Delete a preset by name."""
        presets = self.load_presets()
        if name in presets:
            del presets[name]
            self._atomic_write_json(self.presets_file, presets)

    def _atomic_write_json(self, filepath: Path, data: dict):
        """Write JSON atomically to prevent corruption."""
        # Write to temp file in same directory
        temp_file = filepath.with_suffix('.tmp')
        with temp_file.open('w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        # Atomic rename (POSIX guarantee)
        temp_file.replace(filepath)
```

### Pattern 2: Last-Used Preset Persistence
**What:** Store the name of the last-used preset in a separate config file
**When to use:** Implementing PRES-04 requirement (auto-load on startup)
**Example:**
```python
# Source: Application state persistence pattern
def save_last_used(self, preset_name: str):
    """Save the last used preset name."""
    config = {"last_used_preset": preset_name}
    self._atomic_write_json(self.config_file, config)

def get_last_used(self) -> str | None:
    """Get the last used preset name."""
    if not self.config_file.exists():
        return None

    with self.config_file.open('r', encoding='utf-8') as f:
        config = json.load(f)

    return config.get("last_used_preset")
```

### Pattern 3: Combobox Integration
**What:** Use ttk.Combobox in readonly state for preset selection dropdown
**When to use:** User needs to select from predefined options (standard pattern)
**Example:**
```python
# Source: Official Python ttk documentation
# https://docs.python.org/3/library/tkinter.ttk.html

from tkinter import ttk

# In view _build_ui method:
preset_frame = tk.LabelFrame(main_frame, text="Presets", padx=10, pady=10)
preset_frame.pack(fill=tk.X, pady=5)

# Combobox for preset selection (readonly prevents typing)
self.preset_combo = ttk.Combobox(
    preset_frame,
    state='readonly',
    width=30
)
self.preset_combo.pack(side=tk.LEFT, padx=5)

# Bind selection event
self.preset_combo.bind('<<ComboboxSelected>>', self._on_preset_selected)

# Update dropdown values dynamically
def update_preset_list(self, preset_names: list):
    """Update combobox values."""
    self.preset_combo['values'] = preset_names

# Set selected preset (use set() for string value or current(index) for position)
def select_preset(self, preset_name: str):
    """Select a preset by name."""
    self.preset_combo.set(preset_name)
```

### Pattern 4: Preset Data Structure
**What:** Store transformation parameters as flat dictionary with descriptive keys
**When to use:** Always - matches existing controller's `get_values()` pattern
**Example:**
```python
# Source: Existing src/view.py get_values() method
preset_data = {
    "x": 10.5,
    "y": -5.0,
    "z": 0.0,
    "rotation": 45.0,
    "rotate_first": True
}

# JSON representation (human-readable, version-controllable):
# {
#   "Site A Offset": {
#     "x": 10.5,
#     "y": -5.0,
#     "z": 0.0,
#     "rotation": 45.0,
#     "rotate_first": true
#   },
#   "Site B Offset": {
#     "x": 100.0,
#     "y": 200.0,
#     "z": 0.0,
#     "rotation": 0.0,
#     "rotate_first": true
#   }
# }
```

### Anti-Patterns to Avoid
- **Don't write directly to the main config file** - Always use temp file + rename for atomic writes
- **Don't use pickle for user-facing config** - Not human-readable, security risks, Python version dependencies
- **Don't hardcode paths like `~/.myapp`** - Use platformdirs for cross-platform compatibility
- **Don't forget encoding='utf-8'** - Prevents platform-dependent behavior on Windows
- **Don't use Combobox in normal state** - Use readonly to prevent invalid user input
- **Don't update UI from model/controller** - Keep MVC separation clean

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Cross-platform app data paths | String concatenation with os.path | platformdirs.user_data_dir() | Handles macOS ~/Library, Windows AppData, Linux XDG spec correctly |
| Atomic file writes | Direct file.write() | Temp file + replace() | Prevents corruption from crashes/power loss during write |
| JSON encoding | Manual string building | json.dump() with ensure_ascii=False | Handles Unicode, escaping, special characters correctly |
| Preset name validation | Custom regex | Existing validate_* pattern | Maintain consistency with existing validation utilities |
| Combobox population | Manual widget state management | values parameter + set() method | Widget designed for this exact use case |

**Key insight:** File corruption from partial writes is a real problem. The write-to-temp-then-rename pattern is atomic on all modern filesystems (POSIX guarantee). Don't assume "it's just a small file, it'll be fine."

## Common Pitfalls

### Pitfall 1: File Corruption from Direct Writes
**What goes wrong:** Writing directly to the config file can leave it corrupted if the program crashes, power fails, or disk fills during write.
**Why it happens:** Write operations are not atomic. A crash mid-write leaves a partial file that fails to parse.
**How to avoid:** Use temp file + replace pattern. Write to `presets.tmp`, then use `Path.replace()` which is atomic.
**Warning signs:** Users report "presets disappeared after crash" or JSONDecodeError on startup.

### Pitfall 2: Wrong Directory on Different Platforms
**What goes wrong:** Hardcoding paths like `~/.myapp/presets.json` works on Linux/macOS but violates Windows conventions.
**Why it happens:** Each OS has different conventions (Windows: AppData, macOS: Application Support, Linux: XDG).
**How to avoid:** Use `platformdirs.user_data_dir(app_name, app_author)` which handles OS-specific paths automatically.
**Warning signs:** Windows users report "can't find presets" or permission errors.

### Pitfall 3: Missing encoding='utf-8' Parameter
**What goes wrong:** Opening files without explicit encoding uses platform default (cp1252 on Windows, utf-8 on macOS/Linux). Presets with non-ASCII characters fail to load cross-platform.
**Why it happens:** Python's open() defaults to locale encoding for backward compatibility.
**How to avoid:** Always specify `encoding='utf-8'` when opening text files. Use `ensure_ascii=False` in json.dump() for readability.
**Warning signs:** Characters like "°" or "ñ" appear as garbage, or UnicodeDecodeError on different machines.

### Pitfall 4: Combobox Set Before Values Populated
**What goes wrong:** Calling `combo.set(preset_name)` before `combo['values'] = preset_list` appears to work but causes inconsistent behavior.
**Why it happens:** The combobox displays the text but doesn't properly register it as a selection.
**How to avoid:** Always populate `values` first, then call `set()` or `current()`.
**Warning signs:** `<<ComboboxSelected>>` event doesn't fire, or `current()` returns -1 unexpectedly.

### Pitfall 5: Forgetting to Update Last-Used on Save
**What goes wrong:** User saves a new preset, but on restart the old preset loads instead.
**Why it happens:** Saving preset updates presets.json but doesn't update the last_used field in config.json.
**How to avoid:** Update last-used whenever a preset is saved or selected, not just when loading.
**Warning signs:** PRES-04 requirement fails - last used preset doesn't persist across restarts.

### Pitfall 6: Not Handling Empty Presets List
**What goes wrong:** App crashes or shows error on first run when no presets exist yet.
**Why it happens:** Code assumes at least one preset exists for populating UI.
**How to avoid:** Check if preset list is empty before setting combobox values. Disable load/delete buttons when no presets exist.
**Warning signs:** IndexError or "list index out of range" on fresh installation.

## Code Examples

Verified patterns from official sources:

### Loading JSON with Proper Error Handling
```python
# Source: Official Python json documentation
# https://docs.python.org/3/library/json.html

from pathlib import Path
import json

def load_presets(self) -> dict:
    """Load presets with proper error handling."""
    if not self.presets_file.exists():
        return {}

    try:
        with self.presets_file.open('r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        # Log error with specific details
        print(f"Error loading presets: {e.msg} at line {e.lineno}, column {e.colno}")
        # Return empty dict rather than crashing
        return {}
    except Exception as e:
        print(f"Unexpected error loading presets: {e}")
        return {}
```

### Atomic Write with pathlib
```python
# Source: Safe atomic file writes pattern
# https://gist.github.com/therightstuff/cbdcbef4010c20acc70d2175a91a321f

from pathlib import Path
import json

def atomic_write_json(filepath: Path, data: dict):
    """
    Write JSON file atomically to prevent corruption.

    Uses temp file in same directory to ensure atomic rename
    works (cross-filesystem renames are not atomic).
    """
    # Create temp file in same directory as target
    temp_file = filepath.with_suffix('.tmp')

    try:
        # Write to temp file
        with temp_file.open('w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        # Atomic rename (POSIX guarantee)
        temp_file.replace(filepath)

    except Exception as e:
        # Clean up temp file if write failed
        if temp_file.exists():
            temp_file.unlink()
        raise
```

### Combobox Event Binding and Value Setting
```python
# Source: Official Python ttk.Combobox documentation
# https://docs.python.org/3/library/tkinter.ttk.html

from tkinter import ttk

# Create combobox
self.preset_combo = ttk.Combobox(parent, state='readonly', width=30)
self.preset_combo.pack()

# Bind to selection event (fires when user selects from dropdown)
self.preset_combo.bind('<<ComboboxSelected>>', self._on_preset_selected)

# Populate dropdown values (do this BEFORE setting selection)
self.preset_combo['values'] = ['Preset A', 'Preset B', 'Preset C']

# Set selected value (two methods):
# Method 1: By string value (most common)
self.preset_combo.set('Preset B')

# Method 2: By index (when index is more convenient)
self.preset_combo.current(1)  # Selects 'Preset B' (index 1)

# Get current selection
selected_name = self.preset_combo.get()  # Returns string
selected_index = self.preset_combo.current()  # Returns int (-1 if not in list)
```

### Cross-Platform Data Directory
```python
# Source: platformdirs documentation
# https://github.com/tox-dev/platformdirs

from pathlib import Path
from platformdirs import user_data_dir

# Get platform-specific user data directory
# macOS: ~/Library/Application Support/IFCTranslateTool
# Windows: C:\Users\<User>\AppData\Local\<AppAuthor>\IFCTranslateTool
# Linux: ~/.local/share/IFCTranslateTool
data_dir = Path(user_data_dir("IFCTranslateTool", "YourName"))

# Create directory if it doesn't exist (parents=True creates intermediate dirs)
data_dir.mkdir(parents=True, exist_ok=True)

# Construct file paths
presets_file = data_dir / "presets.json"
config_file = data_dir / "config.json"
```

### Populating Form Fields from Preset
```python
# Source: Existing view.py get_values() pattern (reversed for setting)

def load_preset_values(self, preset_data: dict):
    """
    Populate form fields from preset data.

    Complements existing get_values() method.
    """
    # Set StringVars (automatically updates Entry widgets)
    self.x_var.set(str(preset_data.get('x', 0)))
    self.y_var.set(str(preset_data.get('y', 0)))
    self.z_var.set(str(preset_data.get('z', 0)))
    self.rotation_var.set(str(preset_data.get('rotation', 0)))

    # Set BooleanVar (automatically updates Checkbutton)
    self.rotate_first_var.set(preset_data.get('rotate_first', True))
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| appdirs library | platformdirs library | 2020 | appdirs officially deprecated; platformdirs is actively maintained fork |
| ConfigParser (INI) | JSON with pathlib | 2015+ | JSON is more flexible, familiar, and supports nested structures |
| pickle for config | JSON | Always | pickle has security risks, not human-readable, Python version dependent |
| Direct file writes | Atomic writes (temp + rename) | Best practice since 2010s | Prevents corruption from crashes, power loss |
| Hardcoded encoding | Explicit encoding='utf-8' | Python 3.7+ | Cross-platform compatibility, explicit is better than implicit |
| Manual Combobox updates | StringVar binding | Modern Tkinter | Cleaner separation, automatic UI updates |

**Deprecated/outdated:**
- **appdirs**: Officially deprecated since 2020, use platformdirs instead
- **ConfigParser for app settings**: Still works but JSON is more flexible and widely adopted
- **pickle for user-facing config**: Security risks (arbitrary code execution), not human-readable

## Open Questions

Things that couldn't be fully resolved:

1. **Should presets be stored per-preset or in a single file?**
   - What we know: Single file is simpler, reduces I/O
   - What's unclear: Impact on concurrent writes (if multiple instances run)
   - Recommendation: Start with single file (presets.json) as single-instance app. If multi-instance support needed later, add file locking or switch to separate files.

2. **Should we validate preset data structure on load?**
   - What we know: Pydantic provides schema validation, but adds dependency
   - What's unclear: Whether validation complexity justifies dependency
   - Recommendation: Start without Pydantic. Use simple dict.get() with defaults. Add Pydantic only if validation errors become a problem in practice.

3. **How to handle preset name conflicts (save with existing name)?**
   - What we know: Standard pattern is "overwrite with confirmation" or "auto-rename"
   - What's unclear: User preference for this app
   - Recommendation: Overwrite with confirmation dialog (simplest, most predictable). Use messagebox.askyesno() before save.

## Sources

### Primary (HIGH confidence)
- [Python json module documentation](https://docs.python.org/3/library/json.html) - Official documentation for JSON serialization (updated Jan 27, 2026)
- [Python pathlib documentation](https://docs.python.org/3/library/pathlib.html) - Official documentation for filesystem paths
- [Python tkinter.ttk documentation](https://docs.python.org/3/library/tkinter.ttk.html) - Official Combobox widget documentation
- [platformdirs GitHub](https://github.com/tox-dev/platformdirs) - Official repository for cross-platform directory paths
- [Safe atomic file writes pattern](https://gist.github.com/therightstuff/cbdcbef4010c20acc70d2175a91a321f) - Verified atomic write pattern for JSON/YAML
- [Tkinter MVC pattern tutorial](https://www.pythontutorial.net/tkinter/tkinter-mvc/) - Standard MVC architecture for Tkinter apps

### Secondary (MEDIUM confidence)
- [Working with Python Configuration Files: Best Practices](https://configu.com/blog/working-with-python-configuration-files-tutorial-best-practices/) - Configuration management patterns (2026)
- [Configuration files in Python](https://martin-thoma.com/configuration-files-in-python/) - Comparison of config formats
- [Crash-safe JSON at scale](https://dev.to/constanta/crash-safe-json-at-scale-atomic-writes-recovery-without-a-db-3aic) - Atomic write patterns
- [Better File Writing in Python: Embrace Atomic Updates](https://sahmanish20.medium.com/better-file-writing-in-python-embrace-atomic-updates-593843bfab4f) - Atomic write explanation
- [6 Methods To Add & Update Items In Tkinter Combobox](https://likegeeks.com/add-update-items-tkinter-combobox/) - Combobox value management
- [Getting the Selected Value from Combobox in Tkinter: Complete Guide 2026](https://copyprogramming.com/howto/getting-the-selected-value-from-combobox-in-tkinter) - Combobox methods comparison

### Tertiary (LOW confidence)
- [EasySettings PyPI](https://pypi.org/project/EasySettings/) - Third-party settings library (not needed for this use case)
- [Pydantic JSON Schema documentation](https://docs.pydantic.dev/latest/concepts/json_schema/) - Schema validation option (overkill for simple presets)

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - All components are Python stdlib or widely-adopted industry standard (platformdirs)
- Architecture: HIGH - MVC pattern matches existing codebase, verified with official Tkinter documentation
- Pitfalls: HIGH - File corruption and encoding issues are well-documented problems with established solutions

**Research date:** 2026-01-30
**Valid until:** 2026-03-30 (60 days - stable ecosystem, stdlib-based)
