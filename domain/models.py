"""
Data models for SVG to G-code pipeline.
"""
from dataclasses import dataclass

@dataclass
class Point:
    """Represents a point in 2D space."""
    x: float
    y: float

@dataclass(frozen=True)
class DomainSegment:
    """Inmutable segment between two points in 2D."""
    start: Point
    end: Point

    def __post_init__(self):
        if self.start == self.end:
            raise ValueError("A segment cannot have zero length (start == end)")

@dataclass(frozen=True)
class DomainPath:
    """Represents a path as an ordered sequence of connected segments."""
    segments: list
    closed: bool = False

    def __post_init__(self):
        if not self.segments or len(self.segments) == 0:
            raise ValueError("A path must have at least one segment")
        for i in range(len(self.segments) - 1):
            if self.segments[i].end != self.segments[i+1].start:
                raise ValueError(f"Segments {i} and {i+1} are not connected")
        if self.closed and self.segments[-1].end != self.segments[0].start:
            raise ValueError("Closed path must connect last segment to first")

__all__ = [
    "Point",
    "DomainSegment",
    "DomainPath"
]
