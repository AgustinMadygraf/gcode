"""
Factory para servicios y entidades de la capa de Dominio.
"""
from domain.services.geometry import GeometryService
from domain.services.filename_service import FilenameService

class DomainFactory:
    @staticmethod
    def create_geometry_service():
        return GeometryService()

    @staticmethod
    def create_filename_service(config):
        return FilenameService(config)
