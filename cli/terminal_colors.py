"""
Utilidad para colorear texto en terminal.
"""
import os
from cli.utils.terminal_utils import supports_color

class TerminalColors:
    def __init__(self, use_colors=True, args=None):
        # Usa supports_color para decidir si activar colores
        self.use_colors = use_colors and supports_color(args)
    def red(self, text):
        return f"\033[91m{text}\033[0m" if self.use_colors else text
    def green(self, text):
        return f"\033[92m{text}\033[0m" if self.use_colors else text
    def yellow(self, text):
        return f"\033[93m{text}\033[0m" if self.use_colors else text
    def blue(self, text):
        return f"\033[94m{text}\033[0m" if self.use_colors else text
    def cyan(self, text):
        return f"\033[96m{text}\033[0m" if self.use_colors else text  # Celeste
    def magenta(self, text):
        return f"\033[95m{text}\033[0m" if self.use_colors else text  # Rosa
    def bold(self, text):
        return f"\033[1m{text}\033[0m" if self.use_colors else text
    def colorize(self, text, color):
        if not self.use_colors or not color:
            return text
        color_method = getattr(self, color, None)
        if callable(color_method):
            return color_method(text)
        return text
