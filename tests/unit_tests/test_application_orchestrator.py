"""
Test básico para ApplicationOrchestrator y EventManager
"""
import unittest
from application.orchestrator import ApplicationOrchestrator
from infrastructure.events.event_manager import EventManager

class DummyWorkflow:
    def __init__(self):
        self.ran = False
    def run(self, *args, **kwargs):
        self.ran = True
        return 'ok'

class DummyModeStrategy:
    def run(self, orchestrator):
        return orchestrator.workflows['dummy'].run()

class TestApplicationOrchestrator(unittest.TestCase):
    def test_orchestrator_runs_workflow(self):
        dummy_workflow = DummyWorkflow()
        orchestrator = ApplicationOrchestrator(
            container=None,
            presenter=None,
            filename_service=None,
            config=None,
            event_bus=None,
            workflows={'dummy': dummy_workflow},
            operations={},
            mode_strategy=DummyModeStrategy(),
            args=None
        )
        result = orchestrator.run()
        self.assertTrue(dummy_workflow.ran)
        self.assertEqual(result, 'ok')

class TestEventManager(unittest.TestCase):
    def test_event_manager_publish_and_subscribe(self):
        manager = EventManager()
        events = []
        class DummyEvent: pass
        def handler(event):
            events.append(event)
        manager.subscribe(DummyEvent, handler)
        event = DummyEvent()
        manager.publish(event)
        self.assertEqual(events, [event])

if __name__ == "__main__":
    unittest.main()
