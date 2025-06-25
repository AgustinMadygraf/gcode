"""
PathPlannerOptimizer: Optimiza el orden de los trazos para minimizar movimientos G0 improductivos.
"""
from typing import List, Dict, Any, Tuple
from domain.ports.gcode_optimization_port import GcodeOptimizationPort
from domain.gcode.commands.base_command import BaseCommand
from domain.gcode.commands.move_command import MoveCommand
import math

class PathPlannerOptimizer(GcodeOptimizationPort):
    """Optimiza el orden de los trazos para minimizar la distancia total de movimientos rápidos."""
    
    def __init__(self, min_distance: float = 5.0):
        """
        Inicializa el optimizador.
        Args:
            min_distance: Distancia mínima para considerar optimización (mm)
        """
        self.min_distance = min_distance
        
    def optimize(self, commands: List[BaseCommand], tolerance: float = None) -> Tuple[List[BaseCommand], Dict[str, Any]]:
        """
        Reordena los grupos de comandos (trazos) para minimizar movimientos rápidos.
        Args:
            commands: Lista de comandos BaseCommand a optimizar
            tolerance: No utilizado en este optimizador
        Returns:
            Tupla con (lista de comandos optimizados, métricas de optimización)
        """
        # Detectar grupos de comandos (trazos)
        path_groups = []
        current_group = []
        last_pos = None
        
        # 1. Identificar grupos de comandos (trazos separados por G0)
        for cmd in commands:
            if isinstance(cmd, MoveCommand) and getattr(cmd, 'rapid', False):
                if current_group:  # Si tenemos un grupo en construcción
                    path_groups.append(current_group)
                    current_group = [cmd]  # Iniciar nuevo grupo con el G0
                else:
                    current_group.append(cmd)
                last_pos = (cmd.x, cmd.y)
            else:
                current_group.append(cmd)
                if isinstance(cmd, MoveCommand):
                    last_pos = (cmd.x, cmd.y)
                    
        # Añadir el último grupo si existe
        if current_group:
            path_groups.append(current_group)
            
        # Si tenemos menos de 2 grupos, no hay optimización posible
        if len(path_groups) < 3:  # Necesitamos al menos inicio + 2 trazos para optimizar
            return commands, {"paths_reordered": 0, "distance_saved": 0}
            
        # 2. El primer grupo siempre es el inicio, no se reordena
        optimized_groups = [path_groups[0]]
        remaining_groups = path_groups[1:]
        
        # 3. Encontrar la posición final del último comando de movimiento en el grupo inicial
        last_pos = self._find_last_position(optimized_groups[0])
        
        # 4. Algoritmo greedy: siempre elegir el grupo más cercano
        total_distance_original = 0
        total_distance_optimized = 0
        
        # Calcular la distancia original (no optimizada)
        orig_last_pos = self._find_last_position(path_groups[0])
        for i in range(1, len(path_groups)):
            start_pos = self._find_first_position(path_groups[i])
            if start_pos and orig_last_pos:
                total_distance_original += self._distance(orig_last_pos, start_pos)
            orig_last_pos = self._find_last_position(path_groups[i])
        
        # Optimizar el orden de los grupos
        while remaining_groups:
            closest_idx = -1
            min_dist = float('inf')
            
            # Encontrar el grupo más cercano
            for i, group in enumerate(remaining_groups):
                start_pos = self._find_first_position(group)
                if start_pos and last_pos:
                    dist = self._distance(last_pos, start_pos)
                    if dist < min_dist:
                        min_dist = dist
                        closest_idx = i
            
            # Si encontramos un grupo cercano, añadirlo a la secuencia optimizada
            if closest_idx >= 0:
                next_group = remaining_groups.pop(closest_idx)
                optimized_groups.append(next_group)
                total_distance_optimized += min_dist
                last_pos = self._find_last_position(next_group)
            else:
                # Si no hay grupos válidos, simplemente añadir el resto en orden
                optimized_groups.extend(remaining_groups)
                break
        
        # 5. Reconstruir la secuencia completa de comandos
        optimized_commands = []
        for group in optimized_groups:
            optimized_commands.extend(group)
        
        # 6. Calcular métricas
        distance_saved = total_distance_original - total_distance_optimized
        metrics = {
            "paths_reordered": len(path_groups) - 1,  # Todos excepto el primero
            "distance_saved": round(distance_saved, 2),
            "original_distance": round(total_distance_original, 2),
            "optimized_distance": round(total_distance_optimized, 2)
        }
        
        return optimized_commands, metrics
    
    def _find_first_position(self, group: List[BaseCommand]) -> Tuple[float, float]:
        """Encuentra la primera posición de movimiento en un grupo de comandos"""
        for cmd in group:
            if isinstance(cmd, MoveCommand):
                return (cmd.x, cmd.y)
        return None
    
    def _find_last_position(self, group: List[BaseCommand]) -> Tuple[float, float]:
        """Encuentra la última posición de movimiento en un grupo de comandos"""
        last_pos = None
        for cmd in group:
            if isinstance(cmd, MoveCommand):
                last_pos = (cmd.x, cmd.y)
        return last_pos
    
    def _distance(self, p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
        """Calcula la distancia euclidiana entre dos puntos"""
        return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
