"""
Utilidades para detección de soporte de colores en terminal.
"""
import os
import sys

def supports_color(args=None):
    if args and getattr(args, 'no_color', False):
        return False
    if not hasattr(sys.stdout, "isatty") or not sys.stdout.isatty():
        return False
    if os.name == "nt":
        return "ANSICON" in os.environ or "WT_SESSION" in os.environ or os.environ.get("TERM_PROGRAM") == "vscode"
    return True
