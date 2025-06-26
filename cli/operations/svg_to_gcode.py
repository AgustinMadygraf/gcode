"""
Operation: SVG to GCODE conversion.
"""
from cli.operations.base import CliOperation

class SvgToGcodeOperation(CliOperation):
    def __init__(self, workflow, selector):
        self.workflow = workflow
        self.selector = selector

    def execute(self):
        return self.workflow.run(self.selector)
