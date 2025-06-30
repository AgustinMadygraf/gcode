import pytest
from infrastructure.config.config import Config
from cli.presenters.cli_presenter import CliPresenter

class DummyI18n:
    def __init__(self):
        self._messages = {'es': {}, 'en': {}}
        self._default_lang = 'es'
    def get(self, key, **kwargs):
        return key

class DummyLogger:
    def info(self, msg, **kwargs):
        pass
    def warning(self, msg, **kwargs):
        pass
    def error(self, msg, **kwargs):
        pass
    def option(self, msg):
        pass
    def debug(self, msg, **kwargs):
        pass

def test_surface_preset_scaling(monkeypatch):
    config = Config()
    config._data['SURFACE_PRESETS'] = {'BIG': [1000.0, 1000.0]}
    config._data['PLOTTER_MAX_AREA_MM'] = [300.0, 200.0]
    presenter = CliPresenter(i18n=DummyI18n(), color_service=None, logger_instance=DummyLogger())
    # Simular selección del preset 'BIG' y respuesta 'sí' a escalar
    monkeypatch.setattr(presenter, 'prompt_selection', lambda prompt, options: 1)
    monkeypatch.setattr(presenter, 'prompt_yes_no', lambda prompt: True)
    monkeypatch.setattr(presenter, 'input', lambda prompt, color=None: '0')
    dims, preset = presenter.prompt_surface_preset(config._data['SURFACE_PRESETS'], config.plotter_max_area_mm)
    assert dims[0] <= 300.0 and dims[1] <= 200.0
    assert preset == 'BIG'

def test_surface_preset_custom(monkeypatch):
    config = Config()
    config._data['SURFACE_PRESETS'] = {'A4': [210.0, 297.0]}
    config._data['PLOTTER_MAX_AREA_MM'] = [300.0, 200.0]
    presenter = CliPresenter(i18n=DummyI18n(), color_service=None, logger_instance=DummyLogger())
    # Simular selección de opción custom y valores válidos
    monkeypatch.setattr(presenter, 'prompt_selection', lambda prompt, options: 2)
    monkeypatch.setattr(presenter, 'input', lambda prompt, color=None: '100' if 'ancho' in prompt else '150')
    dims, preset = presenter.prompt_surface_preset(config._data['SURFACE_PRESETS'], config.plotter_max_area_mm)
    assert dims == [100.0, 150.0]
    assert preset == 'CUSTOM'
