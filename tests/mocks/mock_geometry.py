"""
Mocks para pruebas relacionadas con geometría.
"""

class MockSegment:
    """
    Implementación simulada de un segmento geométrico para pruebas unitarias.
    Simplifica la representación de una línea o curva.
    """
    def __init__(self, length=None, start=(0,0), end=(1,0)):
        self._start = start
        self._end = end
        self._length = length if length is not None else self._calculate_length()
    
    def _calculate_length(self):
        """Calcula la longitud del segmento basado en los puntos de inicio y fin"""
        x_diff = self._end[0] - self._start[0]
        y_diff = self._end[1] - self._start[1]
        return ((x_diff ** 2) + (y_diff ** 2)) ** 0.5
    
    def length(self):
        """Devuelve la longitud del segmento"""
        return self._length
    
    def point(self, t):
        """
        Devuelve un punto en el segmento para el valor t (entre 0 y 1).
        t=0 devuelve el punto inicial, t=1 devuelve el punto final.
        """
        x = self._start[0] + (self._end[0] - self._start[0]) * t
        y = self._start[1] + (self._end[1] - self._start[1]) * t
        return complex(x, y)

    def __repr__(self):
        return f"MockSegment({self._length}, {self._start}, {self._end})"


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
            
    def length(self):
        """
        Calcula la longitud del segmento basada en los puntos de inicio y fin.
        """
        x0, y0 = self.start
        x1, y1 = self.end
        return ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5
