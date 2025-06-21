"""
Test para LegacySvgLoaderAdapter
"""
from pathlib import Path
from infrastructure.adapters.legacy_svg_loader_adapter import LegacySvgLoaderAdapter

def test_legacy_svg_loader_adapter_load_and_get(tmp_path):
    # Crear un SVG mínimo de prueba
    svg_content = '''<svg viewBox="0 0 10 10" xmlns="http://www.w3.org/2000/svg"><path d="M0,0 L10,0 L10,10 Z"/></svg>'''
    svg_file = tmp_path / "test.svg"
    svg_file.write_text(svg_content, encoding="utf-8")

    adapter = LegacySvgLoaderAdapter(svg_file)
    adapter.load()  # Debe cargar paths y atributos
    paths = adapter.get_paths()
    attrs = adapter.get_attributes()
    viewbox = adapter.get_viewbox()
    subpaths = adapter.get_subpaths()

    assert isinstance(paths, list)
    assert isinstance(attrs, dict)
    assert isinstance(viewbox, tuple)
    assert isinstance(subpaths, list)
    assert len(paths) > 0
    assert "viewBox" in attrs
