"""
Controller layer for IFC Translate Tool.

Provides the TransformController class that wires together the model and view,
handles user events, manages background processing, and provides user feedback.
"""

import threading
import queue
from src.utils.validation import validate_input_file, validate_output_directory, build_output_path


class TransformController:
    """
    Controller for coordinating IFC transformation workflow.

    Responsibilities:
    - Wire model and view together
    - Validate user inputs before processing
    - Run transformations in background thread
    - Communicate results via queue for thread-safe UI updates
    - Provide user feedback via view
    """

    def __init__(self, model, view, presets_model):
        """
        Initialize controller with model, view, and presets model.

        Args:
            model: IFCTransformModel instance
            view: TransformView instance
            presets_model: PresetsModel instance
        """
        self.model = model
        self.view = view
        self.presets_model = presets_model
        self.result_queue = queue.Queue()

        # Wire controller to view
        view.set_controller(self)

        # Start queue polling for background thread results
        self._start_queue_polling()

        # Load preset list and auto-load last used
        self._refresh_preset_list()
        self.load_last_preset()

    def _start_queue_polling(self):
        """Start periodic queue polling to check for thread results."""
        self.view.root.after(100, self._check_queue)

    def _check_queue(self):
        """
        Check result queue for background thread results.

        This runs periodically (every 100ms) to process results from
        the background transformation thread in a thread-safe manner.
        """
        try:
            # Non-blocking check for results
            result = self.result_queue.get_nowait()

            # Update UI based on result
            self.view.set_processing(False)

            if result['success']:
                self.view.show_success(result['message'])
            else:
                self.view.show_error(result['message'])

        except queue.Empty:
            # No results yet, continue polling
            pass

        # Schedule next queue check
        self.view.root.after(100, self._check_queue)

    def on_process_clicked(self):
        """
        Handle Process button click.

        Validates inputs, starts background transformation thread,
        and updates UI state.
        """
        # Get form values
        values = self.view.get_values()

        # Validate inputs
        try:
            validate_input_file(values['input_file'])
            validate_output_directory(values['output_dir'])
            output_path = build_output_path(values['input_file'], values['output_dir'])

        except ValueError as e:
            # Show validation error to user
            self.view.show_error(str(e))
            return

        # Set UI to processing state
        self.view.set_processing(True)

        # Start background transformation thread
        thread = threading.Thread(
            target=self._run_transformation,
            args=(values, output_path)
        )
        thread.daemon = True
        thread.start()

    def _run_transformation(self, values, output_path):
        """
        Run transformation in background thread.

        This method runs in a separate thread and must NOT make direct UI calls.
        Results are communicated via the result queue.

        Args:
            values: Dictionary of form values from view
            output_path: Path object for output file
        """
        try:
            # Determine rotation value (None if 0)
            rotation_z = values['rotation'] if values['rotation'] != 0 else None

            # Execute transformation
            self.model.transform_file(
                input_path=values['input_file'],
                output_path=str(output_path),
                x=values['x'],
                y=values['y'],
                z=values['z'],
                should_rotate_first=values['rotate_first'],
                rotation_z=rotation_z
            )

            # Put success result in queue
            self.result_queue.put({
                'success': True,
                'message': f'Transformation complete!\nOutput: {output_path}'
            })

        except ValueError as e:
            # Validation error from model
            self.result_queue.put({
                'success': False,
                'message': str(e)
            })

        except Exception as e:
            # Other errors
            self.result_queue.put({
                'success': False,
                'message': f'Transformation failed: {e}'
            })

    def _refresh_preset_list(self):
        """Refresh the preset dropdown with current presets."""
        presets = self.presets_model.list_presets()
        self.view.update_preset_list(presets)

    def on_preset_selected(self):
        """Handle preset selection from dropdown."""
        preset_name = self.view.get_selected_preset()
        if not preset_name:
            return

        presets = self.presets_model.load_presets()
        if preset_name in presets:
            self.view.set_values(presets[preset_name])
            self.presets_model.save_last_used(preset_name)

    def on_save_preset(self):
        """Handle save preset button click."""
        # Get preset name from user
        preset_name = self.view.ask_preset_name()
        if not preset_name:
            return

        # Check for overwrite
        existing_presets = self.presets_model.list_presets()
        if preset_name in existing_presets:
            if not self.view.confirm_overwrite(preset_name):
                return

        # Get current form values (exclude file paths)
        values = self.view.get_values()
        preset_data = {
            'x': values['x'],
            'y': values['y'],
            'z': values['z'],
            'rotation': values['rotation'],
            'rotate_first': values['rotate_first']
        }

        # Save preset
        self.presets_model.save_preset(preset_name, preset_data)
        self.presets_model.save_last_used(preset_name)

        # Refresh UI
        self._refresh_preset_list()
        self.view.set_selected_preset(preset_name)
        self.view.show_status(f"Preset '{preset_name}' saved")

    def on_delete_preset(self):
        """Handle delete preset button click."""
        preset_name = self.view.get_selected_preset()
        if not preset_name:
            self.view.show_error("No preset selected")
            return

        if not self.view.confirm_delete(preset_name):
            return

        # Delete preset
        self.presets_model.delete_preset(preset_name)

        # Clear selection and refresh
        self.view.set_selected_preset('')
        self._refresh_preset_list()
        self.view.show_status(f"Preset '{preset_name}' deleted")

    def load_last_preset(self):
        """Load the last used preset on startup."""
        last_used = self.presets_model.get_last_used()
        if not last_used:
            return

        presets = self.presets_model.load_presets()
        if last_used in presets:
            self.view.set_selected_preset(last_used)
            self.view.set_values(presets[last_used])
