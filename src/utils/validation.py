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


def validate_input_directory(dir_path: str) -> Path:
    """
    Validate an input directory path.

    Args:
        dir_path: Path to the input directory as string

    Returns:
        Path object representing the validated directory

    Raises:
        ValueError: If dir_path is empty, doesn't exist, isn't a directory,
                   or isn't readable
    """
    if not dir_path:
        raise ValueError("No input directory selected")

    path = Path(dir_path)

    if not path.exists():
        raise ValueError(f"Directory does not exist: {path}")

    if not path.is_dir():
        raise ValueError(f"Path is not a directory: {path}")

    if not os.access(path, os.R_OK):
        raise ValueError(f"No read permission for directory: {path}")

    return path


def find_ifc_files(directory_path: str) -> list[Path]:
    """
    Find all IFC files in a directory (case-insensitive).

    Args:
        directory_path: Path to the directory to search

    Returns:
        Sorted list of Path objects for .ifc files found in the directory.
        Returns empty list if no IFC files found.
    """
    path = Path(directory_path)

    # Find both .ifc and .IFC files (case-insensitive handling)
    ifc_files_lower = list(path.glob('*.ifc'))
    ifc_files_upper = list(path.glob('*.IFC'))

    # Combine and filter to only actual files (not directories)
    all_files = ifc_files_lower + ifc_files_upper
    ifc_files = [f for f in all_files if f.is_file()]

    # Sort for consistent ordering across platforms
    return sorted(ifc_files)


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
