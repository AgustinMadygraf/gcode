"""
Utilidad para calcular y aplicar el offset vertical (Y) en instrucciones G-code.
El offset se calcula como la diferencia entre el área máxima de la plotter y el área objetivo de escritura.
"""

def calcular_offset_y(plotter_max_area_mm, target_write_area_mm):
    """
    Calcula el offset vertical (Y) a aplicar.
    Args:
        plotter_max_area_mm (tuple/list): (ancho, alto) máximo de la plotter en mm.
        target_write_area_mm (tuple/list): (ancho, alto) del área objetivo en mm.
    Returns:
        float: Offset en Y (mm)
    """
    return plotter_max_area_mm[1] - target_write_area_mm[1]


def aplicar_offset_y_a_gcode_linea(linea, offset_y):
    """
    Si la línea es un comando G0 o G1 con coordenada Y, suma el offset a Y.
    Args:
        linea (str): línea de G-code.
        offset_y (float): offset a sumar en Y.
    Returns:
        str: línea modificada (o igual si no aplica)
    """
    import re
    match_g0g1 = re.match(r'^(G0|G1)(.*)', linea.strip(), re.IGNORECASE)
    match_g2g3 = re.match(r'^(G2|G3)(.*)', linea.strip(), re.IGNORECASE)
    if match_g0g1:
        cmd, params = match_g0g1.groups()
        def reemplazar_y(m):
            valor = float(m.group(1))
            return f'Y{valor + offset_y:.3f}'
        params_mod = re.sub(r'Y([\-\d\.]+)', reemplazar_y, params)
        return f'{cmd}{params_mod}'
    elif match_g2g3:
        cmd, params = match_g2g3.groups()
        def reemplazar_y(m):
            valor = float(m.group(1))
            return f'Y{valor + offset_y:.3f}'
        params_mod = re.sub(r'Y([\-\d\.]+)', reemplazar_y, params)
        return f'{cmd}{params_mod}'
    else:
        return linea


def aplicar_offset_y_a_gcode(gcode_lines, offset_y):
    """
    Aplica el offset Y a una lista de líneas de G-code.
    Args:
        gcode_lines (list[str]): líneas de G-code.
        offset_y (float): offset a sumar en Y.
    Returns:
        list[str]: líneas modificadas
    """
    return [aplicar_offset_y_a_gcode_linea(linea, offset_y) for linea in gcode_lines]
