# Modelos de Dominio y Reglas de Invariantes

Este documento describe los modelos de dominio principales del proyecto GCode, sus invariantes y reglas de negocio asociadas. Sirve como referencia para desarrolladores y para la evolución del diseño.

---

## DomainSegment

**Descripción:**
Objeto de valor inmutable que representa un segmento entre dos puntos en 2D.

**Atributos:**
- `start: Point` (punto inicial)
- `end: Point` (punto final)

**Invariantes:**
- `start` y `end` deben ser instancias válidas de `Point`.
- Un segmento no puede tener longitud cero (`start != end`).

**Reglas de negocio:**
- Los segmentos son inmutables: no se pueden modificar tras su creación.
- Dos segmentos con los mismos puntos (sin importar el orden) pueden considerarse iguales según el contexto.

---

## DomainPath

**Descripción:**
Entidad que representa un camino formado por una secuencia ordenada de segmentos.

**Atributos:**
- `segments: List[DomainSegment]`
- (Opcional) `closed: bool` (indica si el camino es cerrado)

**Invariantes:**
- La lista de segmentos no puede estar vacía.
- Los segmentos deben estar conectados: el `end` de un segmento debe coincidir con el `start` del siguiente.
- Si `closed` es `True`, el `end` del último segmento debe coincidir con el `start` del primero.

**Reglas de negocio:**
- Un `DomainPath` es responsable de validar su propia consistencia al crearse.
- Métodos de transformación (traslación, rotación, escalado) deben devolver nuevas instancias.

---

## Ejemplo de Test de Invariantes

```python
# test_domain_segment.py
def test_segment_no_zero_length():
    with pytest.raises(ValueError):
        DomainSegment(Point(0,0), Point(0,0))

def test_path_segments_connected():
    s1 = DomainSegment(Point(0,0), Point(1,0))
    s2 = DomainSegment(Point(1,0), Point(2,0))
    DomainPath([s1, s2])  # No error
    s3 = DomainSegment(Point(3,0), Point(4,0))
    with pytest.raises(ValueError):
        DomainPath([s1, s3])
```

---

## Notas
- Estos modelos deben usarse en puertos y servicios del dominio, evitando exponer tipos de librerías externas.
- Las invariantes deben validarse en los constructores o métodos de factoría.
- Se recomienda documentar reglas adicionales en los docstrings del código fuente.
