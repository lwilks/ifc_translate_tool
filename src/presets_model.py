"""
Preset Persistence Model

This module provides the PresetsModel class for managing transformation
preset storage. Presets are stored as JSON files in the platform-appropriate
user data directory.
"""

from pathlib import Path
from platformdirs import user_data_dir
import json


class PresetsModel:
    """
    Model layer for preset persistence operations.

    Manages saving, loading, and deleting transformation presets using
    JSON storage in cross-platform user data directory. Follows MVC
    pattern established in Phase 1.
    """

    def __init__(self, app_name="IFCTranslateTool", app_author="IFCTranslateTool"):
        """
        Initialize preset model with cross-platform data directory.

        Creates data directory if it doesn't exist and sets up paths
        for presets.json and config.json files.

        Args:
            app_name: Application name for directory naming
            app_author: Application author for directory naming (Windows)
        """
        self.data_dir = Path(user_data_dir(app_name, app_author))
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.presets_file = self.data_dir / "presets.json"
        self.config_file = self.data_dir / "config.json"

    def load_presets(self) -> dict:
        """
        Load all presets from JSON file.

        Returns empty dict if file doesn't exist or is corrupted.
        Handles JSONDecodeError gracefully to prevent crashes.

        Returns:
            Dictionary mapping preset names to preset data dicts.
            Empty dict if no presets or file corrupted.
        """
        if not self.presets_file.exists():
            return {}

        try:
            with self.presets_file.open('r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            # Return empty dict rather than crashing on corrupted file
            return {}
        except Exception:
            # Handle other errors gracefully
            return {}

    def save_preset(self, name: str, preset_data: dict):
        """
        Save a single preset using atomic write.

        Loads existing presets, adds/updates the new one, and writes
        back atomically to prevent corruption.

        Preset data structure:
        {
            "x": float,
            "y": float,
            "z": float,
            "rotation": float,
            "rotate_first": bool
        }

        Args:
            name: Preset name (used as dictionary key)
            preset_data: Dictionary of transformation parameters
        """
        presets = self.load_presets()
        presets[name] = preset_data
        self._atomic_write_json(self.presets_file, presets)

    def delete_preset(self, name: str):
        """
        Delete a preset by name.

        Loads presets, removes if exists, writes back atomically.
        Does nothing if preset doesn't exist.

        Args:
            name: Preset name to delete
        """
        presets = self.load_presets()
        if name in presets:
            del presets[name]
            self._atomic_write_json(self.presets_file, presets)

    def list_presets(self) -> list[str]:
        """
        Return sorted list of preset names.

        Returns:
            Sorted list of preset names. Empty list if no presets.
        """
        presets = self.load_presets()
        return sorted(presets.keys())

    def save_last_used(self, preset_name: str):
        """
        Save the last used preset name to config.

        Used for auto-loading preset on application startup.

        Args:
            preset_name: Name of preset to mark as last used
        """
        config = {"last_used_preset": preset_name}
        self._atomic_write_json(self.config_file, config)

    def get_last_used(self) -> str | None:
        """
        Get the last used preset name from config.

        Returns:
            Last used preset name, or None if not set or file doesn't exist
        """
        if not self.config_file.exists():
            return None

        try:
            with self.config_file.open('r', encoding='utf-8') as f:
                config = json.load(f)
            return config.get("last_used_preset")
        except (json.JSONDecodeError, Exception):
            return None

    def _atomic_write_json(self, filepath: Path, data: dict):
        """
        Write JSON file atomically to prevent corruption.

        Uses temp file + rename pattern (atomic on POSIX). Writes to
        .tmp file first, then uses Path.replace() for atomic rename.

        Args:
            filepath: Target file path
            data: Dictionary to serialize as JSON
        """
        temp_file = filepath.with_suffix('.tmp')

        try:
            # Write to temp file with UTF-8 encoding
            with temp_file.open('w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            # Atomic rename (POSIX guarantee)
            temp_file.replace(filepath)

        except Exception:
            # Clean up temp file if write failed
            if temp_file.exists():
                temp_file.unlink()
            raise
