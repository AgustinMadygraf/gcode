"""
PathSampler: Utility to sample points along SVG paths at fixed intervals.

- step: distance between sampled points (SVG units)
- sample(path): receives a list of SVG segments and produces (x, y) tuples at regular intervals.
- Raises ValueError if step <= 0.

Usage example:
    sampler = PathSampler(step=2.0)
    for x, y in sampler.sample(path):
        print(x, y)
"""
import math
import numpy as np
from domain.entities.point import Point
from domain.ports.path_sampler_port import PathSamplerPort
from domain.ports.logger_port import LoggerPort


class PathSampler(PathSamplerPort):
    """Samples points along SVG paths at specified intervals."""

    def __init__(self, step: float, logger: LoggerPort = None):
        if step <= 0:
            raise ValueError("step must be positive")
        self.step = step
        self.logger = logger

    def sample(self, path):
        """Yield Point objects sampled along the path at the given step interval.
        Args:
            path: Iterable of segments, each with .length() and .point(t).
        Yields:
            Point: Sampled (x, y) coordinates.
        """
        for seg in path:
            seg_len = seg.length()
            n = max(1, int(math.ceil(seg_len / self.step)))
            for t in np.linspace(0, 1, n + 1):
                z = seg.point(t)
                #                if self.logger:
                #                    self.logger.debug(f"Sampled point: ({z.real:.3f}, {z.imag:.3f})")
                yield Point(z.real, z.imag)
