"""
Test manual/integración para NonInteractiveSvgToGcodeWorkflow tras modularización.
Este test puede ser adaptado a pytest/unittest si se desea automatizar.
"""
from application.workflows.non_interactive_svg_to_gcode_workflow import NonInteractiveSvgToGcodeWorkflow
from types import SimpleNamespace

class DummyPresenter:
    def print(self, *args, **kwargs):
        print("[Presenter]", args, kwargs)

class DummyContainer:
    def __init__(self):
        self.logger = None
        self.domain_factory = None
        self.adapter_factory = None
        self.path_processing_service = None
        self.gcode_generation_service = None
        self.gcode_compression_service = None
        self.compress_gcode_use_case = None
        self.svg_to_gcode_use_case = None
        self.gcode_to_gcode_use_case = None
        self.gcode_rescale_use_case = None
    def get_svg_loader(self, *a, **k):
        raise NotImplementedError("Mock or real implementation needed")
    def get_gcode_generator(self, *a, **k):
        raise NotImplementedError("Mock or real implementation needed")
    def create_path_processing_service(self):
        raise NotImplementedError()
    def create_gcode_generation_service(self, *a, **k):
        raise NotImplementedError()
    def create_gcode_compression_service(self):
        raise NotImplementedError()
    def create_config_adapter(self, *a, **k):
        raise NotImplementedError()
    def create_compress_gcode_use_case(self, *a, **k):
        raise NotImplementedError()
    def create_svg_to_gcode_use_case(self, *a, **k):
        raise NotImplementedError()
    def create_gcode_to_gcode_use_case(self, *a, **k):
        raise NotImplementedError()
    def create_gcode_rescale_use_case(self, *a, **k):
        raise NotImplementedError()

class DummyFilenameService:
    pass

class DummyConfig:
    def get_remove_svg_border(self): return False
    def get_border_detection_tolerance(self): return 0.05
    def get_mirror_vertical(self): return False

if __name__ == "__main__":
    # Simula argumentos para SVG
    args_svg = SimpleNamespace(input="test.svg", output="out.gcode", optimize=False, rescale=None, tool="pen", double_pass=True)
    # Simula argumentos para GCODE
    args_gcode = SimpleNamespace(input="test.gcode", output="out2.gcode", optimize=True, rescale=None)
    workflow = NonInteractiveSvgToGcodeWorkflow(DummyContainer(), DummyPresenter(), DummyFilenameService(), DummyConfig())
    print("--- Test SVG ---")
    try:
        workflow.run(args_svg)
    except NotImplementedError:
        print("[OK] Llamadas a dependencias externas no implementadas (esperado en test dummy)")
    print("--- Test GCODE ---")
    try:
        workflow.run(args_gcode)
    except NotImplementedError:
        print("[OK] Llamadas a dependencias externas no implementadas (esperado en test dummy)")
