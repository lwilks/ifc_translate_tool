# Phase 3: Batch Processing - Research

**Researched:** 2026-01-30
**Domain:** Batch file processing in Python Tkinter with thread-safe progress tracking
**Confidence:** HIGH

## Summary

Batch processing multiple IFC files requires coordinating directory scanning, background thread execution, progress tracking, and cancellation support. The standard approach uses Python's `pathlib.Path.glob()` for file discovery, `threading.Event` for cancellable operations, `queue.Queue` for thread-safe communication, and `ttk.Progressbar` for visual feedback.

The existing codebase already implements the queue-based pattern for single-file processing in `controller.py` (lines 37-77), using `queue.Queue` and `root.after()` polling. This pattern extends naturally to batch operations by iterating over multiple files and updating progress after each completion.

Key architectural insight: Batch processing is fundamentally single-file processing in a loop with progress tracking. The cancellation mechanism requires checking a `threading.Event` flag between file operations, not interrupting mid-transformation.

**Primary recommendation:** Extend existing queue-polling pattern with `threading.Event` for cancellation and `ttk.Progressbar` in determinate mode for progress display.

## Standard Stack

The established libraries/tools for this domain:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `pathlib.Path` | stdlib | Directory scanning and file pattern matching | Python 3.4+ standard, object-oriented file paths |
| `threading.Event` | stdlib | Cancellation signaling between threads | Official Python threading primitive for graceful shutdown |
| `queue.Queue` | stdlib | Thread-safe result communication | Thread-safe communication without locks |
| `ttk.Progressbar` | stdlib (tkinter.ttk) | Visual progress feedback | Standard Tkinter widget, determinate/indeterminate modes |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `concurrent.futures.ThreadPoolExecutor` | stdlib | Optional parallel processing | Only if parallelizing I/O-bound operations (not needed for sequential batch) |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `pathlib.Path.glob()` | `glob.glob()` | `pathlib` is more modern, returns Path objects directly |
| `threading.Event` | Custom flag with locks | Event is thread-safe by design, simpler API |
| `ttk.Progressbar` | Custom canvas drawing | Progressbar handles platform styling, less code |

**Installation:**
```bash
# All libraries are Python stdlib - no installation required
```

## Architecture Patterns

### Recommended Project Structure
```
src/
├── controller.py       # Add batch_process method alongside on_process_clicked
├── view.py            # Add directory selection, progress bar, cancel button
├── model.py           # No changes needed - transform_file works per-file
└── utils/
    └── validation.py  # Add validate_input_directory, find_ifc_files
```

### Pattern 1: Event-Based Cancellation
**What:** Use `threading.Event` to signal background thread to stop gracefully between file operations.

**When to use:** Any long-running background operation that user can cancel.

**Example:**
```python
# Source: https://docs.python.org/3/library/threading.html
import threading

def batch_worker(files, stop_event):
    for file in files:
        if stop_event.is_set():
            break  # Check before each file
        process_file(file)

stop_event = threading.Event()
thread = threading.Thread(target=batch_worker, args=(files, stop_event))
thread.start()

# User clicks cancel
stop_event.set()
thread.join()
```

### Pattern 2: Queue-Based Progress Updates
**What:** Background thread puts progress updates in queue, main thread polls via `root.after()`.

**When to use:** Updating GUI from background threads (Tkinter requirement).

**Example:**
```python
# Source: Existing pattern in controller.py lines 49-77
def _check_queue(self):
    try:
        result = self.result_queue.get_nowait()
        # Update progress bar, status text
        self.view.update_progress(result['current'], result['total'])
    except queue.Empty:
        pass
    self.view.root.after(100, self._check_queue)
```

### Pattern 3: Determinate Progress Bar
**What:** `ttk.Progressbar` in determinate mode with `maximum` set to file count.

**When to use:** When total work is known (batch file count).

**Example:**
```python
# Source: https://www.pythontutorial.net/tkinter/tkinter-progressbar/
progress = ttk.Progressbar(parent, orient='horizontal', length=300, mode='determinate')
progress['maximum'] = len(files)
progress['value'] = 0

# After each file
progress['value'] += 1
```

### Pattern 4: Directory Scanning with pathlib
**What:** Use `Path.glob('*.ifc')` to find all IFC files in directory.

**When to use:** Finding files matching pattern in single directory (non-recursive).

**Example:**
```python
# Source: https://docs.python.org/3/library/pathlib.html
from pathlib import Path

def find_ifc_files(directory):
    path = Path(directory)
    # Returns generator, convert to list for counting
    files = list(path.glob('*.ifc'))
    # Sort for consistent ordering
    return sorted(files)
```

