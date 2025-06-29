import re

# Este script genera un plan de eliminación para los elementos [OK] SEGURO PARA ELIMINAR
# usando el reporte de vulture y la lista de candidatos.
# Genera una lista de archivos y líneas a modificar para automatizar la limpieza.

# 1. Parsear el reporte de vulture para obtener ubicaciones
vulture_report = 'vulture/vulture_report.txt'
candidates_file = 'vulture/candidates.txt'
plan_file = 'vulture/ok_removal_plan.txt'

# Leer candidatos
with open(candidates_file, 'r', encoding='utf-8') as f:
    candidates = set(line.strip() for line in f if line.strip())

# Parsear el reporte de vulture (ahora con encoding utf-16)
ok_locations = []
with open(vulture_report, 'r', encoding='utf-16') as f:
    for line in f:
        m = re.match(r"(.+?):(\d+): unused (?:class|method|function|variable|import) '([^']+)'", line)
        if m:
            file, lineno, name = m.groups()
            if name in candidates:
                ok_locations.append((file.replace('\\', '/'), int(lineno), name))

# Guardar plan
with open(plan_file, 'w', encoding='utf-8') as f:
    for file, lineno, name in ok_locations:
        f.write(f"{file}:{lineno}:{name}\n")

print(f"Plan de eliminación generado en {plan_file} ({len(ok_locations)} elementos)")
