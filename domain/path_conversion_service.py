"""
Servicio de conversión de paths a G-code en el dominio.
Define la interfaz y la responsabilidad de orquestar la conversión, sin implementación.
"""
from abc import ABC, abstractmethod
from typing import Any, List, Dict

__all__ = [
    "PathConversionService"
]
