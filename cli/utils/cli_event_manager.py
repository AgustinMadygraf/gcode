"""
EventManager centralizado para la suscripción y manejo de eventos CLI.
"""
from domain.events.events import GcodeGeneratedEvent, GcodeRescaledEvent

class CliEventManager:
    def __init__(self, presenter):
        self.presenter = presenter
        self._subscriptions = {}
        self._register_default_events()

    def _register_default_events(self):
        self.subscribe(GcodeGeneratedEvent, self._on_gcode_generated)
        self.subscribe(GcodeRescaledEvent, self._on_gcode_rescaled)

    def subscribe(self, event_type, handler):
        self._subscriptions.setdefault(event_type, []).append(handler)

    def publish(self, event):
        for handler in self._subscriptions.get(type(event), []):
            handler(event)

    def _on_gcode_generated(self, event):
        self.presenter.print_event('gcode_generated', {
            'output_file': event.output_file,
            'lines': event.lines,
            'metadata': event.metadata
        })

    def _on_gcode_rescaled(self, event):
        self.presenter.print_event('gcode_rescaled', {
            'output_file': event.output_file,
            'original_dimensions': event.original_dimensions,
            'new_dimensions': event.new_dimensions,
            'scale_factor': event.scale_factor,
            'commands_rescaled': event.commands_rescaled
        })
