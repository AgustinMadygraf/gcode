import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest
from pathlib import Path
from infrastructure.config.config import Config
import json
import shutil
import os

def make_temp_config(tmp_path, data):
    config_path = tmp_path / "config.json"
    default_path = tmp_path / "config_default.json"
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(data, f)
    # Copiar el default real para fallback
    shutil.copy(Path(__file__).parent.parent.parent / "infrastructure" / "config" / "config_default.json", default_path)
    return config_path

def test_invalid_area_uses_default(tmp_path):
    # Área inválida (no lista)
    data = {"PLOTTER_MAX_AREA_MM": "foo", "TARGET_WRITE_AREA_MM": [210.0, 148.0]}
    config_path = make_temp_config(tmp_path, data)
    cfg = Config(config_path)
    assert cfg.plotter_max_area_mm == [300.0, 200.0]
    # Área inválida (valores negativos)
    data = {"PLOTTER_MAX_AREA_MM": [-1, 0], "TARGET_WRITE_AREA_MM": [210.0, 148.0]}
    config_path = make_temp_config(tmp_path, data)
    cfg = Config(config_path)
    assert cfg.plotter_max_area_mm == [300.0, 200.0]

def test_target_area_exceeds_max_uses_default(tmp_path):
    data = {"PLOTTER_MAX_AREA_MM": [100.0, 100.0], "TARGET_WRITE_AREA_MM": [200.0, 200.0]}
    config_path = make_temp_config(tmp_path, data)
    cfg = Config(config_path)
    assert cfg.target_write_area_mm == [210.0, 148.0]

def test_valid_areas_are_kept(tmp_path):
    data = {"PLOTTER_MAX_AREA_MM": [400.0, 300.0], "TARGET_WRITE_AREA_MM": [200.0, 100.0]}
    config_path = make_temp_config(tmp_path, data)
    cfg = Config(config_path)
    assert cfg.plotter_max_area_mm == [400.0, 300.0]
    assert cfg.target_write_area_mm == [200.0, 100.0]
