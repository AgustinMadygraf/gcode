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
from adapters.input.segment_sampling_strategies import (
    sample_line, sample_bezier, sample_arc, sample_uniform
)
from adapters.input.primitive_point_generators import generate_circle_points, generate_ellipse_points


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
                 enable_primitive_detection: bool = True,
                 circle_detector=None,
                 rectangle_detector=None,
                 ellipse_detector=None):
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
        self.circle_detector = circle_detector or CircleDetector()
        self.rectangle_detector = rectangle_detector or RectangleDetector()
        self.ellipse_detector = ellipse_detector or EllipseDetector()
        
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
                segment_points = sample_line(segment)
            elif isinstance(segment, (CubicBezier, QuadraticBezier)):
                # Para curvas de Bezier, usamos muestreo basado en curvatura
                segment_points = sample_bezier(segment, self.max_segment_length, self.curvature_factor)
            elif isinstance(segment, Arc):
                # Para arcos, usamos muestreo uniforme según radio
                segment_points = sample_arc(segment, self.min_segment_length)
            else:
                # Para otros tipos, fallback a muestreo uniforme
                segment_points = sample_uniform(segment, 10)
                
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
        circle_info = self.circle_detector.try_detect_circle(path)
        if circle_info:
            center, radius = circle_info
            from adapters.input.primitive_point_generators import generate_circle_points
            return generate_circle_points(center, radius, self.min_segment_length)
            
        # Rectángulo
        rect_info = self.rectangle_detector.try_detect_rectangle(path)
        if rect_info:
            corners = rect_info
            return [Point(c.real, c.imag) for c in corners]
            
        # Elipse
        ellipse_info = self.ellipse_detector.try_detect_ellipse(path)
        if ellipse_info:
            center, rx, ry, phi = ellipse_info
            from adapters.input.primitive_point_generators import generate_ellipse_points
            return generate_ellipse_points(center, rx, ry, phi, self.min_segment_length)
            
        # No es una primitiva reconocible
        return None
    
    def _sample_line(self, line: Line) -> List[Point]:
        """Muestreo optimizado para línea recta"""
        # Deprecated: use sample_line strategy
        return sample_line(line)
    
    def _sample_bezier(self, bezier) -> List[Point]:
        """Muestreo adaptativo para curvas de Bezier basado en curvatura"""
        # Deprecated: use sample_bezier strategy
        return sample_bezier(bezier, self.max_segment_length, self.curvature_factor)
    
    def _sample_arc(self, arc: Arc) -> List[Point]:
        """Muestreo optimizado para arcos basado en radio y ángulo"""
        # Deprecated: use sample_arc strategy
        return sample_arc(arc, self.min_segment_length)
    
    def _sample_uniform(self, segment, num_points: int) -> List[Point]:
        """Muestreo uniforme para cualquier tipo de segmento"""
        # Deprecated: use sample_uniform strategy
        return sample_uniform(segment, num_points)
    
    def _estimate_curvature(self, curve, t: float) -> float:
        """
        Estima la curvatura en un punto dado de la curva.
        
        Args:
            curve: Curva a analizar
            t: Parámetro t donde calcular curvatura (0-1)
            
        Returns:
            Valor estimado de curvatura (mayor valor = curva más pronunciada)
        """
        # Deprecated: use estimate_curvature from strategies
        from adapters.input.segment_sampling_strategies import estimate_curvature
        return estimate_curvature(curve, t)
