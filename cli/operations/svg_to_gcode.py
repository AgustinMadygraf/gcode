"""
Operation: SVG to GCODE conversion.
"""
from cli.operations.base import CliOperation
from infrastructure.performance.timing import PerformanceTimer

class SvgToGcodeOperation(CliOperation):
    def __init__(self, workflow, selector):
        self.workflow = workflow
        self.selector = selector

    @PerformanceTimer.timed_method()
    def execute(self):
        return self.workflow.run(self.selector)
