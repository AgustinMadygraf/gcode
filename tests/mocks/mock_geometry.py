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
        self.start = complex(start[0], start[1])
        self.end = complex(end[0], end[1])
        self.start_point = self.start
        self.end_point = self.end
        
    def point(self, t):
        """
        Devuelve un punto en el segmento para el valor t (entre 0 y 1).
        """
        if t == 0:
            return self.start
        elif t == 1:
            return self.end
        else:
            x = self.start.real + t * (self.end.real - self.start.real)
            y = self.start.imag + t * (self.end.imag - self.start.imag)
            return complex(x, y)
            
    def length(self):
        """
        Calcula la longitud del segmento basada en los puntos de inicio y fin.
        """
        return abs(self.end - self.start)


class CustomMockSegment(MockSegment):
    """
    Mock especializado para tests que simula un segmento de línea de (0,0) a (10,10).
    """
    def point(self, t):
        # Simula un segmento de línea de (0,0) a (10,10)
        return complex(10 * t, 10 * t)
