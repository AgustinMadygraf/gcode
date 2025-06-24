import pytest
from infrastructure.factories.adapter_factory import AdapterFactory
from infrastructure.config.config import Config
from pathlib import Path

def test_create_config_adapter():
    config = Config(Path("infrastructure/config/config.json"))
    adapter = AdapterFactory.create_config_adapter(config)
    assert adapter is not None
    assert hasattr(adapter, 'get') or hasattr(adapter, 'get_config')

def test_create_logger_adapter():
    logger = AdapterFactory.create_logger_adapter()
    assert logger is not None
    assert hasattr(logger, 'info')

def test_create_svg_loader():
    loader = AdapterFactory.create_svg_loader("dummy.svg")
    assert loader is not None
    assert hasattr(loader, 'get_paths')
