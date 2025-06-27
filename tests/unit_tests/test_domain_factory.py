from infrastructure.factories.domain_factory import DomainFactory
from tests.mocks.mock_config import DummyConfig

def test_create_geometry_service():
    service = DomainFactory.create_geometry_service()
    assert service is not None
    assert hasattr(service, '_calculate_bbox')
    assert hasattr(service, '_center')

# def test_create_filename_service():
#     service = DomainFactory.create_filename_service(DummyConfig())
#     assert service is not None
#     assert hasattr(service, 'next_filename')
