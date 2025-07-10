"""
Operation: GCODE to GCODE (optimize/rescale).
"""
from cli.operations.base import CliOperation

class GcodeToGcodeOperation(CliOperation):
    " Operation to optimize or rescale GCODE files. "
    def __init__(self, workflow, config, perf_timer=None):
        self.workflow = workflow
        self.config = config
        self.perf_timer = perf_timer

    def execute(self):
        " Execute the GCODE to GCODE operation. "
        if self.perf_timer:
            @self.perf_timer.timed_method()
            def _run():
                return self.workflow.run(self.config)
            return _run()
        else:
            return self.workflow.run(self.config)