### Anti-Patterns to Avoid
- **Daemon threads for batch work:** Daemon threads terminate abruptly on shutdown, potentially corrupting files. Use non-daemon threads with Event signaling.
- **Direct GUI updates from thread:** Never call Tkinter widget methods from background threads. Always use queue + `after()` pattern.
- **Blocking operations in main thread:** Never run `thread.join()` or blocking I/O in main thread - freezes GUI.
- **Ignoring partial failures:** Don't stop entire batch on first error. Collect errors, continue processing, report at end.

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Thread cancellation | Custom flag + Lock | `threading.Event` | Event is thread-safe, simpler API, standard pattern |
| Thread-safe GUI updates | Direct widget calls + locks | `queue.Queue` + `root.after()` | Tkinter requires main thread updates, queue is stdlib |
| Progress bar rendering | Custom Canvas drawing | `ttk.Progressbar` | Platform-native styling, accessibility, less code |
| File pattern matching | Manual loop + string checks | `Path.glob('*.ifc')` | Handles edge cases (symlinks, permissions, case sensitivity) |

**Key insight:** Threading primitives (Event, Queue) exist because manual synchronization with locks is error-prone. Use stdlib patterns that have been battle-tested.

## Common Pitfalls

### Pitfall 1: File Corruption on Cancellation
**What goes wrong:** Canceling during `model.transform_file()` leaves partial/corrupted output file.

**Why it happens:** `ifcpatch.write()` is not atomic - file is incomplete if interrupted.

**How to avoid:** Check `stop_event.is_set()` BETWEEN files, never during. Let each file complete or fail fully.

**Warning signs:** Partial IFC files in output directory after cancel, transformation errors on retry.

### Pitfall 2: Progress Updates Freeze GUI
**What goes wrong:** GUI becomes unresponsive during batch processing despite threading.

**Why it happens:** Updating GUI directly from worker thread, or polling queue too infrequently.

**How to avoid:**
- Use `queue.Queue` for thread communication
- Poll queue every 100ms with `root.after()`
- Update progress bar value directly (fast operation)

**Warning signs:** Window shows "Not Responding", can't click cancel button during processing.

### Pitfall 3: Ignoring File Errors Stops Batch
**What goes wrong:** First corrupted/unreadable IFC file stops entire batch.

**Why it happens:** Exception in `transform_file()` propagates to thread, exits loop.

**How to avoid:** Wrap each file operation in try/except, collect failures, continue batch.

```python
# Source: https://www.kdnuggets.com/5-error-handling-patterns-in-python-beyond-try-except
results = {'success': [], 'failed': []}
for file in files:
    try:
        transform_file(file)
        results['success'].append(file)
    except Exception as e:
        results['failed'].append((file, str(e)))
```

**Warning signs:** Batch stops after first error, user sees "Transformation failed" for valid files.

### Pitfall 4: Race Condition on Cancel Click
**What goes wrong:** Cancel button clicked, but more files still process.

**Why it happens:** Event flag set but thread already past the check point.

**How to avoid:** Check event at start of each iteration, disable process button until thread joins.

**Warning signs:** Files created after cancel clicked, inconsistent stop points.

### Pitfall 5: Progress Bar Doesn't Update
**What goes wrong:** Progress bar stays at 0% despite files processing.

**Why it happens:** Forgetting to call `progress['value'] = X` after queue update.

**How to avoid:** Update progress bar in `_check_queue()` when receiving success/failure messages.

**Warning signs:** Files complete but progress bar frozen, only final message shows completion.

## Code Examples

Verified patterns from official sources:

### Finding IFC Files in Directory
```python
# Source: https://docs.python.org/3/library/pathlib.html
from pathlib import Path

def find_ifc_files(directory_path: str) -> list[Path]:
    """Find all .ifc files in directory (non-recursive)."""
    directory = Path(directory_path)

    # glob() returns generator, convert to list for len()
    # Sort for consistent ordering across platforms
    files = sorted(directory.glob('*.ifc'))

    return [f for f in files if f.is_file()]  # Exclude directories named *.ifc
```

### Cancellable Batch Processing Loop
```python
# Source: https://docs.python.org/3/library/threading.html
import threading
import queue

def batch_process_files(files, stop_event, result_queue):
    """Process files with cancellation support."""
    results = {'success': [], 'failed': []}

    for i, file in enumerate(files):
        # Check cancellation before each file
        if stop_event.is_set():
            result_queue.put({
                'type': 'cancelled',
                'processed': i,
                'total': len(files)
            })
            break

        try:
            # Process single file
            transform_file(file)
            results['success'].append(file)

            # Report progress
            result_queue.put({
                'type': 'progress',
                'current': i + 1,
                'total': len(files),
                'file': file.name
            })
        except Exception as e:
            results['failed'].append((file, str(e)))
            result_queue.put({
                'type': 'error',
                'file': file.name,
                'error': str(e)
            })

    # Final summary
    if not stop_event.is_set():
        result_queue.put({
            'type': 'complete',
            'results': results
        })
```

