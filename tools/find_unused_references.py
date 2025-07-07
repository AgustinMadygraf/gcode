"""
Path: tools/find_unused_references.py
Analizador de código muerto en adapters con POO y SOLID
ejecuta Vulture, filtra rutas, busca referencias y reporta símbolos seguros para eliminar.
"""

import os
import re
import argparse
import chardet

from tools.vulture_runner import VultureRunner
from tools.report_presenter import ReportPresenter

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Carpetas a analizar de más externa a más interna
ANALYSIS_FOLDERS = [
    "adapters",
    "interfaces",
    "infrastructure",
    "application",
    "domain"
]
REPORT_PATH = os.path.join(PROJECT_ROOT, 'vulture_report.txt')
EXCLUDE = "tests/,tools/"

class VultureReportParser:
    " Clase para analizar el reporte de Vulture y extraer símbolos no utilizados. "
    def __init__(self, report_path):
        self.report_path = report_path

    def parse(self):
        " Analiza el reporte de Vulture y devuelve una lista de símbolos no utilizados. "
        unused = []
        pattern = re.compile(
            r"^(.*?):(\d+): unused "
            r"(import|class|method|function|attribute) "
            r"'([^']+)' "
            r"\((\d+)% confidence\)"
        )
        with open(self.report_path, 'rb') as f:
            raw = f.read()
            encoding = chardet.detect(raw)['encoding']
        with open(self.report_path, encoding=encoding) as f:
            for line in f:
                m = pattern.match(line.strip())
                if m:
                    unused.append({
                        'file': m.group(1).replace("\\", os.sep),
                        'line': m.group(2),
                        'type': m.group(3),
                        'symbol': m.group(4),
                        'confidence': m.group(5)
                    })
        return unused

