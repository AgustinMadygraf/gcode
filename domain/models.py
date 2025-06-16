"""
Data models for SVG to G-code pipeline.
"""
from dataclasses import dataclass

@dataclass
class Point:
    """Represents a point in 2D space."""
    x: float
    y: float
