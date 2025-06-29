import os
import re

# Configura las carpetas a buscar
SEARCH_DIRS = ['adapters', 'application', 'domain']
CANDIDATES_FILE = 'vulture/candidates.txt'

# Regex para detectar definición de clase, función, método o variable
DEF_PATTERNS = [
    re.compile(rf"^\s*class\s+{{name}}\b"),
    re.compile(rf"^\s*def\s+{{name}}\b"),
    re.compile(rf"^\s*{{name}}\s*[:=]"),  # variable o atributo
]

def is_definition(line, name):
    for pat in DEF_PATTERNS:
        if pat.pattern.find('{name}') >= 0:
            pat = re.compile(pat.pattern.replace('{name}', re.escape(name)))
        if pat.match(line):
            return True
    return False

def find_references(name, search_dirs):
    results = []
    for search_dir in search_dirs:
        for root, _, files in os.walk(search_dir):
            for file in files:
                if file.endswith('.py'):
                    path = os.path.join(root, file)
                    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                        for idx, line in enumerate(f, 1):
                            if name in line:
                                results.append((path, idx, line.strip()))
    return results

with open(CANDIDATES_FILE, 'r', encoding='utf-8') as f:
    candidates = [line.strip() for line in f if line.strip()]

print("\n=== RESULTADO DE FILTRADO AUTOMÁTICO ===\n")
for candidate in candidates:
    refs = find_references(candidate, SEARCH_DIRS)
    # Filtra las referencias que son solo la definición
    non_def_refs = []
    for path, idx, line in refs:
        if not is_definition(line, candidate):
            non_def_refs.append((path, idx, line))
    if not non_def_refs:
        print(f"[OK] '{candidate}' solo aparece en su definición. SEGURO PARA ELIMINAR.")
    else:
        print(f"[REVISAR] '{candidate}' tiene referencias externas:")
        for path, idx, line in non_def_refs:
            print(f"   {path}:{idx}: {line}")