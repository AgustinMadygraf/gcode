"""
Detector de elipses en paths SVG.
"""
from typing import Optional, Tuple
import numpy as np
from svgpathtools import Path
from domain.services.geometry_utils import sample_path_points

class EllipseDetector:
    def try_detect_ellipse(self, path: Path, tolerance: float = 0.1) -> Optional[Tuple[complex, float, float, float]]:
        """
        Intenta detectar si un path es una elipse.
        Args:
            path: Path SVG a analizar
            tolerance: Tolerancia para la desviación de puntos
        Returns:
            Tupla (centro, radio_x, radio_y, ángulo) si es una elipse, None en caso contrario
        """
        if not path.isclosed():
            return None
        num_samples = min(100, max(20, int(path.length() / 5)))
        points = sample_path_points(path, num_samples)
        try:
            center, axes, angle = self._fit_ellipse(points)
            rx, ry = axes[0], axes[1]
            cos_angle = np.cos(angle)
            sin_angle = np.sin(angle)
            max_error = 0
            for x, y in points:
                dx = x - center[0]
                dy = y - center[1]
                x_rot = dx * cos_angle + dy * sin_angle
                y_rot = -dx * sin_angle + dy * cos_angle
                distance = ((x_rot / rx)**2 + (y_rot / ry)**2)**0.5
                error = abs(distance - 1.0)
                max_error = max(max_error, error)
            if max_error <= tolerance:
                return complex(center[0], center[1]), rx, ry, angle
        except:
            pass
        return None

    def _fit_ellipse(self, points: np.ndarray) -> Tuple[np.ndarray, np.ndarray, float]:
        x = points[:, 0]
        y = points[:, 1]
        D = np.column_stack([x*x, x*y, y*y, x, y, np.ones(len(x))])
        C = np.zeros((6, 6))
        C[0, 2] = 2
        C[2, 0] = 2
        C[1, 1] = -1
        _, eigenvecs = np.linalg.eig(np.dot(np.linalg.inv(np.dot(D.T, D)), C))
        a_vec = np.real_if_close(eigenvecs[:, 0])
        a, b, c, d, e, f = a_vec
        x0 = (2*c*d - b*e) / (b*b - 4*a*c)
        y0 = (2*a*e - b*d) / (b*b - 4*a*c)
        center = np.array([x0, y0])
        if abs(b) < 1e-10:
            angle = 0 if a > c else np.pi/2
        else:
            angle = 0.5 * np.arctan2(b, a - c)
        cos_phi = np.cos(angle)
        sin_phi = np.sin(angle)
        a_prime = a*cos_phi*cos_phi + b*sin_phi*cos_phi + c*sin_phi*sin_phi
        c_prime = a*sin_phi*sin_phi - b*sin_phi*cos_phi + c*cos_phi*cos_phi
        g = f + a*x0*x0 + b*x0*y0 + c*y0*y0 + d*x0 + e*y0
        semi_major = np.sqrt(-g / a_prime) if a_prime < 0 else np.sqrt(-g / c_prime)
        semi_minor = np.sqrt(-g / c_prime) if a_prime < 0 else np.sqrt(-g / a_prime)
        if semi_major < semi_minor:
            semi_major, semi_minor = semi_minor, semi_major
            angle += np.pi/2
        angle = angle % np.pi
        return center, np.array([semi_major, semi_minor]), angle
