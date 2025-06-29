from pathlib import Path
from typing import List, Dict, Any
from domain.ports.logger_port import LoggerPort
from domain.ports.filename_service_port import FilenameServicePort
from domain.services.validation.gcode_validator import GCodeValidator

class GcodeToGcodeUseCase:
    """Caso de uso para refactorizar archivos GCODE existentes."""
    def __init__(self, filename_service: FilenameServicePort, logger: LoggerPort = None):
        self.filename_service = filename_service
        self.logger = logger

    def execute(self, gcode_file: Path) -> Dict[str, Any]:
        if self.logger:
            msg = getattr(self.logger, 'i18n', None)
            if msg:
                self.logger.info(msg.get("info_refactor_start", gcode_file=gcode_file))
            else:
                self.logger.info(f"Iniciando refactorización de: {gcode_file}")
        with open(gcode_file, 'r', encoding='utf-8') as f:
            gcode_lines = f.read().splitlines()
        # Validar integridad G-code antes de procesar
        valido, error = GCodeValidator.validate(gcode_lines)
        if not valido:
            if self.logger:
                msg = getattr(self.logger, 'i18n', None)
                if msg:
                    self.logger.error(msg.get("error_gcode_validation", error=error))
                else:
                    self.logger.error(f"Validación G-code fallida: {error}")
            raise ValueError(f"Archivo G-code inválido: {error}")
        refactored_lines, stats = self._optimize_gcode_movements(gcode_lines)
        output_file = self.filename_service.next_filename(gcode_file)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("\n".join(refactored_lines))
        if self.logger:
            msg = getattr(self.logger, 'i18n', None)
            if msg:
                self.logger.info(msg.get("info_refactor_saved", output_file=output_file))
                self.logger.info(msg.get("info_refactor_stats", changes=stats['changes']))
            else:
                self.logger.info(f"Archivo refactorizado guardado en: {output_file}")
                self.logger.info(f"Estadísticas: {stats['changes']} movimientos optimizados")
        return {
            'input_file': gcode_file,
            'output_file': output_file,
            'lines_processed': len(gcode_lines),
            'changes_made': stats['changes'],
            'stats': stats
        }

    def _optimize_gcode_movements(self, lines: List[str]) -> tuple[List[str], Dict[str, Any]]:
        result = []
        changes = 0
        in_tool_up_state = False
        for line in lines:
            clean_line = line.split(';')[0].strip()
            if clean_line.startswith("M5"):
                in_tool_up_state = True
                result.append(line)
                continue
            if clean_line.startswith("M3"):
                in_tool_up_state = False
                result.append(line)
                continue
            if in_tool_up_state and clean_line.startswith("G1"):
                modified_line = "G0" + line[2:]
                result.append(modified_line)
                changes += 1
                continue
            result.append(line)
        stats = {
            'changes': changes,
            'lines_total': len(lines),
            'optimization_rate': changes / len(lines) if lines else 0
        }
        return result, stats
