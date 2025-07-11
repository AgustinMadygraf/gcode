"""
Operation: SVG to GCODE conversion.
"""

from cli.operations.base import CliOperation


class SvgToGcodeOperation(CliOperation):
    " Operation to convert SVG files to GCODE. "
    def __init__(self, workflow, selector, perf_timer=None):
        self.workflow = workflow
        self.selector = selector
        self.perf_timer = perf_timer

    def execute(self):
        " Execute the SVG to GCODE operation with interactive offset/center input. "
        # Prompt interactivo para offset y centrado
        print("¿Desea centrar el dibujo automáticamente? (s/n): ", end="")
        center_input = input().strip().lower()
        center = center_input in {"s", "si", "y", "yes"}
        offset_x = None
        offset_y = None
        if not center:
            while True:
                try:
                    offset_x = float(input("Ingrese offset X en mm (puede ser negativo, ENTER=0): ") or "0")
                    break
                except ValueError:
                    print("Valor inválido. Intente nuevamente.")
            while True:
                try:
                    offset_y = float(input("Ingrese offset Y en mm (puede ser negativo, ENTER=0): ") or "0")
                    break
                except ValueError:
                    print("Valor inválido. Intente nuevamente.")
        # Asignar los valores al workflow
        self.workflow.offset_x = offset_x
        self.workflow.offset_y = offset_y
        self.workflow.center = center
        if self.perf_timer:
            @self.perf_timer.timed_method()
            def _run():
                return self.workflow.run(self.selector)
            return _run()
        else:
            return self.workflow.run(self.selector)
