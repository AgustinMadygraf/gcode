"""
Factory para servicios y entidades de la capa de Dominio.
"""
from domain.services.geometry import GeometryService

class DomainFactory:
    @staticmethod
    def create_geometry_service():
        return GeometryService()