class ReferenceFinder:
    " Clase para buscar referencias a símbolos en el código. "
    def is_symbol_used_anywhere(self, symbol, skip_file):
        """
        Busca el símbolo en todo el proyecto 
        (incluyendo archivos .py, .yml, .yaml, .json, .ini, .md),
        ignorando el archivo donde se define. 
        Devuelve True si lo encuentra fuera del archivo original.
        """
        pattern = re.compile(fr'\b{re.escape(symbol)}\b')
        text_exts = ['.py', '.yml', '.yaml', '.json', '.ini', '.md']
        for root, _, files in os.walk(self.project_root):
            for fname in files:
                if not any(fname.endswith(ext) for ext in text_exts):
                    continue
                fpath = os.path.join(root, fname)
                abs_fpath = os.path.abspath(fpath)
                abs_skip_file = os.path.abspath(os.path.join(self.project_root, skip_file))
                if abs_fpath == abs_skip_file:
                    continue
                try:
                    with open(fpath, encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        if pattern.search(content):
                            return True
                except (OSError, UnicodeDecodeError):
                    continue
        return False

    def __init__(self, project_root):
        self.project_root = project_root

    def is_symbol_used(self, symbol, skip_file):
        """
        Verifica si un símbolo está siendo utilizado en el proyecto, 
        ignorando un archivo específico.
        Utiliza expresiones regulares para coincidencias exactas de palabra.
        """
        pattern = re.compile(fr'\b{re.escape(symbol)}\b')
        for root, _, files in os.walk(self.project_root):
            for fname in files:
                if fname.endswith('.py'):
                    fpath = os.path.join(root, fname)
                    abs_fpath = os.path.abspath(fpath)
                    abs_skip_file = os.path.abspath(
                        os.path.join(
                            self.project_root,
                            skip_file
                        )
                    )
                    if abs_fpath == abs_skip_file:
                        continue
                    with open(fpath, encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        if pattern.search(content):
                            return True
        return False

    def calculate_risk_level(self, item, file_path):
        """
        Calcula el nivel de riesgo de eliminar un símbolo basado en varios factores.
        Riesgo ALTO: tiene comentario especial (# @keep) cerca de la definición.
        Riesgo MEDIO: aparece como string en otros archivos.
        Riesgo BAJO: solo aparece en su archivo de definición.
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
        except (OSError, UnicodeDecodeError):
            pass

        # 2. Buscar referencias como string en otros archivos y guardarlas
        symbol = item['symbol']
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        found_as_string = False
        references = []
        for root, _, files in os.walk(project_root):
            for fname in files:
                if fname.endswith(('.py', '.yml', '.yaml', '.json', '.ini', '.md')):
                    fpath = os.path.join(root, fname)
                    if os.path.abspath(fpath) == os.path.abspath(file_path):
                        continue
                    try:
                        with open(fpath, encoding='utf-8', errors='ignore') as f:
                            for idx, line in enumerate(f, 1):
                                if re.search(rf'["\'\u0019]{re.escape(symbol)}["\'\u0019]', line):
                                    found_as_string = True
                                    references.append(f"{fpath}:{idx}: {line.strip()}")
                    except (OSError, UnicodeDecodeError):
                        continue
            if found_as_string:
                break
        if found_as_string:
            item['references'] = references
            return 'MEDIO'

        # 3. Por defecto, riesgo bajo
        return 'BAJO'

def process_folder(folder, aggressiveness, round_num, finder, parser, presenter, processed_folders, args):
    folder_key = f"{folder}-{aggressiveness['name']}"
    if folder_key in processed_folders:
        print(f"\nOmitiendo carpeta ya procesada: {folder}")
        return

    print(f"\nAnalizando carpeta: {folder}")
    vulture = VultureRunner(folder, EXCLUDE, REPORT_PATH)
    vulture.run()
    unused = parser.parse()
    encontrados = []
    muy_seguros = []
    riesgo_bajo = []

    motivos_no_eliminados = []
    for item in unused:
        # Filtrar por umbral de confianza según la ronda
        if int(item['confidence']) < aggressiveness['confidence_threshold']:
            item['motivo_no_eliminado'] = f"Confianza ({item['confidence']}%) menor al umbral ({aggressiveness['confidence_threshold']}%)"
            motivos_no_eliminados.append(item)
            continue

        if not finder.is_symbol_used(item['symbol'], item['file']):
            muy_seguro = not finder.is_symbol_used_anywhere(
                item['symbol'], item['file']
            )
            item['muy_seguro'] = muy_seguro

            # Calcular riesgo usando el presentador con nivel de agresividad
            file_path = os.path.join(PROJECT_ROOT, item['file'])
            item['risk_level'] = presenter.calculate_risk_level(item, file_path, aggressiveness['strict_checks'])

            # En modo agresivo, bajar nivel de riesgo para ciertos tipos
            if not aggressiveness['strict_checks']:
                if item['risk_level'] == 'MEDIO' and item['type'] in ['attribute', 'import']:
                    item['risk_level'] = 'BAJO'
                    item['downgraded'] = True

            encontrados.append(item)
            if muy_seguro:
                muy_seguros.append(item)
            if item['risk_level'] == 'BAJO':
                riesgo_bajo.append(item)
        else:
            item['motivo_no_eliminado'] = "Referencia directa encontrada en el proyecto"
            motivos_no_eliminados.append(item)

    if encontrados:
        print(f"\nRONDA {round_num+1} ({aggressiveness['name']}): Símbolos seguros para eliminar:")
        presenter.show(unused, finder)

        # Eliminar automáticamente símbolos con riesgo BAJO
        if riesgo_bajo:
            print(f"\nEliminando automáticamente {len(riesgo_bajo)} símbolos con riesgo BAJO:")
            presenter.auto_remove_symbols(riesgo_bajo)

        print(f"\nSe encontraron {len(encontrados)} símbolos seguros para eliminar en '{folder}'.")

        processed_folders.add(folder_key)
    else:
        print("No se encontraron símbolos seguros para eliminar en esta carpeta.")

    # Reporte de motivos para símbolos no eliminados (solo si flag activa)
    if args.motivos and motivos_no_eliminados:
        print(f"\nMotivos por los que NO se eliminaron {len(motivos_no_eliminados)} símbolos en '{folder}':")
        for item in motivos_no_eliminados:
            print(f"- {item['file']}:{item['line']} {item['type']} {item['symbol']} -> {item.get('motivo_no_eliminado','(sin motivo)')}")

def main():
    " Función principal para ejecutar el análisis de código muerto. "

    parser_args = argparse.ArgumentParser(description="Análisis de código muerto con reporte opcional de motivos de no eliminación.")
    parser_args.add_argument('--motivos', action='store_true', help='Imprime los motivos por los que NO se eliminaron símbolos')
    args = parser_args.parse_args()

    finder = ReferenceFinder(PROJECT_ROOT)
    parser = VultureReportParser(REPORT_PATH)
    presenter = ReportPresenter()
    processed_folders = set()

    # Dos rondas: conservadora y agresiva
    for round_num, aggressiveness in enumerate([
        {"name": "CONSERVADORA", "confidence_threshold": 80, "strict_checks": True},
        {"name": "AGRESIVA", "confidence_threshold": 60, "strict_checks": False}
    ]):
        print(f"\n{'='*80}\nRONDA {round_num+1}: ANÁLISIS {aggressiveness['name']}\n{'='*80}")
        print(f"Umbral de confianza: {aggressiveness['confidence_threshold']}%")
        print(f"Verificaciones estrictas: {'Sí' if aggressiveness['strict_checks'] else 'No'}")

        for folder in ANALYSIS_FOLDERS:
            process_folder(folder, aggressiveness, round_num, finder, parser, presenter, processed_folders, args)

if __name__ == "__main__":
    main()
