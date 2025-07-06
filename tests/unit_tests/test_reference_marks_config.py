from infrastructure.adapters.reference_marks_generator import ReferenceMarksGenerator

def test_reference_marks_enabled(monkeypatch):
    class DummyLogger:
        def __init__(self):
            self.infos = []
            self.debugs = []
        def info(self, msg):
            self.infos.append(msg)
        def debug(self, msg):
            self.debugs.append(msg)
    logger = DummyLogger()
    # Forzar config: monkeypatch Config para devolver True
    monkeypatch.setattr('infrastructure.adapters.reference_marks_generator.Config.get', lambda self, k, d=None: True if k == 'GENERATE_REFERENCE_MARKS' else d)
    gcode = ReferenceMarksGenerator.generate(logger=logger, width=210.0, height=148.0)
    assert 'M3 S255' in gcode  # CMD_DOWN
    assert 'M5' in gcode      # CMD_UP
    assert '; --- START OF AUTOMATIC REFERENCE MARKS ---' in gcode
    assert '; --- END OF AUTOMATIC REFERENCE MARKS ---' in gcode


def test_reference_marks_disabled(monkeypatch):
    class DummyLogger:
        def __init__(self):
            self.infos = []
            self.debugs = []
        def info(self, msg):
            self.infos.append(msg)
        def debug(self, msg):
            self.debugs.append(msg)
    logger = DummyLogger()
    # Forzar config: monkeypatch Config para devolver False
    monkeypatch.setattr('infrastructure.adapters.reference_marks_generator.Config.get', lambda self, k, d=None: False if k == 'GENERATE_REFERENCE_MARKS' else d)
    gcode = ReferenceMarksGenerator.generate(logger=logger, width=210.0, height=148.0)
    assert 'M3 S255' not in gcode  # CMD_DOWN
    assert 'M5' not in gcode      # CMD_UP
    assert '; --- START OF AUTOMATIC REFERENCE MARKS ---' in gcode
    assert '; --- END OF AUTOMATIC REFERENCE MARKS ---' in gcode
