import subprocess
import sys
import os
import json
import tempfile

def test_surface_preset_batch_scaling():
    # Crear config temporal con preset grande
    config_data = {
        "PLOTTER_MAX_AREA_MM": [300.0, 200.0],
        "TARGET_WRITE_AREA_MM": [210.0, 148.0],
        "SURFACE_PRESETS": {"BIG": [1000.0, 1000.0]}
    }
    with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.json') as tmp:
        json.dump(config_data, tmp)
        config_path = tmp.name
    # Ejecutar en modo batch con --surface-preset BIG
    result = subprocess.run([
        sys.executable, 'run.py', '--no-interactive', '--input', 'dummy.svg', '--output', 'dummy.gcode', '--surface-preset', 'BIG', '--config', config_path
    ], capture_output=True, text=True)
    os.unlink(config_path)
    assert '[WARN]' in result.stdout or '[INFO]' in result.stdout
    assert 'escalada' in result.stdout.lower() or 'escalado' in result.stdout.lower() or 'scaled' in result.stdout.lower()
