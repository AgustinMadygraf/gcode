"""
Path: domain/services/path_filter_service.py
Implementación concreta de PathFilterPort para filtrado de paths SVG.
"""
from typing import List, Any, Callable
from domain.ports.path_filter_port import PathFilterPort
from domain.filters.svg_border_detector import SvgBorderDetector

class DummyI18n:
    def get(self, key, **_kwargs):
        return key  # Devuelve la clave como mensaje por defecto

class PathFilter(PathFilterPort):
    DEBUG_ENABLED = False  # Controla si se muestran logs debug
    " Filtra paths SVG no triviales basándose en longitud y atributos SVG. "
    def __init__(self, min_length: float = 1e-3, extra_filters: List[Callable[[Any], bool]] = None,
                 remove_svg_border: bool = True, border_tolerance: float = 0.05, logger=None, i18n=None):
        self.min_length = min_length
        self.extra_filters = extra_filters or []
        self.remove_svg_border = remove_svg_border
        if logger is None:
            raise RuntimeError("Logger debe ser inyectado en PathFilter. Usar siempre el constructor con logger explícito.")
        self.logger = logger
        self.i18n = i18n if i18n is not None else DummyI18n()
        self.border_detector = SvgBorderDetector(tolerance=border_tolerance, logger=logger) if remove_svg_border else None

    def _debug(self, msg, *args, **kwargs):
        if self.DEBUG_ENABLED:
            self.logger.debug(msg, *args, **kwargs)

    def filter_nontrivial(self, paths: List[Any], svg_attr: dict = None) -> List[Any]:
        filtered = []
        removed = 0
        for _i, p in enumerate(paths):
            try:
                total_length = sum(seg.length() for seg in p)
                # self._debug(self.i18n.get('DEBUG_PATH_LENGTH', idx=_i, length=total_length, segments=len(p)))
                if total_length <= self.min_length:
                    self._debug(self.i18n.get('DEBUG_PATH_DISCARDED_LENGTH', idx=_i, length=total_length))
                    continue
                try:
                    if not all(f(p) for f in self.extra_filters):
                        self._debug(self.i18n.get('DEBUG_PATH_DISCARDED_EXTRA_FILTER', idx=_i))
                        continue
                except (TypeError, ValueError) as e:
                    self.logger.error(self.i18n.get('ERROR_EXTRA_FILTER', idx=_i, error=str(e)), exc_info=True)
                    continue
                if self.remove_svg_border:
                    if not svg_attr:
                        self._debug(self.i18n.get('DEBUG_MATCHES_SVG_BOUNDS', idx=_i, borde=None))
                        self._debug(self.i18n.get('DEBUG_PATH_NOT_REMOVED_BORDER', idx=_i))
                        filtered.append(p)
                        continue
                    borde = self.border_detector.matches_svg_bounds(p, svg_attr)
                    self._debug(self.i18n.get('DEBUG_MATCHES_SVG_BOUNDS', idx=_i, borde=borde))
                    if borde:
                        removed += 1
                        continue
                    self._debug(self.i18n.get('DEBUG_PATH_NOT_REMOVED_BORDER', idx=_i))
                filtered.append(p)
            except (AttributeError, KeyError, TypeError, ValueError) as e:
                self.logger.error(self.i18n.get('ERROR_FILTER_PATH', idx=_i, error=str(e)), exc_info=True)
        self._debug(self.i18n.get('DEBUG_TOTAL_PATHS_REMOVED', removed=removed))
        return filtered
