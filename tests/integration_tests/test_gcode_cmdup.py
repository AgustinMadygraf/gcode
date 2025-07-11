"""
Test para verificar que el comando CMD_UP separa correctamente los trazos en el G-code generado.
"""
import unittest
import sys
import os

from tests.mocks.mock_strategy import MockStrategy
from adapters.output.gcode_generator_adapter import GCodeGeneratorAdapter
from domain.services.optimization.optimization_chain import OptimizationChain
from application.use_cases.gcode_generation.gcode_generation_service import GCodeGenerationService
from adapters.input.path_sampler import PathSampler
from tests.mocks.mock_geometry import DummySegment
from tests.mocks.mock_config import DummyConfig

class DummyLogger:
    def info(self, *a, **k): pass
    def error(self, *a, **k): pass
    def debug(self, *a, **k): pass
    def warning(self, *a, **k): pass

class DummyI18n:
    def get(self, key, default=None, **_kwargs):
        return default or key
    def info(self, *a, **k): pass
    def warning(self, *a, **k): pass
    def error(self, *a, **k): pass
    def debug(self, *a, **k): pass

class TestGCodeCMDUP(unittest.TestCase):
    def test_cmd_up_separates_strokes(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            seg1 = DummySegment(start=(0,0), end=(5,0))
            seg2 = DummySegment(start=(10,0), end=(15,0))
            paths = [[seg1], [seg2]]  # Dos trazos separados
            svg_attr = {"viewBox": "0 0 20 10", "width": "20"}
            generator = GCodeGeneratorAdapter(
                path_sampler=PathSampler(1),
                feed=1000,
                cmd_down="M3 S1000",
                cmd_up="M5",
                step_mm=1,
                dwell_ms=100,
                max_height_mm=DummyConfig(tmpdir).plotter_max_area_mm[1],
                logger=DummyLogger(),
                i18n=DummyI18n(),
                transform_strategies=[MockStrategy()],
                optimizer=OptimizationChain(),  # Inyectar la cadena de optimización
                config=DummyConfig(tmpdir)  # Mock config
            )
            print(f"[DEBUG] paths: {paths}")  # Print temporal para inspección
            gcode_service = GCodeGenerationService(generator)
            gcode = gcode_service.generate(paths, svg_attr)
            # Debe haber al menos dos ocurrencias de CMD_UP (M5) separando los trazos
            cmd_up_count = sum(1 for line in gcode if line.strip() == "M5")
            self.assertGreaterEqual(cmd_up_count, 2)
            # Debe haber un G0, G4, M5 o M3 después de cada M5 excepto el último
            m5_indices = [i for i, line in enumerate(gcode) if line.strip() == "M5"]
            for idx in m5_indices[:-1]:
                next_line = gcode[idx+1].strip()
                self.assertTrue(
                    next_line.startswith("G4") or
                    next_line.startswith("G0") or
                    next_line.startswith("M5") or
                    next_line.startswith("M3"),
                    f"Línea inesperada tras M5: {next_line}"
                )

    def test_path_sampler_direct(self):
        sampler = PathSampler(1)
        seg = DummySegment(start=(0,0), end=(5,0))
        points = list(sampler.sample([seg]))
        print(f"[DEBUG] Puntos generados por PathSampler: {points}")
        self.assertGreaterEqual(len(points), 2)

    def test_sample_transform_pipeline_direct(self):
        from adapters.output.sample_transform_pipeline import SampleTransformPipeline
        from infrastructure.transform_manager import TransformManager
        sampler = PathSampler(1)
        transform_manager = TransformManager([MockStrategy()])
        pipeline = SampleTransformPipeline(sampler, transform_manager, 1.0)
        seg = DummySegment(start=(0,0), end=(5,0))
        points_list = pipeline.process([[seg]])
        print(f"[DEBUG] Puntos generados por pipeline: {points_list}")
        self.assertGreaterEqual(len(points_list[0]), 2)

if __name__ == "__main__":
    unittest.main()
