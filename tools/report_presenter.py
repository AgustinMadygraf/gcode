"""
Path: tools/report_presenter.py
"""

import os
import re
import shutil

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

EXCLUDED_SYMBOLS = [
    "health_check",
    "optimize_gcode",
    "list_presets"
]

PROTECTED_DECORATORS = [
    "@router.get", "@router.post", "@app.route", "@blueprint.route"
]

class ReportPresenter:
    " Clase para presentar el reporte de símbolos no utilizados. "
    def is_referenced_indirectly(self, symbol):
        """Busca el símbolo como string, en getattr, hasattr, setattr y otros patrones dinámicos."""
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        patterns = [
            rf'["\'\u0019]{re.escape(symbol)}["\'\u0019]',  # Como string
            rf'getattr\([^,]+,\s*["\'\u0019]{re.escape(symbol)}["\'\u0019]',
            rf'hasattr\([^,]+,\s*["\'\u0019]{re.escape(symbol)}["\'\u0019]',
            rf'setattr\([^,]+,\s*["\'\u0019]{re.escape(symbol)}["\'\u0019]'
        ]
        references = []
        for root, _, files in os.walk(project_root):
            for fname in files:
                if fname.endswith(('.py', '.yml', '.yaml', '.json', '.ini', '.md')):
                    fpath = os.path.join(root, fname)
                    try:
                        with open(fpath, encoding='utf-8', errors='ignore') as f:
                            for idx, line in enumerate(f, 1):
                                for pat in patterns:
                                    if re.search(pat, line):
                                        references.append(f"{fpath}:{idx}: {line.strip()}")
                    except (OSError, IOError):
                        continue
        return references

    def _get_class_hierarchy(self, file_path):
        """
        Devuelve un dict {clase: [bases]} para el archivo dado.
        """
        class_hierarchy = {}
        class_pattern = re.compile(r'class\s+([A-Za-z_][A-Za-z0-9_]*)\s*(?:\(([^)]*)\))?:')
        try:
            with open(file_path, encoding='utf-8', errors='ignore') as f:
                for line in f:
                    m = class_pattern.match(line.strip())
                    if m:
                        cls = m.group(1)
                        bases = [b.strip() for b in m.group(2).split(',')] if m.group(2) else []
                        class_hierarchy[cls] = bases
        except (OSError, IOError):
            pass
        return class_hierarchy

    def _find_method_in_bases(self, method, class_name, file_path, project_root):
        """
        Busca si el método existe en alguna superclase del proyecto.
        """
        # 1. Obtener jerarquía local
        hierarchy = self._get_class_hierarchy(file_path)
        if class_name not in hierarchy:
            return False
        bases = hierarchy[class_name]
        # 2. Buscar definición de la base en el proyecto
        for base in bases:
            if not base or base in ('object',):
                continue
            for root, _, files in os.walk(project_root):
                for fname in files:
                    if fname.endswith('.py'):
                        fpath = os.path.join(root, fname)
                        with open(fpath, encoding='utf-8', errors='ignore') as f:
                            lines = f.readlines()
                        # Buscar class base
                        inside = False
                        indent = None
                        for _, line in enumerate(lines):
                            if re.match(rf'class\s+{re.escape(base)}\b', line):
                                inside = True
                                indent = len(line) - len(line.lstrip())
                                continue
                            if inside:
                                # Si cambia la indentación, termina la clase
                                if line.strip() == '' or (len(line) - len(line.lstrip()) <= indent):
                                    inside = False
                                    continue
                                # Buscar método
                                if re.match(rf'\s*def\s+{re.escape(method)}\s*\(', line):
                                    return True
        return False

    def calculate_risk_level(self, item, file_path, strict_checks=True):
        """
        Calcula el nivel de riesgo de eliminar un símbolo basado en varios factores.
        Riesgo ALTO: tiene comentario especial (# @keep) cerca de la definición.
        Riesgo MEDIO: aparece como string, getattr, hasattr, setattr en otros archivos.
        Riesgo BAJO: solo aparece en su archivo de definición.
        Riesgo ALTO: si el método sobrescribe uno de una superclase.
        strict_checks: Si True, aplica verificaciones más estrictas (modo conservador)
        """
        # 1. Verificar si tiene comentario especial cerca
        try:
            with open(file_path, encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            line_num = int(item['line']) - 1
            for offset in range(-2, 3):
                idx = line_num + offset
                if 0 <= idx < len(lines):
                    if '# @keep' in lines[idx]:
                        return 'ALTO'
        except (OSError, IOError):
            pass

        # 1b. Si es método, buscar si sobrescribe uno de una superclase
        # En modo estricto, siempre verificamos herencia
        # En modo agresivo, ignoramos herencia para métodos privados (_method)
        if item['type'] == 'method':
            if strict_checks or not item['symbol'].startswith('_'):
                try:
                    with open(file_path, encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                    line_num = int(item['line']) - 1
                    for i in range(line_num, -1, -1):
                        m = re.match(r'\s*class\s+([A-Za-z_][A-Za-z0-9_]*)\s*(?:\(([^)]*)\))?:', lines[i])
                        if m:
                            class_name = m.group(1)
                            if self._find_method_in_bases(item['symbol'], class_name, file_path, PROJECT_ROOT):
                                return 'ALTO'
                            break
                except (OSError, IOError):
                    pass

        # 2. Buscar referencias indirectas (string, getattr, hasattr, setattr)
        symbol = item['symbol']
        # En modo estricto, consideramos cualquier referencia indirecta
        # En modo agresivo, ignoramos ciertas referencias para símbolos privados
        if strict_checks or not symbol.startswith('_'):
            references = self.is_referenced_indirectly(symbol)
            if references:
                item['references'] = references
                return 'MEDIO'

        # 3. Evaluar por convenciones de nombres en modo estricto
        if strict_checks and (symbol.startswith('__') or (item['type'] == 'method' and symbol.startswith('_'))):
            return 'MEDIO'  # Métodos privados requieren revisión adicional en modo conservador

        # 4. Por defecto, riesgo bajo
        return 'BAJO'
    def auto_remove_symbols(self, symbols):
        """
        Elimina automáticamente la definición de los símbolos 'MUY SEGURO'
        en sus archivos correspondientes.
        Soporta: class, function, method, import, attribute (básico y decoradores).
        """
        # Filtrar símbolos excluidos
        symbols = [item for item in symbols if item['symbol'] not in EXCLUDED_SYMBOLS]
        removed = []
        for item in symbols:
            file_path = os.path.join(PROJECT_ROOT, item['file'])
            backup_path = file_path + '.bak_unused'
            print(
                "\n[DEBBUG] Procesando símbolo: "
                + f"{item['symbol']} "
                + f"({item['type']}) "
                + f"en {item['file']}:{item['line']}"
            )
            if not os.path.exists(backup_path):
                shutil.copy2(file_path, backup_path)
                print(f"[DEBBUG] Backup creado: {backup_path}")
            else:
                print(f"[DEBBUG] Backup ya existe: {backup_path}")
            with open(file_path, encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            symbol = item['symbol']
            tipo = item['type']
            _removed_block = False

            def get_def_pattern(symbol, tipo):
                escaped_symbol = re.escape(symbol)
                if tipo in ('function', 'method'):
                    return re.compile(rf'(async\s+)?def\s+{escaped_symbol}\s*\(', re.IGNORECASE)
                elif tipo == 'class':
                    return re.compile(rf'class\s+{escaped_symbol}\s*[(:]', re.IGNORECASE)
                else:
                    return re.compile(rf'{escaped_symbol}', re.IGNORECASE)

            def_pattern = get_def_pattern(symbol, tipo)
            definition_line = -1
            for i, line in enumerate(lines):
                if def_pattern.search(line):
                    # Verificar si la función está protegida por decorador
                    decorador_protegido = False
                    check_line = i - 1
                    while (
                        check_line >= 0 and (
                            lines[check_line].strip().startswith('@')
                            or lines[check_line].strip() == ''
                            or lines[check_line].strip().startswith('#')
                        )
                    ):
                        for decorador in PROTECTED_DECORATORS:
                            if lines[check_line].strip().startswith(decorador):
                                decorador_protegido = True
                                break
                        if decorador_protegido:
                            break
                        check_line -= 1
                    if decorador_protegido:
                        print(
                            "[DEBBUG] No se elimina "
                            f"{symbol} porque tiene decorador protegido en "
                            f"{item['file']}:{item['line']}"
                        )
                        definition_line = -1
                        break
                    definition_line = i
                    break

            if definition_line < 0:
                print(
                    "[DEBBUG] No se encontró la definición para eliminar en "
                    f"{item['file']}:{item['line']} "
                    f"({tipo} {symbol})"
                )
                # Imprimir contexto de 10 líneas alrededor de la línea reportada
                try:
                    line_num = int(item['line']) - 1
                    start_c = max(0, line_num - 5)
                    end_c = min(len(lines), line_num + 5)
                    print(
                        "[DEBBUG] Contexto en "
                        + f"{item['file']} "
                        + "alrededor de la línea "
                        + f"{item['line']}:"
                    )
                    for idx in range(start_c, end_c):
                        prefix = '>>' if idx == line_num else '  '
                        print(f"{prefix} {idx+1:4}: {lines[idx].rstrip()}")
                except (ValueError, IndexError) as e:
                    print(f"[DEBBUG] No se pudo mostrar el contexto: {e}")
                continue

            # Buscar decoradores hacia arriba (para funciones/métodos)
            start_line = definition_line
            if tipo in ['function', 'method']:
                current_line = definition_line - 1
                while current_line >= 0:
                    if lines[current_line].strip().startswith('@'):
                        start_line = current_line
                        current_line -= 1
                    elif (
                        lines[current_line].strip() == ''
                        or lines[current_line].strip().startswith('#')
                    ):
                        current_line -= 1
                    else:
                        break

            # Determinar indentación del bloque
            indentation = len(lines[definition_line]) - len(lines[definition_line].lstrip())
            # Buscar final del bloque
            end_line = definition_line
            for i in range(definition_line + 1, len(lines)):
                if (
                    i >= len(lines)
                    or (
                        lines[i].strip()
                        and (
                            len(lines[i]) - len(lines[i].lstrip())
                            <= indentation
                        )
                    )
                ):
                    end_line = i - 1
                    break
                end_line = i

            print(
                "[INFO] Eliminando símbolo "
                + f"{symbol} "
                + f"({tipo}) - líneas "
                + f"{start_line+1} a {end_line+1}"
            )
            lines = lines[:start_line] + lines[end_line+1:]
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            removed.append(f"{item['file']}:{item['line']} {tipo} {symbol}")
        if removed:
            print("\nSímbolos eliminados automáticamente:")
            for r in removed:
                print(f"- {r}")
            print("\nDetalles de los cambios:")
            for item in symbols:
                print(
                    f"\nArchivo: {item['file']}\n"
                    f"  Tipo: {item['type']}\n"
                    f"  Símbolo: {item['symbol']}\n"
                    f"  Línea: {item['line']}\n"
                    f"  Confianza: {item['confidence']}%\n"
                    f"  Nivel: {'MUY SEGURO' if item.get('muy_seguro') else ''}"
                )
                print(
                    f"  Backup creado: {item['file']}.bak_unused"
                )
        else:
            print("\nNo se eliminó ningún símbolo automáticamente.")
    def show(self, unused, reference_finder):
        """
        Muestra los símbolos no utilizados que son seguros para eliminar.
        Marca como 'MUY SEGURO' aquellos que no aparecen en ningún otro archivo del proyecto.
        """
        encontrados = []
        for item in unused:
            if not reference_finder.is_symbol_used(item['symbol'], item['file']):
                # Verificar si aparece en algún otro archivo (no solo .py)
                muy_seguro = not reference_finder.is_symbol_used_anywhere(
                    item['symbol'],
                    item['file']
                )
                item['muy_seguro'] = muy_seguro
                # Calcular nivel de riesgo
                file_path = os.path.join(PROJECT_ROOT, item['file'])
                item['risk_level'] = self.calculate_risk_level(item, file_path)
                encontrados.append(item)
        print("Símbolos seguros para eliminar:\n")
        print(f"Cantidad de símbolos encontrados: {len(encontrados)}\n")
        if encontrados:
            print(
                f"{'Archivo':60} "
                f"{'Tipo':>10} "
                f"{'Símbolo':>25} "
                f"{'Confianza':>10} "
                f"{'Nivel':>12} "
                f"{'Riesgo':>10}"
            )
            print("-" * 135)
            for item in encontrados:
                archivo_linea = f"{item['file']}:{item['line']}"
                nivel = 'MUY SEGURO' if item.get('muy_seguro') else ''
                riesgo = item.get('risk_level', '')
                print(
                    f"{archivo_linea:<60} "
                    f"{item['type']:>10} "
                    f"{item['symbol']:>25} "
                    f"{item['confidence']:>9}% "
                    f"{nivel:>12} "
                    f"{riesgo:>10}"
                )
        else:
            print("No se encontraron símbolos seguros para eliminar.")
