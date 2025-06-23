"""
Tests para FilenameService (capa de aplicación).
"""
import unittest
from pathlib import Path
from application.use_cases.file_output.filename_service import FilenameService
import tempfile
import os

class TestFilenameService(unittest.TestCase):
    def test_next_filename(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            service = FilenameService(output_dir)
            svg_file = output_dir / "test.svg"
            svg_file.touch()  # Simula existencia del SVG
            # No hay archivos G-code aún
            fname = service.next_filename(svg_file)
            self.assertTrue(str(fname).endswith("test_v00.gcode"))
            # Simula existencia de test_v00.gcode
            (output_dir / "test_v00.gcode").touch()
            fname2 = service.next_filename(svg_file)
            self.assertTrue(str(fname2).endswith("test_v01.gcode"))

if __name__ == "__main__":
    unittest.main()
