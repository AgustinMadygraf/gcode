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

class DummyI18n:
    def get(self, key, **_kwargs):
        return key

def test_svg_to_gcode_use_case_basic():
    use_case = SvgToGcodeUseCase(
        svg_loader_factory=DummyLoader,
        path_processing_service=DummyPathProcessor(),
        gcode_generation_service=DummyGcodeGen(),
        gcode_compression_use_case=DummyCompressUseCase(),
        logger=DummyLogger(),
        filename_service=DummyFilenameService(),
        i18n=DummyI18n()
    )
    result = use_case.execute(Path(r'data\svg_input\test_lines.svg'))
    # Test laxo: solo verifica que el nombre contenga 'test_lines.svg'
    assert 'test_lines.svg' in result['svg_file'].name
    assert result['processed_paths'] == [1, 2]
    assert result['gcode_lines'] == ['G1 X1', 'G1 X2']
    assert result['compressed_gcode'] == ['G1 X2', 'G1 X1']
