"""
Servicio de geometría para cálculo de bounding box y centro de paths SVG.
"""
from typing import Tuple, List, Any
import numpy as np

class GeometryService:
    """
    Servicio de dominio para operaciones geométricas sobre paths SVG.
    """
    @staticmethod
    def calculate_bbox(paths: List[Any]) -> Tuple[float, float, float, float]:
        """
        Método público para calcular el bounding box de una lista de paths SVG.
        """
        return GeometryService._calculate_bbox(paths)

    @staticmethod
    def _calculate_bbox(paths: List[Any]) -> Tuple[float, float, float, float]:
        """
        Calcula el bounding box de una lista de paths SVG.
        """
        xs, ys = [], []
        for p in paths:
            for seg in p:
                for t in range(21):
                    z = seg.point(t/20)
                    xs.append(z.real)
                    ys.append(z.imag)
        if not xs or not ys:
            raise ValueError("No points found in paths.")
        return min(xs), max(xs), min(ys), max(ys)

    @staticmethod
    def center(bbox: Tuple[float, float, float, float]) -> Tuple[float, float]:
        """
        Método público para calcular el centro del bounding box dado como una tupla (xmin, xmax, ymin, ymax).
        """
        return GeometryService._center(bbox)

    @staticmethod
    def _center(bbox: Tuple[float, float, float, float]) -> Tuple[float, float]:
        """
        Calcula el centro del bounding box dado como una tupla (xmin, xmax, ymin, ymax).
        """
        xmin, xmax, ymin, ymax = bbox
        return (xmin + xmax) / 2, (ymin + ymax) / 2

    def _fit_ellipse(self, points: np.ndarray) -> Tuple[np.ndarray, np.ndarray, float]:
        """
        Ajusta una elipse a un conjunto de puntos usando el algoritmo Direct Ellipse Fit.
        Implementa el método Fitzgibbon, FitzGibbon y Fisher.
        
        Args:
            points: Array Nx2 de coordenadas (x, y)
            
        Returns:
            Tupla (centro, (semi-eje mayor, semi-eje menor), ángulo de rotación en radianes)
        """
        # Centramos los puntos
        x = points[:, 0]
        y = points[:, 1]

        # Construimos la matriz de diseño D
        design_matrix = np.column_stack([x*x, x*y, y*y, x, y, np.ones(len(x))])

        # Construimos la matriz de restricciones C
        constraint_matrix = np.zeros((6, 6))
        constraint_matrix[0, 2] = 2
        constraint_matrix[2, 0] = 2
        constraint_matrix[1, 1] = -1

        # Resolvemos el sistema generalizado de autovalores
        _, eigenvecs = np.linalg.eig(np.dot(np.linalg.inv(np.dot(design_matrix.T, design_matrix)), constraint_matrix))

        # El autovector correspondiente al único autovalor positivo
        a_vec = np.real_if_close(eigenvecs[:, 0])

        # Parámetros de la elipse: a*x^2 + b*xy + c*y^2 + d*x + e*y + f = 0
        a, b, c, d, e, f = a_vec

        # Extraemos parámetros de la elipse
        # Centro de la elipse
        x0 = (2*c*d - b*e) / (b*b - 4*a*c)
        y0 = (2*a*e - b*d) / (b*b - 4*a*c)
        center = np.array([x0, y0])

        # Determinamos ángulo de rotación
        if abs(b) < 1e-10:
            if a > c:
                angle = 0
            else:
                angle = np.pi/2
        else:
            angle = 0.5 * np.arctan2(b, a - c)

        # Coeficientes rotados
        cos_phi = np.cos(angle)
        sin_phi = np.sin(angle)
        a_prime = a*cos_phi*cos_phi + b*sin_phi*cos_phi + c*sin_phi*sin_phi
        c_prime = a*sin_phi*sin_phi - b*sin_phi*cos_phi + c*cos_phi*cos_phi
        g = f + a*x0*x0 + b*x0*y0 + c*y0*y0 + d*x0 + e*y0

        # Semi-ejes
        semi_major = np.sqrt(-g / a_prime) if a_prime < 0 else np.sqrt(-g / c_prime)
        semi_minor = np.sqrt(-g / c_prime) if a_prime < 0 else np.sqrt(-g / a_prime)

        # Ordenamos los ejes
        if semi_major < semi_minor:
            semi_major, semi_minor = semi_minor, semi_major
            angle += np.pi/2

        # Normalizamos el ángulo al rango [0, π]
        angle = angle % np.pi

        return center, np.array([semi_major, semi_minor]), angle
