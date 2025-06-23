"""
Este archivo ha sido migrado. La lógica de generación de G-code ahora reside en:
- infrastructure/adapters/gcode_generator_adapter.py (adaptador)
- domain/ports/gcode_generator_port.py (puerto de dominio)
- domain/path_conversion_service.py (servicio de orquestación de conversión)

Elimina cualquier referencia legacy a GCodeGenerator y usa el adaptador y el nuevo servicio.
"""

__all__ = []
