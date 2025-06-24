import pytest
from pathlib import Path
from application.use_cases.svg_to_gcode_use_case import SvgToGcodeUseCase

class DummyLoader:
    def __init__(self, svg_file):
        self.svg_file = svg_file
    def get_paths(self):
        return [1, 2, 3]  # Simula paths
    def get_attributes(self):
        return {'width': 100, 'height': 100}

class DummyPathProcessor:
    def process(self, paths, attrs):
        return paths[:2]  # Simula filtrado

class DummyGcodeGen:
    def generate(self, paths, attrs):
        return [f'G1 X{p}' for p in paths]

class DummyCompressUseCase:
    def execute(self, gcode_lines):
        return {'compressed_gcode': gcode_lines[::-1], 'original_size': len(gcode_lines), 'compressed_size': len(gcode_lines), 'compression_ratio': 1.0}

class DummyLogger:
    def info(self, *a, **k): pass

class DummyFilenameService:
    pass

def test_svg_to_gcode_use_case_basic():
    use_case = SvgToGcodeUseCase(
        svg_loader_factory=DummyLoader,
        path_processing_service=DummyPathProcessor(),
        gcode_generation_service=DummyGcodeGen(),
        gcode_compression_use_case=DummyCompressUseCase(),
        logger=DummyLogger(),
        filename_service=DummyFilenameService()
    )
    result = use_case.execute(Path('dummy.svg'))
    assert result['svg_file'].name == 'dummy.svg'
    assert result['processed_paths'] == [1, 2]
    assert result['gcode_lines'] == ['G1 X1', 'G1 X2']
    assert result['compressed_gcode'] == ['G1 X2', 'G1 X1']
