import unittest
from domain.services.optimization.offset_optimizer import OffsetOptimizer
from domain.gcode.commands.move_command import MoveCommand

class TestOffsetOptimizer(unittest.TestCase):
    def test_arc_command_offset(self):
        from domain.gcode.commands.arc_command import ArcCommand
        opt = OffsetOptimizer(offset_x=2, offset_y=3)
        arc = ArcCommand(x=5, y=7, i=0, j=0)
        result, stats = opt.optimize([arc])
        self.assertEqual(result[0].x, 7)
        self.assertEqual(result[0].y, 10)
        self.assertEqual(stats['offset_applied'], 1)
    def test_absolute_offset(self):
        opt = OffsetOptimizer(offset_x=5, offset_y=-3)
        cmds = [MoveCommand(x=10, y=10), MoveCommand(x=0, y=0)]
        result, stats = opt.optimize(cmds)
        self.assertEqual(result[0].x, 15)
        self.assertEqual(result[0].y, 7)
        self.assertEqual(result[1].x, 5)
        self.assertEqual(result[1].y, -3)
        self.assertEqual(stats['offset_applied'], 2)

    def test_no_offset(self):
        opt = OffsetOptimizer()
        cmds = [MoveCommand(x=10, y=10)]
        result, stats = opt.optimize(cmds)
        self.assertEqual(result[0].x, 10)
        self.assertEqual(result[0].y, 10)
        self.assertEqual(stats['offset_applied'], 1)

    def test_relative_offset(self):
        opt = OffsetOptimizer(offset_x=0.5, offset_y=-0.2, is_relative=True)
        cmds = [MoveCommand(x=10, y=15)]
        result, stats = opt.optimize(cmds)
        self.assertEqual(result[0].x, 15)
        self.assertEqual(result[0].y, 12)
        self.assertEqual(stats['offset_applied'], 1)

if __name__ == "__main__":
    unittest.main()
