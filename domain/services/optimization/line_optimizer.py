"""
LineOptimizer: Optimizador para consolidar movimientos lineales en la misma coordenada.
"""
from typing import List, Dict, Any
from domain.ports.gcode_optimization_port import GcodeOptimizationPort
from domain.gcode.commands.base_command import BaseCommand
from domain.gcode.commands.move_command import MoveCommand

class LineOptimizer(GcodeOptimizationPort):
    """
    Detecta y consolida secuencias de movimientos lineales en la misma coordenada.
    Ejemplo: Múltiples G1 con incrementos en X y mismo Y se combinan en un único comando.
    """
    
    def __init__(self, tolerance: float = 1e-6):
        """
        Inicializa el optimizador con una tolerancia para comparar coordenadas.
        Args:
            tolerance: Tolerancia para comparar si dos coordenadas son iguales
        """
        self.tolerance = tolerance
        
    def optimize(self, commands: List[BaseCommand], tolerance: float = None) -> tuple[List[BaseCommand], Dict[str, Any]]:
        """
        Optimiza comandos consolidando secuencias lineales en la misma coordenada.
        Args:
            commands: Lista de comandos BaseCommand a optimizar
            tolerance: Tolerancia opcional (usa la del objeto si no se proporciona)
        Returns:
            Tupla con (lista de comandos optimizados, métricas de optimización)
        """
        result = []
        i = 0
        lines_optimized = 0
        segments_removed = 0
        tol = tolerance if tolerance is not None else self.tolerance
        
        while i < len(commands):
            # Si no es un comando de movimiento, simplemente añadirlo
            if not isinstance(commands[i], MoveCommand) or commands[i].rapid:
                result.append(commands[i])
                i += 1
                continue
                
            # Potencial inicio de secuencia lineal
            current = commands[i]
            sequence = [current]
            constant_y = current.y
            constant_feed = current.feed
            start_x = current.x
            
            # Buscar secuencia con Y constante
            j = i + 1
            while (j < len(commands) and 
                   isinstance(commands[j], MoveCommand) and 
                   not commands[j].rapid and
                   abs(commands[j].y - constant_y) < tol and
                   (commands[j].feed is None or commands[j].feed == constant_feed)):
                sequence.append(commands[j])
                j += 1
                
            # Si encontramos una secuencia suficientemente larga, optimizarla
            if len(sequence) > 1:
                end_x = sequence[-1].x
                # Reemplazar toda la secuencia con un único movimiento
                result.append(MoveCommand(end_x, constant_y, constant_feed, rapid=False))
                segments_removed += len(sequence) - 1
                lines_optimized += 1
                i = j
            else:
                result.append(current)
                i += 1
        
        metrics = {
            "segments_removed": segments_removed,
            "lines_optimized": lines_optimized
        }
        return result, metrics
