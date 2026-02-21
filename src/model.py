"""
IFC Transformation Model Layer

This module provides the IFCTransformModel class that wraps IfcPatch's
OffsetObjectPlacements recipe for applying geometric transformations
to IFC files.
"""

import logging
import ifcopenshell
import ifcopenshell.util.unit
import ifcpatch


# Configure logging for debug output
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class IFCTransformModel:
    """
    Model layer for IFC file transformations.

    Wraps IfcPatch's OffsetObjectPlacements recipe to provide
    coordinate transformations (translation and rotation) on IFC files.
    """

    def transform_file(
        self,
        input_path: str,
        output_path: str,
        x: float,
        y: float,
        z: float,
        should_rotate_first: bool,
        rotation_z: float | None = None
    ) -> bool:
        """
        Apply geometric transformation to an IFC file.

        This method applies translation (offset) and optional rotation to all
        objects in an IFC file using IfcPatch's OffsetObjectPlacements recipe.

        Rotation is performed around the Z axis (2D rotation in the horizontal plane).
        The order of operations matters because rotation and translation do not commute:

        - should_rotate_first=True: Apply rotation first, then translate
          (rotation occurs around origin 0,0,0 before moving the object)

        - should_rotate_first=False: Apply translation first, then rotate
          (object is moved first, then rotated around origin 0,0,0)

        Args:
            input_path: Path to input IFC file (string)
            output_path: Path for output IFC file (string)
            x: Translation offset in X direction (metres)
            y: Translation offset in Y direction (metres)
            z: Translation offset in Z direction (metres)
            should_rotate_first: If True, rotate then translate; if False, translate then rotate
            rotation_z: Optional rotation angle around Z axis in decimal degrees.
                       Positive values rotate counter-clockwise when viewed from above.
                       If None, no rotation is applied.

        Returns:
            True if transformation succeeded

        Raises:
            ValueError: If input file is not a valid IFC file
            Exception: If transformation fails for other reasons

        Example:
            >>> model = IFCTransformModel()
            >>> # Translate 100m east, 50m north, no rotation
            >>> model.transform_file("input.ifc", "output.ifc", 100.0, 50.0, 0.0, True)
            True
            >>> # Rotate 90 degrees, then translate
            >>> model.transform_file("input.ifc", "output.ifc", 10.0, 10.0, 0.0, True, 90.0)
            True
        """
        try:
            logger.info(f"Opening IFC file: {input_path}")
            # Open IFC file with path string to capture C++ parse errors
            ifc_file = ifcopenshell.open(input_path)

            # Convert metre offsets to project units
            # unit_scale maps: ifc_project_length * unit_scale = si_metres
            # So: si_metres / unit_scale = ifc_project_length
            unit_scale = ifcopenshell.util.unit.calculate_unit_scale(ifc_file)
            x_proj = x / unit_scale
            y_proj = y / unit_scale
            z_proj = z / unit_scale
            logger.info(f"Project unit scale: {unit_scale} (1 project unit = {unit_scale}m)")
            logger.info(f"Converted offsets from metres ({x}, {y}, {z}) "
                       f"to project units ({x_proj}, {y_proj}, {z_proj})")

            # Build arguments list for OffsetObjectPlacements
            # Format: [x, y, z, should_rotate_first, rotation_angle (optional)]
            arguments = [x_proj, y_proj, z_proj, should_rotate_first]
            if rotation_z is not None:
                arguments.append(rotation_z)
                logger.info(f"Applying transformation: offset=({x_proj}, {y_proj}, {z_proj}), "
                          f"rotate_first={should_rotate_first}, rotation_z={rotation_z}°")
            else:
                logger.info(f"Applying transformation: offset=({x_proj}, {y_proj}, {z_proj}), "
                          f"rotate_first={should_rotate_first}, no rotation")

            # Execute transformation using IfcPatch
            output = ifcpatch.execute({
                "input": str(input_path),
                "file": ifc_file,
                "recipe": "OffsetObjectPlacements",
                "arguments": arguments,
            })

            # Write transformed model to output file
            logger.info(f"Writing output to: {output_path}")
            ifcpatch.write(output, str(output_path))

            logger.info("Transformation completed successfully")
            return True

        except RuntimeError as e:
            # IfcOpenShell raises RuntimeError for invalid IFC files
            # Convert to user-friendly ValueError
            error_msg = f"Invalid IFC file: {e}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        except Exception as e:
            # Catch all other exceptions and provide context
            error_msg = f"Transformation failed: {e}"
            logger.error(error_msg)
            raise Exception(error_msg)
