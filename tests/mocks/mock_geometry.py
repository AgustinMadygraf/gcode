"""
Mocks para pruebas relacionadas con geometría.
"""

class MockSegment:
    """
    Implementación simulada de un segmento geométrico para pruebas unitarias.
    Simplifica la representación de una línea o curva.
    """
    def __init__(self, start=0, end=1):
        self.start = start
        self.end = end
        self._start_point = complex(start, 0)
        self._end_point = complex(end, 0)
    
    def point(self, t):
        """
        Devuelve un punto en el segmento para el valor t (entre 0 y 1).
        t=0 devuelve el punto inicial, t=1 devuelve el punto final.
        """
        if t == 0:
            return self._start_point
        elif t == 1:
            return self._end_point
        else:
            # Interpolación lineal
            return complex(self.start + t * (self.end - self.start), 0)

    def __repr__(self):
        return f"MockSegment({self.start}, {self.end})"


class DummySegment:
    """
    Versión simplificada de segmento para casos de prueba donde solo se necesita
    una representación mínima de un segmento de línea o curva.
    """
    def __init__(self, start=(0,0), end=(1,1)):
        self.start = start
        self.end = end
        
    def point(self, t):
        """
        Devuelve un punto en el segmento para el valor t (entre 0 y 1).
        """
        if t == 0:
            return complex(*self.start)
        elif t == 1:
            return complex(*self.end)
        else:
            # Interpolación lineal
            x = self.start[0] + t * (self.end[0] - self.start[0])
            y = self.start[1] + t * (self.end[1] - self.start[1])
            return complex(x, y)
