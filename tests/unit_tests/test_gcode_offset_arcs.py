import unittest
from utils.gcode_offset import aplicar_offset_y_a_gcode

class TestGcodeOffsetArcs(unittest.TestCase):
    def test_aplicar_offset_y_a_gcode_g2_g3(self):
        offset = 100.0
        lineas = [
            "G2 X10.000 Y20.000 I5.000 J0.000",
            "G3 X15.000 Y25.000 I-5.000 J0.000"
        ]
        esperado = [
            "G2 X10.000 Y120.000 I5.000 J0.000",
            "G3 X15.000 Y125.000 I-5.000 J0.000"
        ]
        self.assertEqual(aplicar_offset_y_a_gcode(lineas, offset), esperado)

if __name__ == "__main__":
    unittest.main()
