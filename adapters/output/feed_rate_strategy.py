"""
FeedRateStrategy: Encapsula la lógica de ajuste de velocidad (feed rate) según curvatura y tipo de herramienta.
"""
from typing import Optional

class FeedRateStrategy:
    def __init__(self, base_feed: float, curvature_factor: float = 1.0, min_feed_factor: float = 0.2):
        self.base_feed = base_feed
        self.curvature_factor = curvature_factor
        self.min_feed_factor = min_feed_factor

    def adjust_feed(self, curvature: Optional[float] = None, tool_type: Optional[str] = None) -> float:
        """
        Ajusta el feed rate según la curvatura y el tipo de herramienta.
        Si curvature es None, retorna el base_feed.
        """
        feed = self.base_feed
        if curvature is not None:
            # Ejemplo: feed disminuye en curvas cerradas
            feed *= max(self.min_feed_factor, 1.0 - self.curvature_factor * curvature)
        if tool_type == "marker":
            feed *= 0.8  # Ejemplo: los marcadores requieren menor velocidad
        # Se pueden agregar más reglas según el tipo de herramienta
        return feed
