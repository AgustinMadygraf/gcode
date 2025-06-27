"""
Módulo: segment_sampling_registry.py

Define un registro de estrategias de muestreo para cada tipo de segmento SVG.
"""
from svgpathtools import Line, CubicBezier, QuadraticBezier, Arc
from adapters.input.segment_sampling_strategies import sample_line, sample_bezier, sample_arc, sample_uniform

class SegmentSamplingRegistry:
    def __init__(self, max_segment_length, curvature_factor, min_segment_length):
        self.registry = {
            Line: lambda seg: sample_line(seg),
            CubicBezier: lambda seg: sample_bezier(seg, max_segment_length, curvature_factor),
            QuadraticBezier: lambda seg: sample_bezier(seg, max_segment_length, curvature_factor),
            Arc: lambda seg: sample_arc(seg, min_segment_length),
        }
        self.fallback = lambda seg: sample_uniform(seg, 10)

    def sample(self, segment):
        for seg_type, strategy in self.registry.items():
            if isinstance(segment, seg_type):
                return strategy(segment)
        return self.fallback(segment)
