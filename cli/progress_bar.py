"""
Utilidad para mostrar una barra de progreso ASCII en terminal.
"""
import sys
import time

def print_progress_bar(iteration, total, prefix='', suffix='', length=40, fill='█', print_end="\r"):
    percent = (iteration / float(total)) * 100 if total else 100
    filled_length = int(length * iteration // total) if total else length
    bar = fill * filled_length + '-' * (length - filled_length)
    print(f'\r{prefix} |{bar}| {percent:3.0f}% {suffix}', end=print_end)
    if iteration == total:
        print()
