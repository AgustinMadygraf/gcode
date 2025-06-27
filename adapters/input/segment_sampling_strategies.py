"""
Estrategias de muestreo para segmentos SVG.
Cada función implementa una estrategia para un tipo de segmento.

- sample_line: líneas rectas
- sample_bezier: curvas de Bezier (cúbica o cuadrática)
- sample_arc: arcos elípticos
- sample_uniform: fallback genérico
- estimate_curvature: utilidad para curvas

Todas retornan una lista de Point.
"""

import numpy as np
from svgpathtools import Line, CubicBezier, QuadraticBezier, Arc
from domain.models.point import Point
from typing import List


def sample_line(line: Line) -> List[Point]:
    """Muestreo optimizado para línea recta (solo extremos)."""
    return [Point(line.start.real, line.start.imag), Point(line.end.real, line.end.imag)]


def sample_bezier(bezier, max_segment_length: float, curvature_factor: float) -> List[Point]:
    """Muestreo adaptativo para curvas de Bezier basado en curvatura local."""
    points = []
    length = bezier.length()
    n_segments = max(int(length / max_segment_length), 2)
    ts = np.linspace(0, 1, n_segments + 1)
    initial_points = [bezier.point(t) for t in ts]
    points.append(Point(initial_points[0].real, initial_points[0].imag))
    for i in range(len(initial_points) - 1):
        p1 = initial_points[i]
        p2 = initial_points[i + 1]
        t_mid = (ts[i] + ts[i + 1]) / 2
        curvature = estimate_curvature(bezier, t_mid)
        segment_length = abs(p2 - p1)
        density = max(1, int(curvature * segment_length * curvature_factor))
        if density > 1:
            sub_ts = np.linspace(ts[i], ts[i + 1], density + 1)[1:-1]
            for t in sub_ts:
                pt = bezier.point(t)
                points.append(Point(pt.real, pt.imag))
        if i < len(initial_points) - 2:
            points.append(Point(p2.real, p2.imag))
    last = initial_points[-1]
    points.append(Point(last.real, last.imag))
    return points


def sample_arc(arc: Arc, min_segment_length: float) -> List[Point]:
    """Muestreo optimizado para arcos basado en radio y ángulo barrido."""
    points = []
    radius = arc.radius.real
    angle = abs(arc.delta)
    n_segments = max(int(angle * radius / min_segment_length), 2)
    for t in np.linspace(0, 1, n_segments + 1):
        pt = arc.point(t)
        points.append(Point(pt.real, pt.imag))
    return points


def sample_uniform(segment, num_points: int) -> List[Point]:
    """Muestreo uniforme para cualquier tipo de segmento (fallback)."""
    return [Point(segment.point(t).real, segment.point(t).imag) for t in np.linspace(0, 1, num_points)]


def estimate_curvature(curve, t: float) -> float:
    """Estimación numérica de la curvatura local en t para Bezier/curvas SVG."""
    dt = 1e-6
    t1 = max(0, t - dt)
    t2 = min(1, t + dt)
    p0 = curve.point(t1)
    p2 = curve.point(t2)
    d1 = (p2 - p0) / (t2 - t1)
    p0 = curve.point(max(0, t - 2*dt))
    p1 = curve.point(t)
    p2 = curve.point(min(1, t + 2*dt))
    d2_approx = (p0 - 2*p1 + p2) / (dt*dt)
    d1_mag = abs(d1)
    d2_mag = abs(d2_approx)
    if d1_mag < 1e-10:
        return 0
    curvature = d2_mag / (1 + d1_mag**2)**1.5
    return curvature
