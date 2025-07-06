"""
Test unitario para la función de rotación de paths 90° en sentido horario.
"""
from domain.entities.point import Point
from domain.entities.segment import Segment
from domain.entities.path import Path as DomainPath
from domain.services.geometry_rotate import rotate_point_90_clockwise, rotate_segment_90_clockwise, rotate_path_90_clockwise

def test_rotate_point_90_clockwise():
    p = Point(1, 2)
    rp = rotate_point_90_clockwise(p)
    assert rp.x == 2 and rp.y == -1

def test_rotate_segment_90_clockwise():
    s = Segment(Point(1, 0), Point(0, 1))
    rs = rotate_segment_90_clockwise(s)
    assert rs.start.x == 0 and rs.start.y == -1
    assert rs.end.x == 1 and rs.end.y == 0

def test_rotate_path_90_clockwise():
    path = DomainPath(segments=[Segment(Point(1, 0), Point(0, 1))])
    rpath = rotate_path_90_clockwise(path)
    assert rpath.segments[0].start.x == 0 and rpath.segments[0].start.y == -1
    assert rpath.segments[0].end.x == 1 and rpath.segments[0].end.y == 0
