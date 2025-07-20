import unittest
from utils.gcode_offset import calcular_offset_y, aplicar_offset_y_a_gcode

class TestGcodeOffsetUtils(unittest.TestCase):
    def test_calcular_offset_y(self):
        plotter_max = (300.0, 260.0)
        target_area = (297.0, 210.0)
        self.assertEqual(calcular_offset_y(plotter_max, target_area), 50.0)

    def test_aplicar_offset_y_a_gcode_linea_g0_g1(self):
        offset = 50.0
        linea = "G1 X10.000 Y20.000"
        esperado = "G1 X10.000 Y70.000"
        self.assertEqual(aplicar_offset_y_a_gcode([linea], offset)[0], esperado)

    def test_aplicar_offset_y_a_gcode_linea_sin_y(self):
        offset = 50.0
        linea = "G1 X10.000"
        # No debe modificar la línea si no hay Y
        self.assertEqual(aplicar_offset_y_a_gcode([linea], offset)[0], linea)

    def test_aplicar_offset_y_a_gcode_linea_no_g0g1(self):
        offset = 50.0
        linea = "M5"
        self.assertEqual(aplicar_offset_y_a_gcode([linea], offset)[0], linea)

    def test_aplicar_offset_y_a_gcode_varias_lineas(self):
        offset = 10.0
        lineas = [
            "G0 X0.000 Y0.000",
            "G1 X5.000 Y5.000",
            "M5"
        ]
        esperado = [
            "G0 X0.000 Y10.000",
            "G1 X5.000 Y15.000",
            "M5"
        ]
        self.assertEqual(aplicar_offset_y_a_gcode(lineas, offset), esperado)

if __name__ == "__main__":
    unittest.main()
