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

    def __init__(self, model, view):
        """
        Initialize controller with model and view.

        Args:
            model: IFCTransformModel instance
            view: TransformView instance
        """
        self.model = model
        self.view = view
        self.result_queue = queue.Queue()

        # Wire controller to view
        view.set_controller(self)

        # Start queue polling for background thread results
        self._start_queue_polling()

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
