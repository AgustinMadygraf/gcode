import io
import sys
import pytest
from infrastructure.logger import ConsoleLogger

def test_logger_info_colored(monkeypatch):
    buf = io.StringIO()
    logger = ConsoleLogger(use_color=True, stream=buf, level='INFO')
    logger.info('Mensaje info')
    output = buf.getvalue()
    assert '[INFO]' in output
    assert '\x1b[32m' in output  # Verde
    assert 'Mensaje info' in output

def test_logger_error_colored(monkeypatch):
    buf = io.StringIO()
    logger = ConsoleLogger(use_color=True, stream=buf, level='INFO')
    logger.error('Mensaje error')
    output = buf.getvalue()
    assert '[ERROR]' in output
    assert '\x1b[31m' in output  # Rojo
    assert 'Mensaje error' in output

def test_logger_no_color(monkeypatch):
    buf = io.StringIO()
    logger = ConsoleLogger(use_color=False, stream=buf, level='INFO')
    logger.info('Sin color')
    output = buf.getvalue()
    assert '\x1b[' not in output
    assert '[INFO]' in output
    assert 'Sin color' in output

def test_logger_level(monkeypatch):
    buf = io.StringIO()
    logger = ConsoleLogger(use_color=False, stream=buf, level='WARNING')
    logger.info('No debe verse')
    logger.warning('Advertencia')
    output = buf.getvalue()
    assert '[WARN]' in output
    assert 'Advertencia' in output
    assert 'No debe verse' not in output

def test_logger_input(monkeypatch):
    buf = io.StringIO()
    logger = ConsoleLogger(use_color=True, stream=buf, level='INFO')
    logger.input('Ingrese valor:')
    output = buf.getvalue()
    assert '[INPUT]' in output
    assert '\x1b[34m' in output  # Azul
    assert 'Ingrese valor:' in output

def test_logger_info_file_line(monkeypatch):
    buf = io.StringIO()
    logger = ConsoleLogger(use_color=False, stream=buf, level='INFO', show_file_line=True)
    logger.info('Mensaje info fileline')
    output = buf.getvalue()
    # Debe contener el nombre de este archivo y un número de línea
    import re
    assert '[INFO]' in output
    assert 'Mensaje info fileline' in output
    # Buscar patrón archivo:línea
    assert re.search(r'test_logger.py:\d+ Mensaje info fileline', output)
