"""
GCodeGenerator: Core logic for SVG to G-code conversion.

- Utiliza PathSampler para muestrear puntos de rutas SVG a intervalos regulares.
- Utiliza TransformManager para aplicar estrategias de transformación a cada punto.
- El método generate() produce una lista de líneas G-code a partir de rutas SVG y atributos.

Ejemplo de uso:
    from domain.gcode_generator import GCodeGenerator
    from domain.path_transform_strategy import MirrorVerticalStrategy
    generator = GCodeGenerator(
        feed=1000,
        cmd_down="M3 S1000",
        cmd_up="M5",
        step_mm=2.0,
        dwell_ms=100,
        max_height_mm=50,
        logger=None,
        transform_strategies=[MirrorVerticalStrategy(25)]
    )
    gcode_lines = generator.generate(paths, svg_attr)
    for line in gcode_lines:
        print(line)
"""

from typing import List, Optional
import numpy as np
from domain.models import Point
from domain.path_transform_strategy import PathTransformStrategy, ScaleStrategy
from infrastructure.path_sampler import PathSampler
from infrastructure.transform_manager import TransformManager

class GCodeGenerator:
    " Class to generate G-code from SVG paths. "
    def __init__(
        self,
        *,
        feed: float,
        cmd_down: str,
        cmd_up: str,
        step_mm: float,
        dwell_ms: int,
        max_height_mm: float,
        logger=None,
        transform_strategies: Optional[List[PathTransformStrategy]] = None
    ):
        self.feed = feed
        self.cmd_down = cmd_down
        self.cmd_up = cmd_up
        self.step_mm = step_mm
        self.dwell_ms = dwell_ms
        self.max_height_mm = max_height_mm
        self.logger = logger
        self.transform_strategies = transform_strategies or []
        # Validar que todas las estrategias implementen PathTransformStrategy
        if self.transform_strategies:
            for s in self.transform_strategies:
                if not isinstance(s, PathTransformStrategy):
                    raise TypeError("Todas las estrategias deben implementar PathTransformStrategy")
        self.path_sampler = PathSampler(self.step_mm, logger=self.logger)
        self.transform_manager = TransformManager(self.transform_strategies, logger=self.logger)

    def _viewbox_scale(self, svg_attr: dict) -> float:
        vb = svg_attr.get("viewBox")
        width = svg_attr.get("width")
        if vb and width:
            try:
                _, _, vb_w, _ = map(float, vb.split())
                width_px = float(width.rstrip("px"))
                return width_px / vb_w
            except ValueError:
                pass
        return 1.0

    def get_svg_bbox(self, paths):
        " Calculate the bounding box of the SVG paths. "
        xs, ys = [], []
        for p in paths:
            for seg in p:
                for t in np.linspace(0, 1, 20):
                    z = seg.point(t)
                    xs.append(z.real)
                    ys.append(z.imag)
        return min(xs), max(xs), min(ys), max(ys)

    def adjust_scale_for_max_height(self, paths, scale, max_height_mm):
        " Adjust the scale to ensure the height does not exceed max_height_mm. "
        _, _, ymin, ymax = self.get_svg_bbox(paths)
        height = abs(ymax - ymin) * scale
        if height > max_height_mm:
            factor = max_height_mm / (abs(ymax - ymin) * scale)
            return scale * factor
        return scale

    def sample_and_transform(self, paths, scale) -> List[List[Point]]:
        """Devuelve una lista de listas de puntos transformados y escalados para cada path."""
        result = []
        for p in paths:
            points = []
            for pt in self.path_sampler.sample(p):
                x, y = self.transform_manager.apply(pt.x, pt.y)
                # Si la estrategia de escalado no está incluida, aplicar el escalado aquí
                if not any(isinstance(s, ScaleStrategy) for s in self.transform_strategies):
                    x, y = x * scale, y * scale
                points.append(Point(x, y))
            result.append(points)
        return result

    def process_points_pipeline(self, paths, scale) -> List[List[Point]]:
        """Pipeline fijo: muestreo -> transformación -> escalado (si corresponde)."""
        result = []
        for p in paths:
            points = []
            for pt in self.path_sampler.sample(p):
                x, y = self.transform_manager.apply(pt.x, pt.y)
                # Si la estrategia de escalado no está incluida, aplicar el escalado aquí
                if not any(isinstance(s, ScaleStrategy) for s in self.transform_strategies):
                    x, y = x * scale, y * scale
                points.append(Point(x, y))
            result.append(points)
        return result

    def generate_gcode_commands(self, all_points: List[List[Point]]) -> List[str]:
        """Genera las líneas de G-code a partir de los puntos procesados."""
        g: List[str] = []
        g += ["G90", "G21", self.cmd_up]
        last_end = None
        for points in all_points:
            if not points:
                continue
            # Si hay un trazo anterior,
            # moverse rápido al inicio del nuevo trazo con el cabezal levantado
            if last_end is not None:
                g.append(self.cmd_up)
                g.append(f"G0 X{points[0].x:.3f} Y{points[0].y:.3f}")
                g.append(f"G4 P{self.dwell_ms / 1000.0:.3f}")
            first_point = True
            path_gcode_count = 0
            for pt in points:
                x_mm, y_mm = pt.x, pt.y
                if first_point:
                    g.extend([
                        self.cmd_down,
                        f"G4 P{self.dwell_ms / 1000.0:.3f}"
                    ])
                    path_gcode_count += 2
                    first_point = False
                g.append(f"G1 X{x_mm:.3f} Y{y_mm:.3f} F{self.feed}")
                path_gcode_count += 1
            g.append(self.cmd_up)
            g.append(f"G4 P{self.dwell_ms / 1000.0:.3f}")
            path_gcode_count += 2
            last_end = (points[-1].x, points[-1].y)
        g += ["M5", "G0 X0 Y0", "(End)"]
        return g

    def generate(self, paths, svg_attr) -> List[str]:
        " Generate G-code from SVG paths. "
        xmin, xmax, ymin, ymax = self.get_svg_bbox(paths)
        scale = self._viewbox_scale(svg_attr)
        scale = self.adjust_scale_for_max_height(paths, scale, self.max_height_mm)
        if self.logger:
            self.logger.info(
                f"Bounding box: xmin={xmin:.3f}, xmax={xmax:.3f}, "
                f"ymin={ymin:.3f}, ymax={ymax:.3f}")
            self.logger.info(f"Scale applied: {scale:.3f}")
        all_points = self.process_points_pipeline(paths, scale)
        gcode = self.generate_gcode_commands(all_points)
        if self.logger:
            self.logger.info(f"G-code lines generated: {len(gcode)}")
        return gcode
