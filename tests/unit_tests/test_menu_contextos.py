import types
import pytest
import builtins
from application.orchestrator import ApplicationOrchestrator
from infrastructure.i18n.i18n_service import I18nService
from cli.i18n import MESSAGES

class DummyPresenter:
    def __init__(self):
        self.messages = []
        self.i18n = I18nService(MESSAGES, default_lang="es")
    def print(self, msg, color=None):
        self.messages.append((msg, color))
    def print_option(self, msg):
        self.messages.append((msg, None))
    def input(self, _prompt):
        # Simula siempre salir
        return '0'

class DummyLogger:
    def info(self, *_a, **_k): pass
    def warning(self, *_a, **_k): pass
    def debug(self, *_a, **_k): pass
    def error(self, *_a, **_k): pass
    def option(self, *_a, **_k): pass

class DummyI18n:
    def get(self, key, **_kwargs):
        return key

@pytest.fixture
def dummy_orchestrator():
    class DummyContainer: error_handler = types.SimpleNamespace(wrap_execution=lambda *a, **k: {'success': True})
    # Adaptar a la nueva firma: container, services, mode_strategy, i18n, args
    services = {
        'filename_service': None,
        'config': None,
        'event_bus': None,
        'workflows': {},
        'operations': {1: lambda: None, 2: lambda: None}
    }
    orchestrator = ApplicationOrchestrator(
        container=DummyContainer(),
        services=services,
        mode_strategy=None,
        i18n=DummyI18n(),
        args=None
    )
    orchestrator.logger = DummyLogger()
    orchestrator.input = lambda prompt: '0'
    orchestrator.input_with_label = lambda prompt: '0'
    return orchestrator

@pytest.fixture(autouse=True)
def mock_input(monkeypatch):
    monkeypatch.setattr(builtins, 'input', lambda _: '0')

def test_menu_batch_mode(dummy_orchestrator):  # pylint: disable=redefined-outer-name
    dummy_orchestrator.args = types.SimpleNamespace(no_interactive=True)
    dummy_orchestrator.input_with_label = lambda prompt: '0'
    assert dummy_orchestrator.select_operation_mode() is None

def test_menu_input_output_args(dummy_orchestrator):  # pylint: disable=redefined-outer-name
    dummy_orchestrator.args = types.SimpleNamespace(input='a.svg', output='b.gcode', no_interactive=False)
    dummy_orchestrator.input_with_label = lambda prompt: '0'
    assert dummy_orchestrator.select_operation_mode() == 1
    dummy_orchestrator.args = types.SimpleNamespace(input='a.gcode', output='b.gcode', no_interactive=False)
    dummy_orchestrator.input_with_label = lambda prompt: '0'
    assert dummy_orchestrator.select_operation_mode() == 2

def test_menu_no_files(monkeypatch, dummy_orchestrator):  # pylint: disable=redefined-outer-name
    # Forzar que no haya archivos SVG ni GCODE
    monkeypatch.setattr('adapters.input.svg_file_selector_adapter._find_svg_files_recursively', lambda d: [])
    monkeypatch.setattr('os.listdir', lambda d: [])
    dummy_orchestrator.args = None
    # Mock input para evitar lectura real
    dummy_orchestrator.input_with_label = lambda prompt: '0'
    with pytest.raises(SystemExit) as excinfo:
        dummy_orchestrator.select_operation_mode()
    assert excinfo.value.code == 0
