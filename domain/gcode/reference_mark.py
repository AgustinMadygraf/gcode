"""
Lógica de dominio para generar el G-code de una marca de referencia (cruz + círculo).
"""

def reference_mark_gcode(x, y, direction, feed):
    """
    Devuelve el G-code (sin comandos de máquina) para una marca de referencia en la esquina indicada.
    direction: 'bottomleft', 'bottomright', 'topleft', 'topright'
    """
    if direction == 'bottomleft':
        xh, yh = x, y+5
        xv, yv = x+5, y
        xc, yc = x+5, y+5
        sign_x, sign_y = 1, 1
    elif direction == 'bottomright':
        xh, yh = x, y+5
        xv, yv = x-5, y
        xc, yc = x-5, y+5
        sign_x, sign_y = -1, 1
    elif direction == 'topleft':
        xh, yh = x, y-5
        xv, yv = x+5, y
        xc, yc = x+5, y-5
        sign_x, sign_y = 1, -1
    else:  # topright
        xh, yh = x, y-5
        xv, yv = x-5, y
        xc, yc = x-5, y-5
        sign_x, sign_y = -1, -1

    gcode = [
        f"G0 X{xh} Y{yh}",
        "CMD_DOWN",
        f"G1 X{xh+10*sign_x} Y{yh} F{feed}",
        "CMD_UP",
        "DWELL",
        f"G0 X{xv} Y{yv}",
        "CMD_DOWN",
        f"G1 X{xv} Y{yv+10*sign_y} F{feed}",
        "CMD_UP",
        "DWELL",
        f"G0 X{xc+5*sign_x} Y{yc}",
        "CMD_DOWN",
        f"G2 X{xc+5*sign_x} Y{yc} I{(-5)*sign_x} J0 F{feed}",
        "CMD_UP",
        "DWELL"
    ]
    return gcode
