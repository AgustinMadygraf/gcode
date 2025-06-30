"""
Test para el bucle infinito en InteractiveModeStrategy.
"""
import unittest
from unittest.mock import MagicMock
from cli.modes.interactive import InteractiveModeStrategy

class TestInteractiveModeStrategy(unittest.TestCase):
    def test_run_loop_exits_on_salir(self):
        # Preparar mocks
        app = MagicMock()
        app.container.error_handler.wrap_execution.return_value = {'success': True}
        app.operations.get.return_value = MagicMock(execute=MagicMock(return_value=None))
        app.i18n.get.side_effect = lambda key, **kwargs: key
        app.presenter.print = MagicMock()
        # Simular que el usuario elige una operación válida y luego "salir"
        app.orchestrator.select_operation_mode.side_effect = [1, 'salir']
        # Ejecutar
        strategy = InteractiveModeStrategy()
        result = strategy.run(app)
        # Verificar que el bucle termina y se muestra mensaje de salida
        self.assertEqual(result, 0)
        app.presenter.print.assert_any_call("INFO_EXIT", color='yellow')

if __name__ == '__main__':
    unittest.main()
