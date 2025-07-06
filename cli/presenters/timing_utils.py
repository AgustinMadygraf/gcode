import time
from functools import wraps

# DEPRECATED: Usar infrastructure.performance.timing.PerformanceTimer en su lugar.
def timed_log(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        dev_mode = kwargs.get('dev_mode', False)
        # No medir tiempo para input
        if method.__name__ == 'input':
            return method(self, *args, **kwargs)
        if dev_mode:
            start = time.perf_counter()
            result = method(self, *args, **kwargs)
            elapsed = time.perf_counter() - start
            # Si el método ya acepta 'elapsed', pásalo
            if 'elapsed' in method.__code__.co_varnames:
                kwargs['elapsed'] = elapsed
                return method(self, *args, **kwargs)
            else:
                # Si no, solo imprime el tiempo aquí (fallback)
                print(f"[DEV] Tiempo: {elapsed:.3f}s")
            return result
        else:
            return method(self, *args, **kwargs)
    return wrapper
