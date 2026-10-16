"""Exercise real decoder teardown using a generated video, without model loads."""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
from pathlib import Path
import tempfile
import time
import unittest

import cv2
import numpy as np
from PySide6.QtWidgets import QApplication

from rope.VideoManager import VideoManager
from rope.qt.parameters import default_values, seed_control_dict


class MediaReleaseTests(unittest.TestCase):
    def test_playing_video_is_released_and_next_media_still_loads(self):
        app = QApplication.instance() or QApplication([])
        with tempfile.TemporaryDirectory(prefix='rope-release-test-', dir=Path.cwd()) as tmp:
            video = Path(tmp) / 'generated.avi'
            writer = cv2.VideoWriter(str(video), cv2.VideoWriter_fourcc(*'MJPG'), 24, (64, 64))
            self.assertTrue(writer.isOpened())
            for i in range(48):
                writer.write(np.full((64, 64, 3), i * 5, dtype=np.uint8))
            writer.release()
            vm = VideoManager(None)
            vm.control = seed_control_dict()
            vm.parameters = default_values(scope='parameter')
            try:
                self.assertEqual(vm.audio_volume, 0.5)
                vm.load_target_video(str(video))
                self.assertTrue(vm.is_video_loaded)
                vm.play_video('play')
                time.sleep(0.15)
                vm.unload_target_media()
                self.assertIsNone(vm.player)
                self.assertFalse(vm.is_video_loaded)
                self.assertFalse(vm.is_image_loaded)
                self.assertFalse(vm.play)
                self.assertTrue(vm._pacer_thread.is_alive())
                self.assertTrue(vm._scrub_thread.is_alive())
                renamed = video.with_name('released.avi')
                video.rename(renamed)
                vm.load_target_video(str(renamed))
                self.assertTrue(vm.is_video_loaded)
                vm.submit_scrub(1)
                time.sleep(0.1)
                vm.unload_target_media()
                renamed.unlink()
            finally:
                vm.play = False
                vm._pacer_stop.set()
                vm._scrub_stop.set()
                with vm._scrub_cond:
                    vm._scrub_cond.notify_all()
                vm._pacer_thread.join(timeout=5)
                vm._scrub_thread.join(timeout=5)
                if vm.player is not None:
                    vm.player.close()
                if vm._executor is not None:
                    vm._executor.shutdown(wait=True)
            del app


if __name__ == '__main__':
    unittest.main(verbosity=2)
