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
    def config_get(_self, k, d=None):
        if k == 'GENERATE_REFERENCE_MARKS':
            return True
        if k == 'DWELL_MS':
            return 100
        if k == 'CMD_UP':
            return 'M5'
        if k == 'CMD_DOWN':
            return 'M3 S255'
        if k == 'FEED':
            return 1000
        return d
    monkeypatch.setattr('infrastructure.adapters.reference_marks_generator.Config.get', config_get)
    class DummyI18n:
        def get(self, key, default=None):
            return default or key
    ref_marks_generator = ReferenceMarksGenerator(logger=logger, i18n=DummyI18n())
    gcode = ref_marks_generator.generate(width=210.0, height=148.0)
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
    def config_get(_self, k, d=None):
        if k == 'GENERATE_REFERENCE_MARKS':
            return False
        if k == 'DWELL_MS':
            return 100
        return d
    monkeypatch.setattr('infrastructure.adapters.reference_marks_generator.Config.get', config_get)
    class DummyI18n:
        def get(self, key, default=None):
            return default or key
    ref_marks_generator = ReferenceMarksGenerator(logger=logger, i18n=DummyI18n())
    gcode = ref_marks_generator.generate(width=210.0, height=148.0)
    assert 'M3 S255' not in gcode  # CMD_DOWN
    assert 'M5' not in gcode      # CMD_UP
    assert '; --- START OF AUTOMATIC REFERENCE MARKS ---' in gcode
    assert '; --- END OF AUTOMATIC REFERENCE MARKS ---' in gcode
