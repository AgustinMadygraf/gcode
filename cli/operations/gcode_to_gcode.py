"""
Operation: GCODE to GCODE (optimize/rescale).
"""
from cli.operations.base import CliOperation
from infrastructure.performance.timing import PerformanceTimer

class GcodeToGcodeOperation(CliOperation):
    def __init__(self, workflow, config):
        self.workflow = workflow
        self.config = config

    @PerformanceTimer.timed_method()
    def execute(self):
        return self.workflow.run(self.config)
