# Domain Models and Invariant Rules

This document describes the main domain models of the GCode project, their invariants, and associated business rules. It serves as a reference for developers and for the evolution of the design.

---

## DomainSegment

**Description:**
Immutable value object representing a segment between two points in 2D.

**Attributes:**
- `start: Point` (start point)
- `end: Point` (end point)

**Invariants:**
- `start` and `end` must be valid instances of `Point`.
- A segment cannot have zero length (`start != end`).

**Business rules:**
- Segments are immutable: they cannot be modified after creation.
- Two segments with the same points (regardless of order) may be considered equal depending on context.

---

## DomainPath

**Description:**
Entity representing a path formed by an ordered sequence of segments.

**Attributes:**
- `segments: List[DomainSegment]`
- (Optional) `closed: bool` (indicates if the path is closed)

**Invariants:**
- The segment list cannot be empty.
- Segments must be connected: the `end` of one segment must match the `start` of the next.
- If `closed` is `True`, the `end` of the last segment must match the `start` of the first.

**Business rules:**
- A `DomainPath` is responsible for validating its own consistency upon creation.
- Transformation methods (translation, rotation, scaling) must return new instances.

---

## Invariant Test Example

```python
# test_domain_segment.py
def test_segment_no_zero_length():
    with pytest.raises(ValueError):
        DomainSegment(Point(0,0), Point(0,0))

def test_path_segments_connected():
    s1 = DomainSegment(Point(0,0), Point(1,0))
    s2 = DomainSegment(Point(1,0), Point(2,0))
    DomainPath([s1, s2])  # No error
    s3 = DomainSegment(Point(3,0), Point(4,0))
    with pytest.raises(ValueError):
        DomainPath([s1, s3])
```

---

## Notes
- These models should be used in domain ports and services, avoiding exposure of external library types.
- Invariants must be validated in constructors or factory methods.
- It is recommended to document additional rules in the code's docstrings.
