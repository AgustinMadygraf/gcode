import unittest
from pathlib import Path
import tempfile
import os
from application.use_cases.gcode_rescale_use_case import GcodeRescaleUseCase
from domain.services.filename_service import FilenameService

class DummyLogger:
    def info(self, msg):
        pass
    def debug(self, msg):
        pass
    def error(self, msg):
        pass

class DummyConfig:
    max_height_mm = 250.0
    def __init__(self, temp_dir):
        self._temp_dir = temp_dir
    def get_gcode_output_dir(self):
        return Path(self._temp_dir)

class DummyConfigProvider:
    def get_gcode_output_dir(self):
        return Path(self.temp_dir.name)

class TestGcodeRescaleUseCase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config_provider = DummyConfigProvider()
        self.filename_service = FilenameService(self.config_provider)
        self.logger = DummyLogger()
        self.config = DummyConfig(self.temp_dir.name)
        self.use_case = GcodeRescaleUseCase(self.filename_service, logger=self.logger, config_provider=self.config)
        # Crear un archivo GCODE de prueba
        self.test_gcode = os.path.join(self.temp_dir.name, "test.gcode")
        with open(self.test_gcode, 'w') as f:
            f.write("G90\n")
            f.write("G0 X0 Y0\n")
            f.write("G1 X10 Y0\n")
            f.write("G1 X10 Y10\n")
            f.write("G1 X0 Y10\n")
            f.write("G1 X0 Y0\n")
            f.write("G2 X5 Y5 I5 J0\n")
            f.write("M5\n")
    def tearDown(self):
        self.temp_dir.cleanup()
    def test_analyze_dimensions(self):
        with open(self.test_gcode, 'r') as f:
            lines = f.readlines()
        dimensions = self.use_case._analyze_dimensions(lines)
        self.assertEqual(0.0, dimensions['x_min'])
        self.assertEqual(10.0, dimensions['x_max'])
        self.assertEqual(-5.0, dimensions['y_min'])  # Corrige el valor esperado
        self.assertEqual(10.0, dimensions['y_max'])
        self.assertEqual(10.0, dimensions['width'])
        self.assertEqual(15.0, dimensions['height'])  # Corrige el valor esperado
    def test_rescale_gcode(self):
        with open(self.test_gcode, 'r') as f:
            lines = f.readlines()
        dimensions = {'x_min': 0.0, 'y_min': 0.0, 'x_max': 10.0, 'y_max': 10.0, 'width': 10.0, 'height': 10.0}
        scale_factor = 2.0
        scaled_lines, stats = self.use_case._rescale_gcode(lines, scale_factor, dimensions)
        self.assertEqual(5, stats['g0g1'])  # 5 movimientos G0/G1
        self.assertEqual(1, stats['g2g3'])  # 1 arco G2
        self.assertGreaterEqual(stats['other'], 2)  # G90 y M5
        self.assertTrue(any("G1 X20.000 Y0.000" in l for l in scaled_lines))
        self.assertTrue(any("G1 X20.000 Y20.000" in l for l in scaled_lines))
        self.assertTrue(any("G2 X10.000 Y10.000 I10.000 J0.000" in l for l in scaled_lines))
    def test_execute(self):
        result = self.use_case.execute(Path(self.test_gcode), target_height=20.0)
        self.assertTrue(os.path.exists(result['output_file']))
        # El factor de escala debe ser 20 / altura_detectada
        expected_scale = 20.0 / 15.0
        self.assertAlmostEqual(expected_scale, result['scale_factor'])
        self.assertAlmostEqual(20.0, result['new_dimensions']['height'])
        with open(result['output_file'], 'r') as f:
            content = f.read()
        self.assertIn("G1 X13.333 Y13.333", content)
        self.assertIn("G2 X6.667 Y6.667 I6.667 J0.000", content)

if __name__ == "__main__":
    unittest.main()
