import re

with open('vulture/vulture_report.txt', 'r', encoding='utf-16') as f:
    lines = f.readlines()

with open('vulture/candidates.txt', 'w', encoding='utf-8') as out:
    found = False
    for idx, line in enumerate(lines):
        print(f"[DEBUG] Línea {idx+1}: {line.strip()}")
        match = re.search(
            r"^(?P<file>[\w\\\/\.]+):(?P<line>\d+): unused (?P<type>class|method|function|variable|import) '(?P<name>[\w_]+)' \((?P<confidence>\d+)% confidence\)",
            line
        )
        if match:
            found = True
            print(
                f"[MATCH] {match.group('type').capitalize():8} | {match.group('name'):30} | {match.group('file')}:{match.group('line')} | Confianza: {match.group('confidence')}%"
            )
            out.write(match.group('name') + '\n')

    if not found:
        print("[INFO] No se encontraron coincidencias con el patrón. Revisa el formato del archivo o el patrón de regex.")