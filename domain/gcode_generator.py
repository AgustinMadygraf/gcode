"""
GCodeGenerator: Core logic for SVG to G-code conversion.
"""
from typing import List
import math
import numpy as np

class GCodeGenerator:
    " Class to generate G-code from SVG paths. "
    def __init__(self, feed, cmd_down, cmd_up, step_mm, dwell_ms, max_height_mm, logger=None):
        self.feed = feed
        self.cmd_down = cmd_down
        self.cmd_up = cmd_up
        self.step_mm = step_mm
        self.dwell_ms = dwell_ms
        self.max_height_mm = max_height_mm
        self.logger = logger

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

    def sample_path(self, path, step: float):
        " Sample points along the SVG path at specified intervals. "
        for seg in path:
            seg_len = seg.length()
            n = max(1, int(math.ceil(seg_len / step)))
            for t in np.linspace(0, 1, n + 1):
                z = seg.point(t)
                yield z.real, z.imag

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

    def generate(self, paths, svg_attr) -> List[str]:
        " Generate G-code from SVG paths. "
        g: List[str] = []
        g += ["G90", "G21", self.cmd_up]
        xmin, xmax, ymin, ymax = self.get_svg_bbox(paths)
        cx, cy = (xmin + xmax) / 2, (ymin + ymax) / 2
        scale = self._viewbox_scale(svg_attr)
        scale = self.adjust_scale_for_max_height(paths, scale, self.max_height_mm)
        if self.logger:
            self.logger.info(
                f"Bounding box: xmin={xmin:.3f}, xmax={xmax:.3f}, "
                f"ymin={ymin:.3f}, ymax={ymax:.3f}"
            )
            self.logger.info(f"Rotation center: cx={cx:.3f}, cy={cy:.3f}")
            self.logger.info(f"Scale applied: {scale:.3f}")
        def rotate180(x, y):
            x2 = 2*cx - x
            y2 = 2*cy - y
            return x2, y2
        def mirror_horizontal(x, y):
            return 2*cx - x, y
        for idx, p in enumerate(paths):
            if self.logger:
                self.logger.info(f"Processing path {idx+1}/{len(paths)}")
            first_point = True
            path_gcode_count = 0
            for x, y in self.sample_path(p, self.step_mm):
                x, y = rotate180(x, y)
                x, y = mirror_horizontal(x, y)
                x_mm, y_mm = x * scale, y * scale
                if first_point:
                    if self.logger:
                        self.logger.info(f"Start of stroke {idx+1}: X={x_mm:.3f}, Y={y_mm:.3f}")
                    if self.logger:
                        msg = (
                            f"Position: X={x_mm:.3f}, "
                            f"Y={y_mm:.3f}, "
                            f"Dwell={self.dwell_ms/1000.0:.3f}"
                        )
                        self.logger.debug(msg)
                    g.extend([
                        f"G0 X{x_mm:.3f} Y{y_mm:.3f}",
                        self.cmd_down,
                        f"G4 P{self.dwell_ms / 1000.0:.3f}"
                    ])
                    path_gcode_count += 3
                    first_point = False
                g.append(f"G1 X{x_mm:.3f} Y{y_mm:.3f} F{self.feed}")
                path_gcode_count += 1
            g += [self.cmd_up, f"G4 P{self.dwell_ms / 1000.0:.3f}"]
            path_gcode_count += 2
            if self.logger:
                msg = (f"End of stroke {idx+1}, "
                      f"commands: {self.cmd_up}, "
                      f"G4 P{self.dwell_ms/1000.0}")
                self.logger.info(msg)
                msg = (f"G-code instructions generated "
                      f"for path {idx+1}: {path_gcode_count}")
                self.logger.info(msg)
        g += ["M5", "G0 X0 Y0", "(End)"]
        if self.logger:
            self.logger.info("Final sequence: M5, G0 X0 Y0, (End)")
        return g
