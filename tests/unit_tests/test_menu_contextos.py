import types
import pytest
from application.orchestrator import ApplicationOrchestrator

class DummyPresenter:
    def __init__(self):
        self.messages = []
    def print(self, msg, color=None):
        self.messages.append((msg, color))
    def print_option(self, msg):
        self.messages.append((msg, None))
    def input(self, prompt):
        # Simula siempre salir
        return '0'

@pytest.fixture
def dummy_orchestrator(monkeypatch):
    class DummyContainer: error_handler = types.SimpleNamespace(wrap_execution=lambda *a, **k: {'success': True})
    orchestrator = ApplicationOrchestrator(
        container=DummyContainer(),
        presenter=DummyPresenter(),
        filename_service=None,
        config=None,
        event_bus=None,
        workflows={},
        operations={1: lambda: None, 2: lambda: None},
        mode_strategy=None,
        args=None
    )
    return orchestrator

def test_menu_batch_mode(dummy_orchestrator):
    dummy_orchestrator.args = types.SimpleNamespace(no_interactive=True)
    assert dummy_orchestrator.select_operation_mode() is None

def test_menu_input_output_args(dummy_orchestrator):
    dummy_orchestrator.args = types.SimpleNamespace(input='a.svg', output='b.gcode', no_interactive=False)
    assert dummy_orchestrator.select_operation_mode() == 1
    dummy_orchestrator.args = types.SimpleNamespace(input='a.gcode', output='b.gcode', no_interactive=False)
    assert dummy_orchestrator.select_operation_mode() == 2

def test_menu_no_files(monkeypatch, dummy_orchestrator):
    # Forzar que no haya archivos SVG ni GCODE
    monkeypatch.setattr('adapters.input.svg_file_selector_adapter._find_svg_files_recursively', lambda d: [])
    monkeypatch.setattr('os.listdir', lambda d: [])
    dummy_orchestrator.args = None
    # Simula que el usuario elige salir
    import pytest
    with pytest.raises(SystemExit) as excinfo:
        dummy_orchestrator.select_operation_mode()
    assert excinfo.value.code == 0
