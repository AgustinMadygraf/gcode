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
        
    def optimize(self, commands: List[BaseCommand], tolerance: float = None, logger=None) -> Tuple[List[BaseCommand], Dict[str, Any]]:
        """
        Reordena los grupos de comandos (trazos) para priorizar primero los más extensos y luego la cercanía, con pesos dinámicos.
        Preserva bloques de inicialización y finalización fuera de los trazos.
        Si se pasa un logger, imprime el orden final y métricas.
        """
        # 1. Detectar bloques fuera de los trazos (antes y después)
        path_groups = []
        current_group = []
        last_pos = None
        in_trazo = False
        # Identificar primer bloque (inicialización)
        i = 0
        while i < len(commands):
            cmd = commands[i]
            if isinstance(cmd, MoveCommand) and getattr(cmd, 'rapid', False):
                break
            current_group.append(cmd)
            i += 1
        bloques_fuera_inicio = current_group.copy()
        current_group = []
        # Ahora procesar los trazos y el bloque final
        bloques_trazos = []
        while i < len(commands):
            cmd = commands[i]
            if isinstance(cmd, MoveCommand) and getattr(cmd, 'rapid', False):
                if current_group:
                    bloques_trazos.append(current_group)
                    current_group = [cmd]
                else:
                    current_group.append(cmd)
            else:
                current_group.append(cmd)
            i += 1
        if current_group:
            bloques_trazos.append(current_group)
        # Si hay solo uno, no hay trazos para reordenar
        if len(bloques_trazos) < 2:
            return commands, {"paths_reordered": 0, "distance_saved": 0}
        # Detectar si hay bloque final fuera de trazos
        bloques_fuera_final = []
        # Buscar desde el final hacia atrás hasta el último MoveCommand rapid
        for j in range(len(bloques_trazos[-1]) - 1, -1, -1):
            cmd = bloques_trazos[-1][j]
            if isinstance(cmd, MoveCommand) and getattr(cmd, 'rapid', False):
                if j < len(bloques_trazos[-1]) - 1:
                    bloques_fuera_final = bloques_trazos[-1][j+1:]
                    bloques_trazos[-1] = bloques_trazos[-1][:j+1]
                break
        # 2. Calcular longitud de cada trazo (solo movimientos G1 dentro del grupo)
        def group_length(group):
            length = 0.0
            prev = None
            for cmd in group:
                if isinstance(cmd, MoveCommand) and not getattr(cmd, 'rapid', False):
                    if prev is not None:
                        length += self._distance((prev.x, prev.y), (cmd.x, cmd.y))
                    prev = cmd
            return length
        group_lengths = [group_length(g) for g in bloques_trazos]
        max_length = max(group_lengths) or 1.0
        class Stroke:
            def __init__(self, group, idx, length):
                self.group = group
                self.idx = idx
                self.length = length
                self.length_norm = length / max_length
                self.start = self._find_first_position(group)
                self.end = self._find_last_position(group)
            def _find_first_position(self, group):
                for cmd in group:
                    if isinstance(cmd, MoveCommand):
                        return (cmd.x, cmd.y)
                return None
            def _find_last_position(self, group):
                last_pos = None
                for cmd in group:
                    if isinstance(cmd, MoveCommand):
                        last_pos = (cmd.x, cmd.y)
                return last_pos
        # Primer trazo no se reordena, ni el último si es solo bloque final
        strokes = [Stroke(g, i, l) for i, (g, l) in enumerate(zip(bloques_trazos, group_lengths))]
        ordered = [strokes[0]]
        remaining = strokes[1:]
        last_pos = ordered[0].end
        N = len(strokes) - 1
        for k in range(1, N+1):
            alpha = 1 - (k / (N+1))
            beta = k / (N+1)
            dists = [self._distance(last_pos, s.start) for s in remaining]
            max_dist = max(dists) or 1.0
            for s, d in zip(remaining, dists):
                s.dist_norm = d / max_dist
            def score(s):
                return alpha * s.length_norm - beta * s.dist_norm
            next_stroke = max(remaining, key=score)
            ordered.append(next_stroke)
            remaining.remove(next_stroke)
            last_pos = next_stroke.end
        # Reconstruir comandos: inicio + trazos reordenados + final
        optimized_commands = []
        optimized_commands.extend(bloques_fuera_inicio)
        for s in ordered:
            optimized_commands.extend(s.group)
        optimized_commands.extend(bloques_fuera_final)
        metrics = {
            "paths_reordered": len(bloques_trazos) - 1,
            "strategy": "length+proximity-dynamic",
        }
        if logger:
            orden = [s.start for s in ordered]
            logger.info(f"Orden final de trazos (puntos de inicio): {orden}")
            logger.info(f"Métricas de optimización: {metrics}")
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
