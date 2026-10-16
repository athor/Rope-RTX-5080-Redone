"""Verify telemetry cannot limit frame delivery or continuously spin the UI."""
import threading
import unittest

from PySide6.QtCore import QCoreApplication, QEvent, QEventLoop, QObject, QTimer, Signal, Slot

from rope.qt.bus import bus
from rope.qt.coordinator import Coordinator


class VM:
    def __init__(self):
        self.control = {}
        self.parameters = {}
    def set_frame_callback(self, callback): self.callback = callback
    def get_frame_length(self): return 2
    def get_requested_frame_length(self): return 1
    def __getattr__(self, name): return lambda *_: None


class Models:
    vram_dirty = True
    def get_gpu_memory(self): return 4.0, 16.0


class Probe(Coordinator):
    def __init__(self, **kwargs):
        self.calls = 0
        super().__init__(**kwargs)
    def _tick(self):
        self.calls += 1
        super()._tick()


class Receiver(QObject):
    @Slot(object, bool)
    def receive(self, frame, requested): self.frames.append((frame, requested))


class TelemetryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QCoreApplication.instance() or QCoreApplication([])

    def setUp(self):
        self.vm = VM()
        self.coordinator = Probe(models=Models(), vm=self.vm)

    def tearDown(self):
        self.coordinator._process_timer.stop()
        self.coordinator.deleteLater()
        self.app.sendPostedEvents(None, QEvent.DeferredDelete)

    def pump(self, milliseconds):
        loop = QEventLoop()
        QTimer.singleShot(milliseconds, loop.quit)
        loop.exec()

    def test_timer_does_not_spin_and_reports_dirty_memory_once(self):
        memory, queues = [], []
        def on_memory(used, total): memory.append((used, total))
        def on_queue(a, b): queues.append((a, b))
        bus.vram_updated.connect(on_memory)
        bus.queue_depths.connect(on_queue)
        try:
            self.pump(400)
            self.assertGreater(self.coordinator.calls, 0)
            self.assertLess(self.coordinator.calls, 25)
            self.assertEqual(memory, [(4.0, 16.0)])
            self.assertGreater(len(queues), 0)
            self.assertTrue(all(q == (2, 1) for q in queues))
        finally:
            bus.vram_updated.disconnect(on_memory)
            bus.queue_depths.disconnect(on_queue)

    def test_frames_and_playhead_arrive_without_telemetry_timer(self):
        self.coordinator._process_timer.stop()
        receiver = Receiver()
        receiver.frames = []
        positions = []
        bus.frame_ready.connect(receiver.receive)
        bus.playback_frame_changed.connect(positions.append)
        try:
            def produce():
                for i in range(60):
                    self.vm.callback(i, i, True)
            worker = threading.Thread(target=produce)
            worker.start()
            self.pump(200)
            worker.join()
            self.app.processEvents()
            self.assertEqual(receiver.frames, [(i, True) for i in range(60)])
            self.assertEqual(positions, list(range(60)))
            self.assertEqual(self.coordinator.calls, 0)
        finally:
            bus.frame_ready.disconnect(receiver.receive)
            bus.playback_frame_changed.disconnect(positions.append)

    def test_ui_without_backend_has_no_timer(self):
        coordinator = Coordinator(models=None, vm=None)
        self.assertFalse(coordinator._process_timer.isActive())
        coordinator.deleteLater()


if __name__ == '__main__':
    unittest.main(verbosity=2)