### Progress Bar Setup and Update
```python
# Source: https://www.pythontutorial.net/tkinter/tkinter-progressbar/
from tkinter import ttk

# Create progress bar in view
self.progress = ttk.Progressbar(
    parent,
    orient='horizontal',
    length=300,
    mode='determinate'
)
self.progress.pack()

# Initialize for batch
def start_batch(self, file_count):
    self.progress['maximum'] = file_count
    self.progress['value'] = 0

# Update after each file (called from _check_queue)
def update_progress(self, current, total):
    self.progress['value'] = current
    self.status_var.set(f"Processing {current}/{total}")
```

### Thread-Safe Queue Polling
```python
# Source: Existing pattern in controller.py (verified thread-safe pattern)
def _check_queue(self):
    """Poll result queue for batch updates."""
    try:
        msg = self.result_queue.get_nowait()

        if msg['type'] == 'progress':
            self.view.update_progress(msg['current'], msg['total'])
            self.view.show_status(f"Processing {msg['file']}...")

        elif msg['type'] == 'error':
            # Log error but continue batch
            self.errors.append((msg['file'], msg['error']))

        elif msg['type'] == 'complete':
            self.view.set_processing(False)
            self._show_batch_summary(msg['results'])

        elif msg['type'] == 'cancelled':
            self.view.set_processing(False)
            self.view.show_status(f"Cancelled after {msg['processed']} files")

    except queue.Empty:
        pass

    # Continue polling
    self.view.root.after(100, self._check_queue)
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `os.listdir()` + manual filtering | `pathlib.Path.glob()` | Python 3.4 (2014) | Object-oriented paths, pattern matching built-in |
| Manual locks for thread communication | `queue.Queue` | Always standard | Thread-safe by design, simpler code |
| `thread.join(timeout)` polling | `threading.Event` | Python 2.6+ (2008) | Clean cancellation API, no timeout guessing |
| Indeterminate progress bar | Determinate with known count | `ttk.Progressbar` modes | Better UX - users see actual progress percentage |

**Deprecated/outdated:**
- `os.path.*` functions: Use `pathlib` for modern Python (3.4+)
- `thread` module: Deprecated, use `threading` module
- Daemon threads for important work: Non-daemon + Event is current best practice

## Open Questions

1. **Should batch processing support recursive directory scanning?**
   - What we know: `Path.glob('**/*.ifc')` supports recursive with `**` pattern
   - What's unclear: User requirement FILE-02 says "input directory" (singular level)
   - Recommendation: Implement single-level for Phase 3, defer recursive as future enhancement

2. **Should failed files block subsequent files?**
   - What we know: Best practice is continue-on-error with summary report
   - What's unclear: User expectation for error handling
   - Recommendation: Continue processing, collect failures, show summary dialog at end

3. **Should progress bar show file names or just count?**
   - What we know: Both are standard patterns
   - What's unclear: UI space constraints, user preference
   - Recommendation: Show both - count in progress bar, current filename in status label

## Sources

### Primary (HIGH confidence)
- [Python pathlib documentation](https://docs.python.org/3/library/pathlib.html) - January 29, 2026 - Path.glob() patterns and directory scanning
- [Python threading documentation](https://docs.python.org/3/library/threading.html) - January 29, 2026 - threading.Event cancellation pattern
- [Python concurrent.futures documentation](https://docs.python.org/3/library/concurrent.futures.html) - January 29, 2026 - ThreadPoolExecutor and Future cancellation
- [Python Tkinter Progressbar Tutorial](https://www.pythontutorial.net/tkinter/tkinter-progressbar/) - March 2025 - ttk.Progressbar modes and usage
- Existing codebase pattern (controller.py lines 37-77) - Verified queue-based threading pattern

### Secondary (MEDIUM confidence)
- [DataCamp Progress Bars Guide](https://www.datacamp.com/tutorial/progress-bars-in-python) - May 2025 - Progress tracking patterns
- [KDnuggets Error Handling Patterns](https://www.kdnuggets.com/5-error-handling-patterns-in-python-beyond-try-except) - 2025 - Collect-and-continue pattern
- [Python Batch Processing Best Practices](https://dev.to/lifeportal20002010/python-batch-processing-from-bat-integration-to-subprocess-best-practices-21bg) - 1 week ago - Common pitfalls
- [Medium: Tkinter and Threading](https://medium.com/tomtalkspython/tkinter-and-threading-building-responsive-python-gui-applications-02eed0e9b0a7) - April 2025 - Thread-safe GUI updates

### Tertiary (LOW confidence)
- None - all findings verified with official docs or existing codebase

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - All stdlib, verified with official Python docs (Jan 2026)
- Architecture: HIGH - Extends existing verified pattern in codebase
- Pitfalls: HIGH - Cross-referenced with official docs and recent (2025-2026) articles

**Research date:** 2026-01-30
**Valid until:** 2026-02-28 (30 days - stdlib patterns are stable)
