"""
LegacySvgLoaderAdapter
Mantiene la API antigua de SvgLoader para compatibilidad durante la refactorización.
"""

from infrastructure.svg_loader import SvgLoader

class LegacySvgLoaderAdapter:
    " Legacy adapter for SvgLoader to maintain old API compatibility. "
    def __init__(self, *args, **kwargs):
        self._svg_loader = SvgLoader(*args, **kwargs)

    def load(self, *_args, **_kwargs):
        " Legacy load method to maintain compatibility. "
        self._svg_loader.load_paths()
        self._svg_loader.load_attributes()

    def get_subpaths(self, *args, **kwargs):
        " Legacy method to get subpaths, maintaining old API. "
        return self._svg_loader.get_subpaths(*args, **kwargs)

    def load_paths(self):
        " Legacy method to load paths, maintaining old API. "
        return self._svg_loader.load_paths()

    def load_attributes(self):
        " Legacy method to load attributes, maintaining old API. "
        return self._svg_loader.load_attributes()

    def get_paths(self):
        " Legacy method to get paths, maintaining old API. "
        return self._svg_loader.get_paths()

    def get_attributes(self):
        " Legacy method to get attributes, maintaining old API. "
        return self._svg_loader.get_attributes()

    def get_viewbox(self):
        " Legacy method to get viewbox, maintaining old API. "
        return self._svg_loader.get_viewbox()

