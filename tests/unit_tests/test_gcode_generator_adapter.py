import pytest
from adapters.output.gcode_generator_adapter import GCodeGeneratorAdapter

class DummyLogger:
    def __init__(self):
        self.infos = []
        self.warnings = []
        self.errors = []
    def info(self, msg):
        self.infos.append(msg)
    def warning(self, msg):
        self.warnings.append(msg)
    def error(self, msg):
        self.errors.append(msg)

class DummyI18n:
    def get(self, key, **kwargs):
        return f"{key}:{kwargs.get('value', '')}"

class DummyConfig:
    def __init__(self):
        self.curvature_adjustment_factor = 0.35
        self.minimum_feed_factor = 0.4
        self.step_mm = 1.0
        self.cmd_down = "D"
        self.cmd_up = "U"
        self.dwell_ms = 100
        self.feed = 100
        self.i18n = DummyI18n()
    def get(self, key, default=None):
        if key == "TARGET_WRITE_AREA_MM":
            return [297.0, 210.0]
        if key == "PLOTTER_MAX_AREA_MM":
            return [300.0, 260.0]
        return default

class DummyPathSampler:
    pass

class DummyOptimizer:
    pass

class DummyTransformManager:
    pass

class DummyReferenceMarksGenerator:
    def __init__(self, logger=None, i18n=None):
        pass
    def generate(self, width, height):
        return ["G0 X0 Y0"]

class DummyTrajectoryOptimizer:
    def optimize_order(self, paths, progress_callback=None):
        return paths

# Patch dependencies
import adapters.output.gcode_generator_adapter as gga

gga.ReferenceMarksGenerator = DummyReferenceMarksGenerator
gga.TrajectoryOptimizer = DummyTrajectoryOptimizer


def test_generate_error_on_missing_path_sampler():
    logger = DummyLogger()
    config = DummyConfig()
    adapter = gga.GCodeGeneratorAdapter(
        cmd_down="D", cmd_up="U", dwell_ms=100, feed=100,
        step_mm=1, config=config, logger=logger, i18n=DummyI18n(),
        path_sampler=None, optimizer=DummyOptimizer(), transform_strategies=None,
        max_height_mm=config.get("PLOTTER_MAX_AREA_MM")[1],
        max_width_mm=config.get("PLOTTER_MAX_AREA_MM")[0]
    )
    with pytest.raises(ValueError):
        adapter.generate([], {}, None)
    assert any("ERR_MISSING_PATH_SAMPLER" in msg for msg in logger.errors)

