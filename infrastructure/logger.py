"""
Logger setup for the application.
Soporta niveles: INPUT, INFO, DEBUG, ERROR, WARN, y colores ANSI.
"""
import logging
import sys
import inspect
import os

class AnsiColor:
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
    LEVELS = {'DEBUG': 10, 'INFO': 20, 'OPTION': 21, 'INPUT': 15, 'WARNING': 30, 'ERROR': 40}
    def __init__(self, use_color=True, stream=sys.stderr, level='INFO', show_file_line=False):
        self.use_color = use_color
        self.stream = stream
        self.level = self.LEVELS.get(level.upper(), 20)
        self.show_file_line = show_file_line

    def set_level(self, level):
        if isinstance(level, int):
            self.level = level
        else:
            self.level = self.LEVELS.get(str(level).upper(), 20)

    def _should_log(self, level):
        lvl = self.LEVELS.get(level, 20)
        return lvl >= self.level or level in ('INPUT', 'OPTION')

    def _log(self, level, msg, *args, **kwargs):
        if not self._should_log(level):
            return
        prefix = LEVEL_PREFIXES.get(level, '[INFO]')
        color = LEVEL_COLORS.get(level, '') if self.use_color else ''
        reset = AnsiColor.RESET if self.use_color and color else ''
        # Añadir archivo:línea si es INFO y show_file_line está activo
        if (level == 'INFO' and self.show_file_line) or (level == 'DEBUG' and self.show_file_line):
            import os
            stack = inspect.stack()
            logger_file = os.path.abspath(__file__)
            caller_frame = None
            for frame_info in stack:
                frame_file = os.path.abspath(frame_info.filename)
                if frame_file != logger_file:
                    caller_frame = frame_info
                    break
            if caller_frame:
                filename = os.path.basename(caller_frame.filename)
                lineno = caller_frame.lineno
                prefix = f"[{level} {filename}:{lineno}]" if level in LEVEL_PREFIXES else f"[INFO {filename}:{lineno}]"
            else:
                prefix = LEVEL_PREFIXES.get(level, '[INFO]')
        else:
            prefix = LEVEL_PREFIXES.get(level, '[INFO]')
        print(f"{color}{prefix} {msg}{reset}", file=self.stream)

    def info(self, msg, *args, **kwargs):
        self._log('INFO', msg, *args, **kwargs)
    def debug(self, msg, *args, **kwargs):
        self._log('DEBUG', msg, *args, **kwargs)
    def error(self, msg, *args, **kwargs):
        self._log('ERROR', msg, *args, **kwargs)
    def warning(self, msg, *args, **kwargs):
        self._log('WARNING', msg, *args, **kwargs)
    def input(self, msg, *args, **kwargs):
        self._log('INPUT', msg, *args, **kwargs)
    def option(self, msg, *args, **kwargs):
        self._log('OPTION', msg, *args, **kwargs)

# Instancia global por defecto
logger = ConsoleLogger(use_color=True)

def get_logger(use_color=True, level='INFO', show_file_line=False):
    return ConsoleLogger(use_color=use_color, level=level, show_file_line=show_file_line)
