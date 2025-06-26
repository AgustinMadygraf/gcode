"""
Operation: GCODE to GCODE (optimize/rescale).
"""
from cli.operations.base import CliOperation

class GcodeToGcodeOperation(CliOperation):
    def __init__(self, workflow, config):
        self.workflow = workflow
        self.config = config

    def execute(self):
        return self.workflow.run(self.config)
