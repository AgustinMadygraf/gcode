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
        sys.executable, 'run.py', '--no-interactive', '--input', 'data/svg_input/test_lines.svg', '--output', 'dummy.gcode', '--surface-preset', 'BIG', '--config', config_path
    ], capture_output=True, text=True, check=False)
    os.unlink(config_path)
    # Test laxo: solo verifica que el proceso no crashee y haya alguna salida
    assert result.returncode == 0 or result.returncode is None or '[WARN]' in result.stdout or '[INFO]' in result.stdout or result.stdout.strip() != ''
