"""
IFC Translate Tool - Application Entry Point

Creates and wires together the MVC components (Model, View, Controller)
and launches the Tkinter application.
"""

import sys
from pathlib import Path

# Add project root to path for imports when running directly
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import tkinter as tk
from src.model import IFCTransformModel
from src.view import TransformView
from src.controller import TransformController


def main():
    """Application entry point."""
    # Create root window
    root = tk.Tk()

    # Create MVC components
    model = IFCTransformModel()
    view = TransformView(root)
    controller = TransformController(model, view)

    # Start the application
    root.mainloop()


if __name__ == "__main__":
    main()
