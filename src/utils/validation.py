"""
Validation utilities for file path and directory handling.

Provides functions to validate input IFC files, output directories, and build output paths.
"""

from pathlib import Path
import os


def validate_input_file(file_path: str) -> Path:
    """
    Validate an input IFC file path.

    Args:
        file_path: Path to the IFC file as string

    Returns:
        Path object representing the validated file

    Raises:
        ValueError: If file_path is empty, doesn't exist, isn't a file,
                   isn't .ifc format, or isn't readable
    """
    if not file_path:
        raise ValueError("No file selected")

    path = Path(file_path)

    if not path.exists():
        raise ValueError(f"File does not exist: {path}")

    if not path.is_file():
        raise ValueError(f"Path is not a file: {path}")

    if path.suffix.lower() != '.ifc':
        raise ValueError(f"File must be .ifc format, got: {path.suffix}")

    if not os.access(path, os.R_OK):
        raise ValueError(f"No read permission for file: {path}")

    return path


def validate_output_directory(dir_path: str) -> Path:
    """
    Validate an output directory path.

    Args:
        dir_path: Path to the output directory as string

    Returns:
        Path object representing the validated directory

    Raises:
        ValueError: If dir_path is empty, doesn't exist, isn't a directory,
                   or isn't writable
    """
    if not dir_path:
        raise ValueError("No output directory selected")

    path = Path(dir_path)

    if not path.exists():
        raise ValueError(f"Directory does not exist: {path}")

    if not path.is_dir():
        raise ValueError(f"Path is not a directory: {path}")

    if not os.access(path, os.W_OK):
        raise ValueError(f"No write permission for directory: {path}")

    return path


def build_output_path(input_path: str | Path, output_dir: str | Path) -> Path:
    """
    Build the output file path by preserving the original filename.

    Args:
        input_path: Path to the input file
        output_dir: Path to the output directory

    Returns:
        Path object representing the full output file path
    """
    input_path = Path(input_path)
    output_dir = Path(output_dir)

    return output_dir / input_path.name
