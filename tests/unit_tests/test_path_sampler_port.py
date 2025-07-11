import pytest
from domain.ports.path_sampler_port import PathSamplerPort
from domain.entities.point import Point

class DummyPathSampler(PathSamplerPort):
    def sample(self, path):
        # Devuelve una lista de puntos fijos para test
        return [Point(x=0, y=0), Point(x=1, y=1)]

def test_sample_returns_points():
    sampler = DummyPathSampler()
    result = list(sampler.sample("dummy_path"))
    assert all(isinstance(p, Point) for p in result)
    assert result[0].x == 0 and result[0].y == 0
    assert result[1].x == 1 and result[1].y == 1

def test_sample_empty_path():
    class EmptySampler(PathSamplerPort):
        def sample(self, path):
            return []
    sampler = EmptySampler()
    result = list(sampler.sample(None))
    assert result == []

def test_sample_type_error():
    class ErrorSampler(PathSamplerPort):
        def sample(self, path):
            raise TypeError("Invalid path type")
    sampler = ErrorSampler()
    with pytest.raises(TypeError):
        sampler.sample(123)

def test_cannot_instantiate_abstract():
    with pytest.raises(TypeError):
        PathSamplerPort()  # noqa: E0110

def test_docstring_present():
    assert PathSamplerPort.__doc__ is not None
    assert "Interfaz" in PathSamplerPort.__doc__ or "Puerto" in PathSamplerPort.__doc__

def test_path_sampler_invalid_step():
    from adapters.input.path_sampler import PathSampler
    try:
        PathSampler(step=0)
        assert False, "Should raise ValueError"
    except ValueError as e:
        assert "step must be positive" in str(e)
