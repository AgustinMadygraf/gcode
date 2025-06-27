import unittest
from domain.services.optimization.line_optimizer import LineOptimizer
from domain.gcode.commands.move_command import MoveCommand
from domain.gcode.commands.tool_up_command import ToolUpCommand
from domain.gcode.commands.tool_down_command import ToolDownCommand

class TestLineOptimizer(unittest.TestCase):
    def test_optimize_horizontal_line(self):
        # Crear una secuencia de comandos que representan una línea horizontal
        commands = [
            ToolDownCommand("M3 S1000"),  # Bajar herramienta
            MoveCommand(10.0, 36.0, feed=1000),  # Inicio
            MoveCommand(10.539, 36.0),  # Incremento
            MoveCommand(11.078, 36.0),  # Incremento
            MoveCommand(11.617, 36.0),  # Incremento
            MoveCommand(12.156, 36.0),  # Incremento
            MoveCommand(12.695, 36.0),  # Incremento
            ToolUpCommand("M5")  # Subir herramienta
        ]
        
        # Crear optimizador y procesar los comandos
        optimizer = LineOptimizer()
        optimized, metrics = optimizer.optimize(commands)
        
        # Verificar que se han consolidado los comandos correctamente
        self.assertEqual(len(optimized), 3)  # Debe quedar: ToolDown, Move, ToolUp
        self.assertEqual(metrics["segments_removed"], 5)  # Se eliminaron 5 segmentos (ajustado a la lógica actual)
        self.assertEqual(metrics["lines_optimized"], 1)  # Se optimizó 1 línea
        
        # Verificar que el movimiento resultante va del inicio al final
        move_cmd = optimized[1]
        self.assertIsInstance(move_cmd, MoveCommand)
        self.assertEqual(move_cmd.x, 12.695)
        self.assertEqual(move_cmd.y, 36.0)
        self.assertEqual(move_cmd.feed, 1000)

    def test_preserve_different_y_coordinates(self):
        # Verificar que no se mezclan coordenadas Y diferentes
        commands = [
            MoveCommand(10.0, 36.0, feed=1000),
            MoveCommand(11.0, 36.0),
            MoveCommand(12.0, 37.0),  # Y diferente
            MoveCommand(13.0, 37.0)
        ]
        
        optimizer = LineOptimizer()
        optimized, metrics = optimizer.optimize(commands)
        
        # Deben quedar 2 movimientos (uno por cada valor Y)
        self.assertEqual(len(optimized), 2)
        self.assertEqual(optimized[0].y, 36.0)
        self.assertEqual(optimized[0].x, 11.0)
        self.assertEqual(optimized[1].y, 37.0)
        self.assertEqual(optimized[1].x, 13.0)

if __name__ == '__main__':
    unittest.main()
