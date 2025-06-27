"""
Path: adapters/input/adaptive_path_sampler.py

Implementación de un muestreador adaptativo de paths SVG que
aplica mayor densidad de puntos en áreas de alta curvatura.
"""

import numpy as np
from svgpathtools import Path, Line, CubicBezier, QuadraticBezier, Arc
from typing import List, Tuple, Dict, Any, Optional

from domain.ports.path_sampler_port import PathSamplerPort
from domain.models.svg_path import SVGPath
from domain.models.point import Point
from domain.services.geometry import GeometryService
from domain.services.detectors.circle_detector import CircleDetector
from domain.services.detectors.rectangle_detector import RectangleDetector
from domain.services.detectors.ellipse_detector import EllipseDetector


class AdaptivePathSampler(PathSamplerPort):
    """
    Muestreador adaptativo que determina la densidad de puntos basándose
    en la curvatura y características geométricas del path.
    
    Características:
    - Menor densidad de puntos en segmentos rectos
    - Mayor densidad de puntos en áreas de alta curvatura
    - Reconocimiento de primitivas geométricas (círculos, rectángulos)
    """
    
    def __init__(self, 
                 min_segment_length: float = 0.1,
                 max_segment_length: float = 5.0,
                 curvature_factor: float = 1.0,
                 min_angle_change: float = 5.0,
                 enable_primitive_detection: bool = True):
        """
        Inicializa el muestreador adaptativo.
        
        Args:
            min_segment_length: Longitud mínima de segmentos en puntos de alta curvatura
            max_segment_length: Longitud máxima de segmentos en áreas rectas
            curvature_factor: Factor de escala para relacionar curvatura con densidad
            min_angle_change: Cambio mínimo de ángulo (grados) para aumentar densidad
            enable_primitive_detection: Activa/desactiva detección de primitivas geométricas
        """
        self.min_segment_length = min_segment_length
        self.max_segment_length = max_segment_length
        self.curvature_factor = curvature_factor
        self.min_angle_change = np.radians(min_angle_change)
        self.enable_primitive_detection = enable_primitive_detection
        self.geometry_service = GeometryService()
        
    def sample(self, svg_path: SVGPath) -> List[Point]:
        """
        Muestrea un path SVG con densidad variable según la curvatura.
        
        Args:
            svg_path: El path SVG a muestrear
            
        Returns:
            Lista de puntos muestreados con densidad adaptativa
        """
        # Primero intentamos detectar si es una primitiva geométrica
        if self.enable_primitive_detection:
            primitive_points = self._try_primitive_detection(svg_path)
            if primitive_points:
                return primitive_points
                
        # Si no es una primitiva o la detección está desactivada, usamos muestreo adaptativo
        return self._adaptive_sampling(svg_path)
    
    def _adaptive_sampling(self, svg_path: SVGPath) -> List[Point]:
        """
        Realiza el muestreo adaptativo basado en curvatura para un path genérico.
        
        Args:
            svg_path: Path SVG a muestrear
            
        Returns:
            Lista de puntos con densidad adaptativa
        """
        points = []
        
        # Convertimos el SVGPath a un objeto Path de svgpathtools
        path = svg_path.path
        
        # Calculamos la longitud total del path
        length = path.length()
        
        # Iteramos a través de cada segmento del path
        for segment in path:
            segment_length = segment.length()
            
            if segment_length < self.min_segment_length:
                # Para segmentos muy pequeños, solo tomamos los puntos extremos
                start = segment.start
                points.append(Point(start.real, start.imag))
                continue
            
            # Determinamos el método de muestreo según el tipo de segmento
            if isinstance(segment, Line):
                # Para líneas rectas, usamos menor densidad
                segment_points = self._sample_line(segment)
            elif isinstance(segment, (CubicBezier, QuadraticBezier)):
                # Para curvas de Bezier, usamos muestreo basado en curvatura
                segment_points = self._sample_bezier(segment)
            elif isinstance(segment, Arc):
                # Para arcos, usamos muestreo uniforme según radio
                segment_points = self._sample_arc(segment)
            else:
                # Para otros tipos, fallback a muestreo uniforme
                segment_points = self._sample_uniform(segment, 10)
                
            # Añadimos los puntos del segmento (excepto el último para evitar duplicados)
            points.extend(segment_points[:-1])
        
        # Añadimos el último punto del path
        end = path[-1].end
        points.append(Point(end.real, end.imag))
        
        return points
    
    def _try_primitive_detection(self, svg_path: SVGPath) -> Optional[List[Point]]:
        """
        Intenta detectar si el path es una primitiva geométrica y devuelve
        una representación optimizada si lo es.
        
        Args:
            svg_path: Path SVG a analizar
            
        Returns:
            Lista de puntos optimizada si es una primitiva, None en caso contrario
        """
        path = svg_path.path
        
        # Círculo
        circle_info = CircleDetector().try_detect_circle(path)
        if circle_info:
            center, radius = circle_info
            return self._generate_circle_points(center, radius)
            
        # Rectángulo
        rect_info = RectangleDetector().try_detect_rectangle(path)
        if rect_info:
            corners = rect_info
            return [Point(c.real, c.imag) for c in corners]
            
        # Elipse
        ellipse_info = EllipseDetector().try_detect_ellipse(path)
        if ellipse_info:
            center, rx, ry, phi = ellipse_info
            return self._generate_ellipse_points(center, rx, ry, phi)
            
        # No es una primitiva reconocible
        return None
    
    def _sample_line(self, line: Line) -> List[Point]:
        """Muestreo optimizado para línea recta"""
        points = []
        start, end = line.start, line.end
        
        # Para líneas, solo necesitamos los extremos
        points.append(Point(start.real, start.imag))
        points.append(Point(end.real, end.imag))
        
        return points
    
    def _sample_bezier(self, bezier) -> List[Point]:
        """Muestreo adaptativo para curvas de Bezier basado en curvatura"""
        points = []
        length = bezier.length()
        
        # Número inicial de segmentos basado en longitud
        n_segments = max(int(length / self.max_segment_length), 2)
        
        # Primera aproximación con muestreo uniforme
        ts = np.linspace(0, 1, n_segments + 1)
        initial_points = [bezier.point(t) for t in ts]
        points.append(Point(initial_points[0].real, initial_points[0].imag))
        
        # Refinamos el muestreo basado en curvatura
        for i in range(len(initial_points) - 1):
            p1 = initial_points[i]
            p2 = initial_points[i + 1]
            
            # Estimamos curvatura en este segmento
            t_mid = (ts[i] + ts[i + 1]) / 2
            curvature = self._estimate_curvature(bezier, t_mid)
            
            # Ajustamos la densidad según curvatura
            segment_length = abs(p2 - p1)
            density = max(1, int(curvature * segment_length * self.curvature_factor))
            
            if density > 1:
                # Si la curvatura justifica más puntos, subdividimos
                sub_ts = np.linspace(ts[i], ts[i + 1], density + 1)[1:-1]
                for t in sub_ts:
                    pt = bezier.point(t)
                    points.append(Point(pt.real, pt.imag))
                    
            # Añadimos el punto final de este segmento
            if i < len(initial_points) - 2:  # Evitamos duplicar el último punto
                points.append(Point(p2.real, p2.imag))
        
        # Añadimos el último punto
        last = initial_points[-1]
        points.append(Point(last.real, last.imag))
        
        return points
    
    def _sample_arc(self, arc: Arc) -> List[Point]:
        """Muestreo optimizado para arcos basado en radio y ángulo"""
        points = []
        
        # El número de segmentos depende del radio y el ángulo barrido
        radius = arc.radius.real  # Asumimos radio uniforme para simplicidad
        angle = abs(arc.delta)  # Ángulo barrido en radianes
        
        # Más segmentos para arcos largos o de radio grande
        n_segments = max(int(angle * radius / self.min_segment_length), 2)
        
        # Muestreo uniforme del arco
        for t in np.linspace(0, 1, n_segments + 1):
            pt = arc.point(t)
            points.append(Point(pt.real, pt.imag))
            
        return points
    
    def _sample_uniform(self, segment, num_points: int) -> List[Point]:
        """Muestreo uniforme para cualquier tipo de segmento"""
        points = []
        
        for t in np.linspace(0, 1, num_points):
            pt = segment.point(t)
            points.append(Point(pt.real, pt.imag))
            
        return points
    
    def _estimate_curvature(self, curve, t: float) -> float:
        """
        Estima la curvatura en un punto dado de la curva.
        
        Args:
            curve: Curva a analizar
            t: Parámetro t donde calcular curvatura (0-1)
            
        Returns:
            Valor estimado de curvatura (mayor valor = curva más pronunciada)
        """
        # Derivada primera
        dt = 1e-6  # Delta pequeño para derivadas numéricas
        t1 = max(0, t - dt)
        t2 = min(1, t + dt)
        
        p0 = curve.point(t1)
        p2 = curve.point(t2)
        
        # Derivada primera (aproximación por diferencia central)
        d1 = (p2 - p0) / (t2 - t1)
        
        # Derivada segunda
        p0 = curve.point(max(0, t - 2*dt))
        p1 = curve.point(t)
        p2 = curve.point(min(1, t + 2*dt))
        
        d2_approx = (p0 - 2*p1 + p2) / (dt*dt)
        
        # Calcula curvatura: |f''| / (1 + f'^2)^(3/2)
        d1_mag = abs(d1)
        d2_mag = abs(d2_approx)
        
        if d1_mag < 1e-10:  # Previene división por cero
            return 0
            
        curvature = d2_mag / (1 + d1_mag**2)**1.5
        return curvature
    
    def _generate_circle_points(self, center, radius: float) -> List[Point]:
        """Genera puntos para un círculo con densidad óptima"""
        points = []
        
        # Calculamos el número óptimo de segmentos según el radio
        # (regla empírica: para círculos de radio r, usar aproximadamente π*r/2 segmentos)
        n_segments = max(8, int(np.pi * radius / self.min_segment_length))
        
        # Generamos puntos equidistantes en el círculo
        for i in range(n_segments):
            angle = 2 * np.pi * i / n_segments
            x = center.real + radius * np.cos(angle)
            y = center.imag + radius * np.sin(angle)
            points.append(Point(x, y))
            
        # Cerramos el círculo
        points.append(points[0])
        
        return points
    
    def _generate_ellipse_points(self, center, rx: float, ry: float, phi: float) -> List[Point]:
        """Genera puntos para una elipse con densidad óptima"""
        points = []
        
        # Calculamos perímetro aproximado y determinamos número de segmentos
        perimeter = np.pi * (3*(rx + ry) - np.sqrt((3*rx + ry) * (rx + 3*ry)))
        n_segments = max(8, int(perimeter / self.min_segment_length))
        
        # Matriz de rotación
        cos_phi = np.cos(phi)
        sin_phi = np.sin(phi)
        
        # Generamos puntos en la elipse
        for i in range(n_segments):
            angle = 2 * np.pi * i / n_segments
            # Coordenadas sin rotar
            x0 = rx * np.cos(angle)
            y0 = ry * np.sin(angle)
            
            # Aplicamos rotación
            x = center.real + x0 * cos_phi - y0 * sin_phi
            y = center.imag + x0 * sin_phi + y0 * cos_phi
            
            points.append(Point(x, y))
        
        # Cerramos la elipse
        points.append(points[0])
        
        return points
