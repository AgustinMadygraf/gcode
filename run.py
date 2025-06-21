"""
Path: run.py
"""

import os
from cli.main import SvgToGcodeApp

if __name__ == "__main__":
    os.system('cls' if os.name == 'nt' else 'clear')
    app = SvgToGcodeApp()
    app.run()
