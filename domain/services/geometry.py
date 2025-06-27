"""
Servicio de geometría para cálculo de bounding box y centro de paths SVG.
"""
from typing import Tuple, List, Any, Dict, Optional, Union
import numpy as np
from svgpathtools import Path, Line, CubicBezier, QuadraticBezier, Arc
import complex as c

class GeometryService:
    """
    Servicio de dominio para operaciones geométricas sobre paths SVG.
    """
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
    def _center(bbox: Tuple[float, float, float, float]) -> Tuple[float, float]:
        """
        Calcula el centro del bounding box dado como una tupla (xmin, xmax, ymin, ymax).
        """
        xmin, xmax, ymin, ymax = bbox
        return (xmin + xmax) / 2, (ymin + ymax) / 2
        
    def try_detect_circle(self, path: Path, tolerance: float = 0.05) -> Optional[Tuple[complex, float]]:
        """
        Intenta detectar si un path es un círculo.
        
        Args:
            path: Path SVG a analizar
            tolerance: Tolerancia relativa para considerar un círculo (0.05 = 5%)
            
        Returns:
            Tupla (centro, radio) si es un círculo, None en caso contrario
        """
        # Un círculo debe ser un path cerrado
        if not path.isclosed():
            return None
            
        # Muestreamos el path para obtener puntos
        points = []
        num_samples = min(100, max(20, int(path.length() / 5)))
        
        for i in range(num_samples):
            t = i / num_samples
            point = path.point(t * path.length())
            points.append((point.real, point.imag))
            
        points = np.array(points)
        
        # Calculamos el centro aproximado usando el promedio
        center_x = np.mean(points[:, 0])
        center_y = np.mean(points[:, 1])
        center = complex(center_x, center_y)
        
        # Calculamos distancias al centro
        distances = np.sqrt((points[:, 0] - center_x)**2 + (points[:, 1] - center_y)**2)
        
        # Calculamos el radio promedio
        avg_radius = np.mean(distances)
        
        # Verificamos si las distancias son consistentes con un círculo
        # (todas deben estar dentro de la tolerancia)
        rel_deviation = np.abs(distances - avg_radius) / avg_radius
        max_deviation = np.max(rel_deviation)
        
        if max_deviation <= tolerance:
            return center, avg_radius
        
        return None
        
    def try_detect_rectangle(self, path: Path, angle_tol: float = 5.0, ratio_tol: float = 0.05) -> Optional[List[complex]]:
        """
        Intenta detectar si un path es un rectángulo.
        
        Args:
            path: Path SVG a analizar
            angle_tol: Tolerancia en grados para ángulos rectos
            ratio_tol: Tolerancia para comparación de lados opuestos
            
        Returns:
            Lista de esquinas si es un rectángulo, None en caso contrario
        """
        # Un rectángulo debe ser un path cerrado
        if not path.isclosed():
            return None
            
        # Un rectángulo normalmente tiene 4 segmentos (o múltiplos en algunos casos)
        if len(path) % 4 != 0 or len(path) < 4:
            return None
            
        # Si tiene más de 4 segmentos, verificamos si son líneas rectas
        if len(path) > 4:
            for segment in path:
                if not isinstance(segment, Line):
                    return None
                    
            # Simplificamos el path uniendo líneas colineales
            path = self._simplify_path_lines(path)
            
            # Si después de simplificar no tenemos 4 segmentos, no es un rectángulo
            if len(path) != 4:
                return None
                
        # Ahora debemos tener exactamente 4 segmentos
        # Verificamos que sean líneas y formén ángulos rectos
        corners = [path[0].start]
        for i in range(4):
            segment = path[i]
            
            # Verificamos que sea una línea
            if not isinstance(segment, Line):
                return None
                
            corners.append(segment.end)
            
            # Verificamos ángulos rectos
            next_segment = path[(i + 1) % 4]
            current_dir = segment.end - segment.start
            next_dir = next_segment.end - next_segment.start
            
            # Calculamos el ángulo entre segmentos
            dot_product = (current_dir.real * next_dir.real + current_dir.imag * next_dir.imag)
            current_mag = abs(current_dir)
            next_mag = abs(next_dir)
            
            # Evitar división por cero
            if current_mag < 1e-10 or next_mag < 1e-10:
                return None
                
            cos_angle = dot_product / (current_mag * next_mag)
            # Limitamos cos_angle al rango [-1, 1]
            cos_angle = max(-1.0, min(1.0, cos_angle))
            angle_rad = np.arccos(cos_angle)
            angle_deg = np.degrees(angle_rad)
            
            # Verificamos si el ángulo está cerca de 90 grados
            if abs(angle_deg - 90) > angle_tol:
                return None
                
        # Verificamos que lados opuestos sean paralelos y de igual longitud
        len1 = abs(path[0].end - path[0].start)
        len2 = abs(path[2].end - path[2].start)
        len3 = abs(path[1].end - path[1].start)
        len4 = abs(path[3].end - path[3].start)
        
        # Comparamos longitudes de lados opuestos
        if abs(len1 - len2) / max(len1, len2) > ratio_tol or abs(len3 - len4) / max(len3, len4) > ratio_tol:
            return None
            
        return corners[:4]  # Devolvemos las 4 esquinas
        
    def try_detect_ellipse(self, path: Path, tolerance: float = 0.1) -> Optional[Tuple[complex, float, float, float]]:
        """
        Intenta detectar si un path es una elipse.
        
        Args:
            path: Path SVG a analizar
            tolerance: Tolerancia para la desviación de puntos
            
        Returns:
            Tupla (centro, radio_x, radio_y, ángulo) si es una elipse, None en caso contrario
        """
        # Una elipse debe ser un path cerrado
        if not path.isclosed():
            return None
            
        # Muestreamos el path para obtener puntos
        points = []
        num_samples = min(100, max(20, int(path.length() / 5)))
        
        for i in range(num_samples):
            t = i / num_samples
            point = path.point(t * path.length())
            points.append((point.real, point.imag))
            
        points = np.array(points)
        
        try:
            # Usamos ajuste elíptico directo
            center, axes, angle = self._fit_ellipse(points)
            
            # Verificamos la calidad del ajuste
            rx, ry = axes[0], axes[1]
            cos_angle = np.cos(angle)
            sin_angle = np.sin(angle)
            
            # Calculamos distancias de puntos a la elipse teórica
            max_error = 0
            for x, y in points:
                # Transformamos el punto al sistema de coordenadas de la elipse
                dx = x - center[0]
                dy = y - center[1]
                
                # Rotamos el punto
                x_rot = dx * cos_angle + dy * sin_angle
                y_rot = -dx * sin_angle + dy * cos_angle
                
                # Calculamos la distancia normalizada a la elipse
                distance = ((x_rot / rx)**2 + (y_rot / ry)**2)**0.5
                error = abs(distance - 1.0)
                max_error = max(max_error, error)
                
            # Si el error es menor que la tolerancia, es una elipse
            if max_error <= tolerance:
                return complex(center[0], center[1]), rx, ry, angle
            
        except:
            pass
            
        return None
    
    def _simplify_path_lines(self, path: Path) -> Path:
        """
        Simplifica un path combinando líneas colineales.
        """
        if len(path) <= 1:
            return path
            
        new_segments = [path[0]]
        
        for i in range(1, len(path)):
            prev_segment = new_segments[-1]
            current_segment = path[i]
            
            if not (isinstance(prev_segment, Line) and isinstance(current_segment, Line)):
                new_segments.append(current_segment)
                continue
                
            # Verificamos colinealidad
            prev_dir = prev_segment.end - prev_segment.start
            curr_dir = current_segment.end - current_segment.start
            
            prev_mag = abs(prev_dir)
            curr_mag = abs(curr_dir)
            
            # Evitar división por cero
            if prev_mag < 1e-10 or curr_mag < 1e-10:
                new_segments.append(current_segment)
                continue
                
            # Normalizamos vectores
            prev_dir_norm = prev_dir / prev_mag
            curr_dir_norm = curr_dir / curr_mag
            
            # Producto vectorial para verificar paralelismo
            cross_product = prev_dir_norm.real * curr_dir_norm.imag - prev_dir_norm.imag * curr_dir_norm.real
            
            if abs(cross_product) < 1e-6:  # Son colineales
                # Reemplazamos los dos segmentos por uno solo
                new_segments[-1] = Line(prev_segment.start, current_segment.end)
            else:
                new_segments.append(current_segment)
                
        return Path(*new_segments)
    
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
        D = np.column_stack([x*x, x*y, y*y, x, y, np.ones(len(x))])
        
        # Construimos la matriz de restricciones C
        C = np.zeros((6, 6))
        C[0, 2] = 2
        C[2, 0] = 2
        C[1, 1] = -1
        
        # Resolvemos el sistema generalizado de autovalores
        _, eigenvecs = np.linalg.eig(np.dot(np.linalg.inv(np.dot(D.T, D)), C))
        
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
