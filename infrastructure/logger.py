"""
Logger setup for the application.
Soporta niveles: INPUT, INFO, DEBUG, ERROR, WARN, y colores ANSI.
"""
import sys
import inspect
import os

class AnsiColor:
    " ANSI color codes for terminal output. "
    RED = '\x1b[31m'
    YELLOW = '\x1b[33m'
    GREEN = '\x1b[32m'
    CYAN = '\x1b[36m'
    BLUE = '\x1b[34m'
    MAGENTA = '\x1b[35m'  # Violeta claro
    RESET = '\x1b[0m'

LEVEL_COLORS = {
    'ERROR': AnsiColor.RED,
    'WARNING': AnsiColor.YELLOW,
    'INFO': AnsiColor.GREEN,
    'DEBUG': AnsiColor.CYAN,
    'INPUT': AnsiColor.BLUE,
    'OPTION': AnsiColor.MAGENTA,
}

LEVEL_PREFIXES = {
    'ERROR': '[ERROR]',
    'WARNING': '[WARN]',
    'INFO': '[INFO]',
    'DEBUG': '[DEBUG]',
    'INPUT': '[INPUT]',
    'OPTION': '[OPTION]',
}

class ConsoleLogger:
    " Logger that outputs messages to the console with optional colors and file/line info. "
    LEVELS = {'DEBUG': 10, 'INFO': 20, 'OPTION': 21, 'INPUT': 15, 'WARNING': 30, 'ERROR': 40}
    def __init__(self, use_color=True, stream=sys.stderr, level='INFO', show_file_line=False):
        self.use_color = use_color
        self.stream = stream
        self.level = self.LEVELS.get(level.upper(), 20)
        self.show_file_line = show_file_line

    def _should_log(self, level):
        lvl = self.LEVELS.get(level, 20)
        return lvl >= self.level or level in ('INPUT', 'OPTION')

    def _log(self, level, msg, *_args, stacklevel=2, **_kwargs):
        if not self._should_log(level):
            return
        prefix = LEVEL_PREFIXES.get(level, '[INFO]')
        color = LEVEL_COLORS.get(level, '') if self.use_color else ''
        reset = AnsiColor.RESET if self.use_color and color else ''
        # Añadir archivo:línea si es INFO, DEBUG o WARNING y show_file_line está activo
        if level in ('INFO', 'DEBUG', 'WARNING', 'ERROR') and self.show_file_line:
            stack = inspect.stack()
            idx = stacklevel
            if idx >= len(stack):
                idx = len(stack) - 1
            frame_info = stack[idx]
            filename = os.path.basename(frame_info.filename)
            lineno = frame_info.lineno
            if level in LEVEL_PREFIXES:
                prefix = (
                    f"[{level} {filename}:{lineno}]"
                )
            else:
                prefix = (
                    f"[INFO {filename}:{lineno}]"
                )
        else:
            prefix = LEVEL_PREFIXES.get(level, '[INFO]')
        print(f"{color}{prefix} {msg}{reset}", file=self.stream)

    def info(self, msg, *args, stacklevel=2, **kwargs):
        " Log an informational message. "
        self._log('INFO', msg, *args, stacklevel=stacklevel, **kwargs)
    def debug(self, msg, *args, stacklevel=2, **kwargs):
        " Log a debug message. "
        self._log('DEBUG', msg, *args, stacklevel=stacklevel, **kwargs)
    def error(self, msg, *args, stacklevel=2, **kwargs):
        " Log an error message. "
        self._log('ERROR', msg, *args, stacklevel=stacklevel, **kwargs)
    def warning(self, msg, *args, stacklevel=2, **kwargs):
        " Log a warning message. "
        self._log('WARNING', msg, *args, stacklevel=stacklevel, **kwargs)
    def input(self, msg, *args, stacklevel=2, **kwargs):
        " Log an input message. "
        self._log('INPUT', msg, *args, stacklevel=stacklevel, **kwargs)
    def option(self, msg, *args, stacklevel=2, **kwargs):
        " Log an option message. "
        self._log('OPTION', msg, *args, stacklevel=stacklevel, **kwargs)

def get_logger(use_color=True, level='INFO', show_file_line=False):
    """
    Retorna una instancia de ConsoleLogger configurada.
    Siempre usar esta función y pasar el logger a los componentes por inyección.
    No existe más instancia global; el uso debe ser explícito.
    """
    return ConsoleLogger(use_color=use_color, level=level, show_file_line=show_file_line)
