from adapters.input.config_adapter import ConfigAdapter
from domain.compression_config import CompressionConfig

class DummyConfig:
    def __init__(self):
        self.marker_feed_rate = 42
        self.tool_type = "pen"
        self.pen_double_pass = True
        self._debug_flags = {"test": True}
        self._compression = {
            "ENABLED": False,
            "GEOMETRIC_TOLERANCE": 0.5,
            "USE_ARCS": False,
            "USE_RELATIVE_MOVES": True,
            "REMOVE_REDUNDANCIES": False
        }
    def get(self, key, default=None):
        if key == "COMPRESSION":
            return self._compression
        return getattr(self, key, default)
    def get_debug_flag(self, name):
        return self._debug_flags.get(name, False)


def test_get_compression_config():
    adapter = ConfigAdapter(DummyConfig())
    cfg = adapter.get_compression_config()
    assert isinstance(cfg, CompressionConfig)
    assert not cfg.enabled
    assert cfg.geometric_tolerance == 0.5
    assert not cfg.use_arcs
    assert cfg.use_relative_moves
    assert not cfg.remove_redundancies

def test_marker_feed_rate():
    adapter = ConfigAdapter(DummyConfig())
    assert adapter.marker_feed_rate == 42

def test_tool_type():
    adapter = ConfigAdapter(DummyConfig())
    assert adapter.tool_type == "pen"

def test_pen_double_pass():
    adapter = ConfigAdapter(DummyConfig())
    assert adapter.pen_double_pass is True

def test_get_method():
    adapter = ConfigAdapter(DummyConfig())
    assert adapter.get("marker_feed_rate") == 42
    assert adapter.get("nonexistent", 123) == 123

def test_get_debug_flag():
    adapter = ConfigAdapter(DummyConfig())
    assert adapter.get_debug_flag("test") is True
    assert adapter.get_debug_flag("other") is False

def test_get_remove_border_true():
    from adapters.output.gcode_generation_config_helper import GcodeGenerationConfigHelper
    class DummyConfigRemoveBorderTrue:
        def get(self, key, default=None):
            if key == "REMOVE_BORDER_RECTANGLE":
                return False
            return default
    cfg = DummyConfigRemoveBorderTrue()
    assert GcodeGenerationConfigHelper.get_remove_border(cfg) is False

def test_get_remove_border_exception():
    from adapters.output.gcode_generation_config_helper import GcodeGenerationConfigHelper
    class DummyConfigRemoveBorderException:
        def get(self, key, default=None):
            raise Exception("fail")
    cfg = DummyConfigRemoveBorderException()
    assert GcodeGenerationConfigHelper.get_remove_border(cfg) is True

def test_get_use_relative_moves_from_data():
    from adapters.output.gcode_generation_config_helper import GcodeGenerationConfigHelper
    class DummyConfigRelativeMovesData:
        def __init__(self):
            self._data = {"COMPRESSION": {"USE_RELATIVE_MOVES": True}}
        def get(self, _key, default=None):
            return default
    cfg = DummyConfigRelativeMovesData()
    assert GcodeGenerationConfigHelper.get_use_relative_moves(cfg) is True

def test_get_use_relative_moves_fallback():
    from adapters.output.gcode_generation_config_helper import GcodeGenerationConfigHelper
    class DummyConfigRelativeMovesFallback:
        def get(self, key, default=None):
            if key == "USE_RELATIVE_MOVES":
                return True
            return default
    cfg = DummyConfigRelativeMovesFallback()
    assert GcodeGenerationConfigHelper.get_use_relative_moves(cfg) is True

def test_get_use_relative_moves_exception():
    from adapters.output.gcode_generation_config_helper import GcodeGenerationConfigHelper
    class DummyConfigRelativeMovesException:
        def get(self, key, default=None):
            raise Exception("fail")
    cfg = DummyConfigRelativeMovesException()
    assert GcodeGenerationConfigHelper.get_use_relative_moves(cfg) is False

def test_domain_segment_valid():
    from domain.models import Point, DomainSegment
    seg = DomainSegment(Point(0, 0), Point(1, 1))
    assert seg.start == Point(0, 0)
    assert seg.end == Point(1, 1)

def test_domain_segment_zero_length():
    from domain.models import Point, DomainSegment
    try:
        DomainSegment(Point(0, 0), Point(0, 0))
        assert False, "Should raise ValueError"
    except ValueError as e:
        assert "zero length" in str(e)

def test_domain_path_valid():
    from domain.models import Point, DomainSegment, DomainPath
    seg1 = DomainSegment(Point(0, 0), Point(1, 1))
    seg2 = DomainSegment(Point(1, 1), Point(2, 2))
    path = DomainPath([seg1, seg2], closed=False)
    assert path.segments == [seg1, seg2]
    assert not path.closed

def test_domain_path_not_connected():
    from domain.models import Point, DomainSegment, DomainPath
    seg1 = DomainSegment(Point(0, 0), Point(1, 1))
    seg2 = DomainSegment(Point(2, 2), Point(3, 3))
    try:
        DomainPath([seg1, seg2], closed=False)
        assert False, "Should raise ValueError"
    except ValueError as e:
        assert "not connected" in str(e)

def test_domain_path_empty():
    from domain.models import DomainPath
    try:
        DomainPath([], closed=False)
        assert False, "Should raise ValueError"
    except ValueError as e:
        assert "at least one segment" in str(e)

def test_domain_path_closed():
    from domain.models import Point, DomainSegment, DomainPath
    seg1 = DomainSegment(Point(0, 0), Point(1, 1))
    seg2 = DomainSegment(Point(1, 1), Point(0, 0))
    path = DomainPath([seg1, seg2], closed=True)
    assert path.closed

def test_domain_path_closed_not_connected():
    from domain.models import Point, DomainSegment, DomainPath
    seg1 = DomainSegment(Point(0, 0), Point(1, 1))
    seg2 = DomainSegment(Point(1, 1), Point(2, 2))
    try:
        DomainPath([seg1, seg2], closed=True)
        assert False, "Should raise ValueError"
    except ValueError as e:
        assert "Closed path must connect" in str(e)

def test_gcode_compression_factory_disable():
    from adapters.output.gcode_compression_factory import GcodeCompressionFactory
    class DummyConfig:
        disable_gcode_compression = True
    result = GcodeCompressionFactory.get_compression_service(DummyConfig())
    assert result is None

def test_gcode_builder_helper_empty_points():
    from adapters.output.gcode_builder_helper import GCodeBuilderHelper
    helper = GCodeBuilderHelper(cmd_down="D", cmd_up="U", dwell_ms=100)
    # all_points contiene una lista vacía
    result = helper.build([[]], feed_fn=lambda p: 100)
    assert result is not None  # Solo se prueba que no falla y retorna algo

def test_gcode_analyzer_no_x_values():
    from adapters.output.gcode_analyzer import GCodeAnalyzer
    lines = ["G01 Y10", "G01 Z5", "G01"]
    width = GCodeAnalyzer.get_width_from_gcode_lines(lines)
    assert width == 0.0

def test_curvature_feed_calculator_none_points():
    from adapters.output.curvature_feed_calculator import CurvatureFeedCalculator
    class DummyStrategy:
        pass
    calc = CurvatureFeedCalculator(DummyStrategy())
    result = calc.calculate_curvature(None, None, None)
    assert result is None

def test_feed_rate_strategy_none_curvature():
    from adapters.output.feed_rate_strategy import FeedRateStrategy
    strat = FeedRateStrategy(base_feed=100)
    result = strat.adjust_feed(curvature=None)
    assert result == 100
