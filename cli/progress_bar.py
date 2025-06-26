"""
Utilidad para mostrar una barra de progreso ASCII en terminal.
"""
import sys
import time

def print_progress_bar(iteration, total, prefix='', suffix='', length=40, fill='█', print_end="\r", accessible=False):
    if accessible or not sys.stdout.isatty():
        # Modo accesible: solo imprime porcentaje y mensaje final
        percent = (iteration / float(total)) * 100 if total else 100
        if iteration == total:
            print(f"{prefix} 100% {suffix}")
        return
    percent = (iteration / float(total)) * 100 if total else 100
    filled_length = int(length * iteration // total) if total else length
    bar = fill * filled_length + '-' * (length - filled_length)
    # No hay mensajes de usuario aquí, solo formato de barra. Si se agregan mensajes, usar i18n.
    # Si se agregan mensajes de usuario, usar i18n.get('clave')
    print(f'\r{prefix} |{bar}| {percent:3.0f}% {suffix}', end=print_end)
    if iteration == total:
        print()
