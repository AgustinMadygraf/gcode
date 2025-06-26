"""
Utilidad para colorear texto en terminal.
"""
import os

class TerminalColors:
    def __init__(self, use_colors=True):
        self.use_colors = use_colors and os.name != "nt"  # Desactivar en Windows por defecto
    def red(self, text):
        return f"\033[91m{text}\033[0m" if self.use_colors else text
    def green(self, text):
        return f"\033[92m{text}\033[0m" if self.use_colors else text
    def yellow(self, text):
        return f"\033[93m{text}\033[0m" if self.use_colors else text
    def blue(self, text):
        return f"\033[94m{text}\033[0m" if self.use_colors else text
    def bold(self, text):
        return f"\033[1m{text}\033[0m" if self.use_colors else text
