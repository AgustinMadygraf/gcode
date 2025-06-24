from infrastructure.factories.infra_factory import InfraFactory
from pathlib import Path

def test_create_config():
    config = InfraFactory.create_config()
    assert config is not None
    assert hasattr(config, 'feed')

def test_get_logger():
    logger = InfraFactory.get_logger()
    assert logger is not None
    assert hasattr(logger, 'info')
