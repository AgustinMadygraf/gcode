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
        " Execute the SVG to GCODE operation without interactive offset input. "
        # No se solicita offset X/Y aquí; se maneja después de la generación del GCODE
        self.workflow.center = False
        if self.perf_timer:
            @self.perf_timer.timed_method()
            def _run():
                return self.workflow.run(self.selector)
            return _run()
        else:
            return self.workflow.run(self.selector)
