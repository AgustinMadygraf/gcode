
"""
Rotación de paths de svgpathtools 90° en sentido horario respecto al origen, con soporte de logging.
"""
from svgpathtools import Path as SvgPath
from svgpathtools import Line, QuadraticBezier, CubicBezier, Arc
from infrastructure.logger_helper import LoggerHelper

class SvgpathtoolsRotate(LoggerHelper):
    """
    Clase para rotar paths de svgpathtools 90° horario respecto al origen, con logging opcional.
    """
    def __init__(self, config=None, logger=None):
        super().__init__(config=config, logger=logger)

    def rotate_svgpathtools_path_90_clockwise(self, path: SvgPath) -> SvgPath:
        """Rota un svgpathtools.Path 90° horario respecto al origen (x, y) -> (y, -x)."""
        def rotate_point(pt):
            return complex(pt.imag, -pt.real)

        # Debug antes de rotar
        all_points = [pt for seg in path for pt in [seg.start, seg.end]]
        if all_points:
            min_x = min(pt.real for pt in all_points)
            max_x = max(pt.real for pt in all_points)
            min_y = min(pt.imag for pt in all_points)
            max_y = max(pt.imag for pt in all_points)
            self._debug(f"[SvgpathtoolsRotate] BEFORE: bbox=({min_x:.2f},{min_y:.2f})-({max_x:.2f},{max_y:.2f}), first_points={[str(pt) for pt in all_points[:3]]}")

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
        rotated_path = SvgPath(*rotated_segments)

        # Debug después de rotar
        all_points_rot = [pt for seg in rotated_path for pt in [seg.start, seg.end]]
        if all_points_rot:
            min_xr = min(pt.real for pt in all_points_rot)
            max_xr = max(pt.real for pt in all_points_rot)
            min_yr = min(pt.imag for pt in all_points_rot)
            max_yr = max(pt.imag for pt in all_points_rot)
            self._debug(f"[SvgpathtoolsRotate] AFTER: bbox=({min_xr:.2f},{min_yr:.2f})-({max_xr:.2f},{max_yr:.2f}), first_points={[str(pt) for pt in all_points_rot[:3]]}")

        return rotated_path

    def rotate_svgpathtools_paths_90_clockwise(self, paths):
        """Rota una lista de svgpathtools.Path 90° horario respecto al origen."""
        return [self.rotate_svgpathtools_path_90_clockwise(p) for p in paths]
