import pytest
from pathlib import Path
from application.use_cases.svg_to_gcode_use_case import SvgToGcodeUseCase
from tests.mocks.mock_use_case import (
    DummyLoader, 
    DummyPathProcessor, 
    DummyGcodeGen, 
    DummyCompressUseCase,
    DummyLogger,
    DummyFilenameService
)

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
