"""
Tkinter view layer for IFC Translate Tool.

Provides the TransformView class that creates and manages the UI components
for file selection, transformation parameters, and processing controls.
"""

import tkinter as tk
from tkinter import filedialog, messagebox


class TransformView:
    """
    Main view for the IFC transformation tool.

    Creates a Tkinter UI with:
    - Input file selection
    - Output directory selection
    - X, Y, Z offset fields (float validated)
    - Rotation field (float validated)
    - Rotate first checkbox
    - Process button
    - Status display
    """

    def __init__(self, root: tk.Tk):
        """
        Initialize the view with all UI components.

        Args:
            root: The Tkinter root window
        """
        self.root = root
        self.controller = None

        # Configure window
        self.root.title("IFC Translate Tool")
        self.root.geometry("550x400")

        # Initialize all StringVars and BooleanVars
        self.input_file_var = tk.StringVar()
        self.output_dir_var = tk.StringVar()
        self.x_var = tk.StringVar(value="0")
        self.y_var = tk.StringVar(value="0")
        self.z_var = tk.StringVar(value="0")
        self.rotation_var = tk.StringVar(value="0")
        self.rotate_first_var = tk.BooleanVar(value=True)
        self.status_var = tk.StringVar(value="Ready")

        # Register float validation command
        validate_float_cmd = self.root.register(self._validate_float)

        # Build UI
        self._build_ui(validate_float_cmd)

    def _build_ui(self, validate_float_cmd):
        """Build all UI components."""
        # Main container with padding
        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Input file selection
        file_frame = tk.Frame(main_frame)
        file_frame.pack(fill=tk.X, pady=5)
        tk.Label(file_frame, text="Input IFC File:", width=15, anchor="w").pack(side=tk.LEFT)
        tk.Entry(file_frame, textvariable=self.input_file_var, width=35).pack(side=tk.LEFT, padx=5)
        tk.Button(file_frame, text="Browse...", command=self._select_input_file).pack(side=tk.LEFT)

        # Output directory selection
        output_frame = tk.Frame(main_frame)
        output_frame.pack(fill=tk.X, pady=5)
        tk.Label(output_frame, text="Output Directory:", width=15, anchor="w").pack(side=tk.LEFT)
        tk.Entry(output_frame, textvariable=self.output_dir_var, width=35).pack(side=tk.LEFT, padx=5)
        tk.Button(output_frame, text="Browse...", command=self._select_output_dir).pack(side=tk.LEFT)

        # Separator
        tk.Frame(main_frame, height=2, bd=1, relief=tk.SUNKEN).pack(fill=tk.X, pady=15)

        # Offset fields
        offset_label_frame = tk.LabelFrame(main_frame, text="Translation Offsets (meters)", padx=10, pady=10)
        offset_label_frame.pack(fill=tk.X, pady=5)

        # X offset
        x_frame = tk.Frame(offset_label_frame)
        x_frame.pack(fill=tk.X, pady=2)
        tk.Label(x_frame, text="X Offset:", width=15, anchor="w").pack(side=tk.LEFT)
        tk.Entry(
            x_frame,
            textvariable=self.x_var,
            width=20,
            validate="key",
            validatecommand=(validate_float_cmd, "%P")
        ).pack(side=tk.LEFT)

        # Y offset
        y_frame = tk.Frame(offset_label_frame)
        y_frame.pack(fill=tk.X, pady=2)
        tk.Label(y_frame, text="Y Offset:", width=15, anchor="w").pack(side=tk.LEFT)
        tk.Entry(
            y_frame,
            textvariable=self.y_var,
            width=20,
            validate="key",
            validatecommand=(validate_float_cmd, "%P")
        ).pack(side=tk.LEFT)

        # Z offset
        z_frame = tk.Frame(offset_label_frame)
        z_frame.pack(fill=tk.X, pady=2)
        tk.Label(z_frame, text="Z Offset:", width=15, anchor="w").pack(side=tk.LEFT)
        tk.Entry(
            z_frame,
            textvariable=self.z_var,
            width=20,
            validate="key",
            validatecommand=(validate_float_cmd, "%P")
        ).pack(side=tk.LEFT)

        # Rotation field
        rotation_label_frame = tk.LabelFrame(main_frame, text="Rotation", padx=10, pady=10)
        rotation_label_frame.pack(fill=tk.X, pady=5)

        rotation_frame = tk.Frame(rotation_label_frame)
        rotation_frame.pack(fill=tk.X, pady=2)
        tk.Label(rotation_frame, text="Rotation (degrees):", width=15, anchor="w").pack(side=tk.LEFT)
        tk.Entry(
            rotation_frame,
            textvariable=self.rotation_var,
            width=20,
            validate="key",
            validatecommand=(validate_float_cmd, "%P")
        ).pack(side=tk.LEFT)

        # Rotate first checkbox
        tk.Checkbutton(
            rotation_label_frame,
            text="Rotate First (apply rotation before translation)",
            variable=self.rotate_first_var
        ).pack(anchor="w", pady=5)

        # Action button
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=15)
        self.process_button = tk.Button(
            button_frame,
            text="Process",
            command=self._on_process_clicked,
            width=20,
            height=2,
            font=("Arial", 12, "bold")
        )
        self.process_button.pack()

        # Status display
        status_frame = tk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=5)
        tk.Label(status_frame, text="Status:", anchor="w").pack(side=tk.LEFT)
        tk.Label(status_frame, textvariable=self.status_var, anchor="w", fg="blue").pack(side=tk.LEFT, padx=5)

    def _validate_float(self, value_if_allowed: str) -> bool:
        """
        Validate that input is a valid float or partial float input.

        Args:
            value_if_allowed: The value that would be in the entry if allowed

        Returns:
            True if valid float input, False otherwise
        """
        # Allow empty string (user can clear the field)
        if value_if_allowed == "":
            return True

        # Allow minus sign at the start
        if value_if_allowed == "-":
            return True

        # Check for multiple decimal points
        if value_if_allowed.count('.') > 1:
            return False

        # Try to convert to float
        try:
            float(value_if_allowed)
            return True
        except ValueError:
            return False

    def _select_input_file(self):
        """Open file dialog to select input IFC file."""
        filename = filedialog.askopenfilename(
            title="Select IFC File",
            filetypes=[("IFC files", "*.ifc"), ("All files", "*.*")]
        )
        if filename:
            self.input_file_var.set(filename)

    def _select_output_dir(self):
        """Open directory dialog to select output directory."""
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.output_dir_var.set(directory)

    def _on_process_clicked(self):
        """Handle process button click."""
        if self.controller is not None:
            self.controller.on_process_clicked()

    def set_controller(self, controller):
        """
        Set the controller for handling user actions.

        Args:
            controller: Controller object with on_process_clicked method
        """
        self.controller = controller

    def get_values(self) -> dict:
        """
        Get all form values as a dictionary.

        Returns:
            Dictionary with keys: input_file, output_dir, x, y, z, rotation, rotate_first
        """
        return {
            'input_file': self.input_file_var.get(),
            'output_dir': self.output_dir_var.get(),
            'x': float(self.x_var.get() or "0"),
            'y': float(self.y_var.get() or "0"),
            'z': float(self.z_var.get() or "0"),
            'rotation': float(self.rotation_var.get() or "0"),
            'rotate_first': self.rotate_first_var.get()
        }

    def show_status(self, message: str):
        """
        Display a status message.

        Args:
            message: Status message to display
        """
        self.status_var.set(message)

    def show_error(self, message: str):
        """
        Display an error dialog.

        Args:
            message: Error message to display
        """
        messagebox.showerror("Error", message)

    def show_success(self, message: str):
        """
        Display a success dialog.

        Args:
            message: Success message to display
        """
        messagebox.showinfo("Success", message)

    def set_processing(self, is_processing: bool):
        """
        Update UI state based on processing status.

        Args:
            is_processing: True if processing, False otherwise
        """
        if is_processing:
            self.process_button.config(state=tk.DISABLED)
            self.show_status("Processing...")
        else:
            self.process_button.config(state=tk.NORMAL)
            self.show_status("Ready")
