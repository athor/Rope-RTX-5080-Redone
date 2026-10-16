"""Media deletion tests use generated fixtures only; user media is never touched."""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
from PySide6.QtCore import QRect, Qt
from PySide6.QtGui import QColor, QPainter, QPixmap
from PySide6.QtWidgets import QApplication, QMessageBox, QStyle, QStyleOptionViewItem

from rope.qt.main_window import MainWindow
from rope.qt.settings import Settings
from rope.qt.panes.left_pane import _ASSIGNED_ROLE


class DeleteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='rope-delete-test-', dir=Path.cwd())
        self.root = Path(self.tmp.name)
        self.patches = [
            patch.object(Settings, 'load', return_value=Settings()),
            patch.object(Settings, 'save'),
            patch('rope.qt.thumbnails.ThumbnailLoader.request'),
            patch('rope.qt.main_window.QMessageBox.warning'),
            patch('rope.qt.main_window.QFile', SimpleNamespace(moveToTrash=self.recycle_fixture)),
        ]
        for p in self.patches:
            p.start()
        self.w = MainWindow()
        self.w._faces_panel._loader.request = lambda *_: None
        self.w._videos_panel._loader.request = lambda *_: None

    def tearDown(self):
        self.w._faces_panel._shutdown_loader()
        self.w._videos_panel._shutdown_loader()
        self.w._source_face_index_pool.shutdown(wait=True)
        self.w.deleteLater()
        self.app.sendPostedEvents(None, 0)
        for p in reversed(self.patches):
            p.stop()
        self.tmp.cleanup()

    def recycle_fixture(self, name):
        p = Path(name)
        assert p.parent == self.root, 'Test refuses to remove non-fixture files'
        p.unlink()
        return True

    def select(self, panel, *names):
        paths = []
        for name in names:
            p = self.root / name
            p.write_bytes(b'generated test fixture')
            paths.append(str(p))
        panel.populate_from_folder(str(self.root))
        panel.set_selected_paths(paths)
        return paths

    def test_defaults_and_buttons(self):
        cp = self.w._center_pane
        self.assertEqual(cp.volume_slider.value(), 50)
        self.assertTrue(cp.buttons['AudioButton'].get())
        self.assertTrue(self.w._control['AudioButton'])
        self.assertNotIn('SaveImageButton', cp.buttons)
        events = []
        cp.delete_image.disconnect()
        cp.delete_video.disconnect()
        cp.delete_image.connect(lambda: events.append('image'))
        cp.delete_video.connect(lambda: events.append('video'))
        cp.buttons['DeleteImageButton'].click()
        cp.buttons['DeleteVideoButton'].click()
        self.assertEqual(events, ['image', 'video'])

    def test_cancel_keeps_source_file_and_selection(self):
        paths = self.select(self.w._faces_panel, 'portrait.png')
        with patch.object(QMessageBox, 'exec', return_value=QMessageBox.Cancel):
            self.w._on_delete_image()
        self.assertTrue(Path(paths[0]).exists())
        self.assertEqual(self.w._faces_panel.selected_paths(), paths)

    def test_confirmed_source_deletion_clears_embedding_and_assignment(self):
        paths = self.select(self.w._faces_panel, 'portrait.png', 'portrait2.png')
        self.w._source_face_embeddings = {p: np.ones(512) for p in paths}
        self.w._selected_source_paths = list(paths)
        slot = dict(SourceFaceAssignments=list(paths), AssignedEmbedding=np.ones(512))
        self.w._found_faces = [slot]
        with patch.object(QMessageBox, 'exec', return_value=QMessageBox.Yes):
            self.w._on_delete_image()
        self.assertFalse(any(Path(p).exists() for p in paths))
        self.assertEqual(self.w._faces_panel.paths(), [])
        self.assertEqual(self.w._source_face_embeddings, {})
        self.assertEqual(slot['SourceFaceAssignments'], [])
        self.assertIsNone(slot['AssignedEmbedding'])
        self.w._on_source_face_indexed(paths[0], None, np.ones(512), self.w._source_face_index_generation)
        self.assertNotIn(paths[0], self.w._source_face_embeddings)

    def test_trash_failure_keeps_file_and_list_item(self):
        paths = self.select(self.w._faces_panel, 'portrait.png')
        with patch.object(QMessageBox, 'exec', return_value=QMessageBox.Yes), \
                patch('rope.qt.main_window.QFile', SimpleNamespace(moveToTrash=lambda _: False)):
            self.w._on_delete_image()
        self.assertTrue(Path(paths[0]).exists())
        self.assertEqual(self.w._faces_panel.paths(), paths)

    def test_replaced_file_is_not_deleted(self):
        paths = self.select(self.w._faces_panel, 'portrait.png')
        def changed(_dialog):
            Path(paths[0]).write_bytes(b'replaced after confirmation')
            return QMessageBox.Yes
        with patch.object(QMessageBox, 'exec', changed):
            self.w._on_delete_image()
        self.assertTrue(Path(paths[0]).exists())

    def test_video_unload_precedes_recycle(self):
        paths = self.select(self.w._videos_panel, 'video.mp4')
        self.w._current_media_path = paths[0]
        events = []
        self.w._coordinator = SimpleNamespace(vm=SimpleNamespace(
            unload_target_media=lambda: events.append('unload')))
        with patch.object(QMessageBox, 'exec', return_value=QMessageBox.Yes), \
                patch('rope.qt.main_window.QFile', SimpleNamespace(
                    moveToTrash=lambda p: events.append('recycle') or self.recycle_fixture(p))):
            self.w._on_delete_video()
        self.assertEqual(events, ['unload', 'recycle'])
        self.assertIsNone(self.w._current_media_path)
        self.assertFalse(Path(paths[0]).exists())

    def test_busy_video_and_recording_never_recycle(self):
        paths = self.select(self.w._videos_panel, 'video.mp4')
        self.w._current_media_path = paths[0]
        def busy():
            raise RuntimeError('decoder busy')
        self.w._coordinator = SimpleNamespace(vm=SimpleNamespace(unload_target_media=busy))
        with patch.object(QMessageBox, 'exec', return_value=QMessageBox.Yes):
            self.w._on_delete_video()
        self.assertTrue(Path(paths[0]).exists())
        self.w._is_recording = True
        with patch.object(QMessageBox, 'exec') as confirm:
            self.w._on_delete_video()
        confirm.assert_not_called()
        self.assertTrue(Path(paths[0]).exists())

    def test_green_border_remains_visible_without_focus_and_with_assignment(self):
        panel = self.w._faces_panel
        paths = self.select(panel, 'portrait.png')
        item = panel._items_by_path[paths[0]]
        item.setData(_ASSIGNED_ROLE, True)
        opt = QStyleOptionViewItem()
        opt.rect = QRect(0, 0, 112, 148)
        opt.state = QStyle.State_Enabled | QStyle.State_Selected
        pix = QPixmap(112, 148)
        pix.fill(Qt.black)
        painter = QPainter(pix)
        panel.list.itemDelegate().paint(painter, opt, panel.list.indexFromItem(item))
        painter.end()
        img = pix.toImage()
        self.assertEqual(img.pixelColor(2, 30), QColor('#39FF14'))
        self.assertEqual(img.pixelColor(6, 30), QColor('#FFD400'))
        pix.save(str(Path(__file__).with_name('selection-r02.png')))


if __name__ == '__main__':
    unittest.main(verbosity=2)
