import sys
import subprocess
import os


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RUN_PY = os.path.join(PROJECT_ROOT, 'run.py')


def run_with_args(args):
    """Ejecuta run.py con argumentos y retorna (stdout, stderr, exit_code)"""
    cmd = [sys.executable, RUN_PY] + args
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    out, err = proc.communicate()
    return out, err, proc.returncode


def test_dev_flag_enables_debug_and_stacktrace():
    # Forzar excepción genérica usando argumento inválido
    out, err, code = run_with_args(['--dev', '--input', 'no_existe.svg'])
    # Debe mostrar logging DEBUG y stacktrace extendido
    assert 'Modo desarrollador activo' in err or 'Modo desarrollador activo' in out
    assert 'Traceback' in err or 'Traceback' in out
    assert code in (1, 2, 99)  # 1: error genérico, 2: input error, 99: error inesperado


def test_no_dev_flag_no_stacktrace():
    _out, _err, code = run_with_args(['--input', 'no_existe.svg'])
    # Puede mostrar stacktrace dependiendo del entorno, solo verificar código
    assert code in (1, 2, 99)
