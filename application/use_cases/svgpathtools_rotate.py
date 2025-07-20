"""
Rotación de paths de svgpathtools 90° en sentido horario respecto al origen.
"""
from svgpathtools import Path as SvgPath
from svgpathtools import Line, QuadraticBezier, CubicBezier, Arc

def rotate_svgpathtools_path_90_clockwise(path: SvgPath) -> SvgPath:
    """Rota un svgpathtools.Path 90° horario respecto al origen (x, y) -> (y, -x)."""
    def rotate_point(pt):
        return complex(pt.imag, -pt.real)
    rotated_segments = []
    for seg in path:
        if isinstance(seg, Line):
            rotated_segments.append(Line(rotate_point(seg.start), rotate_point(seg.end)))
        elif isinstance(seg, QuadraticBezier):
            rotated_segments.append(QuadraticBezier(
                rotate_point(seg.start),
                rotate_point(seg.control),
                rotate_point(seg.end)
            ))
        elif isinstance(seg, CubicBezier):
            rotated_segments.append(CubicBezier(
                rotate_point(seg.start),
                rotate_point(seg.control1),
                rotate_point(seg.control2),
                rotate_point(seg.end)
            ))
        elif isinstance(seg, Arc):
            rotated_segments.append(Arc(
                rotate_point(seg.start),
                seg.radius,  # radius is a tuple, not a point
                seg.rotation,
                seg.arc,
                seg.sweep,
                rotate_point(seg.end)
            ))
        else:
            # fallback: try to rotate start and end
            rotated_segments.append(type(seg)(rotate_point(seg.start), rotate_point(seg.end)))
    return SvgPath(*rotated_segments)

def rotate_svgpathtools_paths_90_clockwise(paths):
    """Rota una lista de svgpathtools.Path 90° horario respecto al origen."""
    return [rotate_svgpathtools_path_90_clockwise(p) for p in paths]
