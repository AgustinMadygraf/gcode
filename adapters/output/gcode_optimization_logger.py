"""
GcodeOptimizationLogger: Centraliza el logging de optimización y métricas de paths para generación de G-code.
"""
from typing import List, Any, Dict

class GcodeOptimizationLogger:
    def __init__(self, logger, i18n):
        self.logger = logger
        self.i18n = i18n

    def log_paths_order(self, paths, path_id_fn, label):
        if not self.logger:
            return
        ids = [path_id_fn(p, i) for i, p in enumerate(paths)]
        self.logger.debug(self.i18n.get(label, list=f"{ids[:20]}{'...' if len(ids) > 20 else ''}"))

    def log_total_distance(self, dist, label):
        if not self.logger:
            return
        self.logger.debug(self.i18n.get(label, dist=f"{dist:.2f}"))

    def log_bbox_and_scale(self, bbox, scale):
        if not self.logger:
            return
        xmin, xmax, ymin, ymax = bbox
        self.logger.debug(self.i18n.get("DEBUG_BOUNDING_BOX", xmin=f"{xmin:.3f}", xmax=f"{xmax:.3f}", ymin=f"{ymin:.3f}", ymax=f"{ymax:.3f}"))
        self.logger.debug(self.i18n.get("DEBUG_SCALE_APPLIED", scale=f"{scale:.3f}"))
