"""
Telemetry processing service - converts F1 telemetry data into sculpture coordinates.
Extracted from original main.py for better modularity.
"""

import numpy as np
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class TelemetryProcessor:
    """Processes F1 telemetry data into 3D sculpture coordinates."""

    @staticmethod
    def calculate_g_forces(speed, distance):
        """
        Calculate G-forces from speed and distance data.
        Returns lateral and longitudinal G-forces.

        Args:
            speed: Speed array in km/h
            distance: Distance array in meters

        Returns:
            Array of G-force values
        """
        # Convert speed from km/h to m/s
        speed_ms = speed / 3.6

        # Calculate acceleration (m/s²)
        # Using finite differences for derivative
        dt = np.gradient(distance) / speed_ms
        dt[dt == 0] = 0.001  # Avoid division by zero

        acceleration = np.gradient(speed_ms) / dt

        # Convert to G-forces (1G = 9.81 m/s²)
        g_force = acceleration / 9.81

        return g_force

    def process_telemetry_to_sculpture(self, telemetry_data) -> Dict[str, Any]:
        """
        Transform telemetry data into 3D sculpture coordinates.
        Returns vertices for rendering with Three.js.

        Args:
            telemetry_data: Pandas DataFrame with telemetry channels

        Returns:
            Dictionary containing vertices, colors, and metadata
        """
        logger.info(f"Processing telemetry data: {len(telemetry_data)} data points")

        # Extract key telemetry channels
        x = telemetry_data['X'].values
        y = telemetry_data['Y'].values
        speed = telemetry_data['Speed'].values
        distance = telemetry_data['Distance'].values

        # Calculate G-forces
        throttle = telemetry_data['Throttle'].values / 100.0  # Normalize
        brake = telemetry_data['Brake'].values

        # Approximate G-forces from speed changes
        speed_ms = speed / 3.6

        # Longitudinal G (acceleration/braking)
        long_g = np.gradient(speed_ms) / 9.81
        long_g = np.clip(long_g * 10, -5, 5)  # Scale and clip

        # Lateral G (approximate from speed and turn radius)
        dx = np.gradient(x)
        dy = np.gradient(y)
        curvature = np.abs(np.gradient(dx) * dy - dx * np.gradient(dy))
        curvature = np.where(curvature > 0, curvature, 0.0001)

        lateral_g = (speed_ms ** 2) / (curvature * 9.81)
        lateral_g = np.clip(lateral_g * 0.1, 0, 5)  # Scale and clip

        # Combined G-force magnitude
        combined_g = np.sqrt(long_g**2 + lateral_g**2)

        # Normalize track coordinates to a reasonable scale
        x_norm = (x - np.mean(x)) / np.std(x) * 100
        y_norm = (y - np.mean(y)) / np.std(y) * 100

        # Z-axis is the combined G-force (extrusion height)
        z = combined_g * 20  # Scale for visibility

        # Create vertices list
        vertices = []
        colors = []

        for i in range(len(x_norm)):
            vertices.append({
                'x': float(x_norm[i]),
                'y': float(y_norm[i]),
                'z': float(z[i]),
                'distance': float(distance[i]),
                'speed': float(speed[i]),
                'gForce': float(combined_g[i]),
                'longG': float(long_g[i]),
                'latG': float(lateral_g[i])
            })

            # Color based on G-force intensity (0-5G range)
            # Green (low G) → Red (high G) gradient
            g_intensity = min(combined_g[i] / 5.0, 1.0)
            colors.append({
                'r': g_intensity,
                'g': 1.0 - g_intensity,
                'b': 0.3
            })

        logger.info(f"Processed sculpture: max G-force={np.max(combined_g):.2f}, avg G-force={np.mean(combined_g):.2f}")

        return {
            'vertices': vertices,
            'colors': colors,
            'metadata': {
                'maxGForce': float(np.max(combined_g)),
                'avgGForce': float(np.mean(combined_g)),
                'maxSpeed': float(np.max(speed)),
                'totalDistance': float(np.max(distance))
            }
        }
