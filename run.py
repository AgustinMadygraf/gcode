"""
Path: run.py
"""

import os
from cli.main import main

if __name__ == "__main__":
    os.system('cls' if os.name == 'nt' else 'clear')
    main()
