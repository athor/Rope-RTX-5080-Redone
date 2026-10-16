"""Check rendering-only presets, signal batching, guards and button placement."""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
from PySide6.QtCore import QEvent
from PySide6.QtWidgets import QApplication, QMessageBox

from rope.qt.face_swap_presets import FACE_SWAP_PRESETS, HIGH_REQUIRED_MODELS, matching_preset
from rope.qt.main_window import MainWindow
from rope.qt.parameters import PARAMETER_BY_NAME
from rope.qt.settings import Settings


class PresetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])
        cls.app.setStyleSheet(Path("rope/qt/rope.qss").read_text(encoding="utf-8"))

    def setUp(self):
        # Presence-only fixtures: preset tests never load inference models.
        self.models_dir = tempfile.TemporaryDirectory(prefix="rope-preset-test-", dir=Path.cwd())
        for name in HIGH_REQUIRED_MODELS:
            (Path(self.models_dir.name) / name).touch()
        self.patches = [patch.object(Settings, "load", return_value=Settings(models_folder=self.models_dir.name)),
                        patch.object(Settings, "save"),
                        patch("rope.qt.main_window.QMessageBox.warning")]
        for item in self.patches:
            item.start()
        self.w = MainWindow()

    def tearDown(self):
        self.w._faces_panel._shutdown_loader()
        self.w._videos_panel._shutdown_loader()
        self.w._source_face_index_pool.shutdown(wait=True)
        self.w.deleteLater()
        self.app.sendPostedEvents(None, QEvent.DeferredDelete)
        for item in reversed(self.patches):
            item.stop()
        self.models_dir.cleanup()

    def test_profiles_resolve_valid_rendering_values(self):
        forbidden = {"ThreadsSlider", "ModelSessionsTextSel", "DetectTypeTextSel",
                     "DetectInputSizeTextSel", "DetectScoreSlider", "RecordTypeTextSel",
                     "VideoQualSlider", "CaptureFPSSlider", "MergeTextSel", "ThresholdSlider"}
        for preset in FACE_SWAP_PRESETS.values():
            self.assertFalse(forbidden.intersection(preset))
            for key, value in preset.items():
                param = PARAMETER_BY_NAME[key]
                if param.kind == "select":
                    self.assertIn(value, param.modes)
                elif param.kind == "slider":
                    self.assertGreaterEqual(value, param.min)
                    self.assertLessEqual(value, param.max)
                    self.assertAlmostEqual((value-param.min)/param.inc,
                                           round((value-param.min)/param.inc))
                elif param.kind == "switch":
                    self.assertIsInstance(value, bool)
                else:
                    self.fail(f"Unexpected preset parameter: {key}")

    def test_buttons_apply_one_snapshot_without_changing_other_settings(self):
        pane = self.w._params_pane
        before = dict(pane.values)
        snapshots = []
        pane.params_changed.connect(snapshots.append)
        for name in ("high", "low", "high"):
            snapshots.clear()
            self.w._center_pane.buttons["Auto"+name.title()+"Button"].click()
            self.assertEqual(len(snapshots), 1)
            self.assertEqual(pane.values, before | FACE_SWAP_PRESETS[name])
            for key, value in FACE_SWAP_PRESETS[name].items():
                self.assertEqual(pane.widgets[key].get(), value)
            self.assertEqual(matching_preset(pane.values), name)
            self.assertEqual(self.w._center_pane.buttons["Auto"+name.title()+"Button"].property("state"), "on")

    def test_custom_adjustment_clears_active_preset(self):
        self.w._on_face_swap_preset("low")
        self.w._params_pane.widgets["BlendSlider"].set(9)
        self.assertIsNone(matching_preset(self.w._params_pane.values))
        self.assertEqual(self.w._center_pane.buttons["AutoLowButton"].property("state"), "off")

    def test_missing_high_models_or_recording_does_not_change_settings(self):
        before = dict(self.w._params_pane.values)
        self.w.settings.models_folder = str(Path.cwd() / "archive" / "nonexistent-models-test")
        self.w._on_face_swap_preset("high")
        self.assertEqual(self.w._params_pane.values, before)
        QMessageBox.warning.assert_called_once()
        self.w._is_recording = True
        self.w._on_face_swap_preset("low")
        self.assertEqual(self.w._params_pane.values, before)

    def test_faces_stay_assigned_and_old_worker_cannot_repopulate_new_cache(self):
        emb = np.ones(512, dtype=np.float32)
        old_slot = dict(Embedding=emb, AssignedEmbedding=emb,
                        SourceFaceAssignments=["source.png"], HFCorrectionGap=emb,
                        HFCorrectionGapSamples=2, HFRefinePending=True)
        self.w._found_faces = [old_slot]
        self.w._on_face_swap_preset("low")
        new_slot = self.w._found_faces[0]
        self.assertIsNot(new_slot, old_slot)
        self.assertIs(new_slot["AssignedEmbedding"], emb)
        self.assertEqual(new_slot["SourceFaceAssignments"], ["source.png"])
        self.assertIsNone(new_slot["HFCorrectionGap"])
        old_slot["HFCorrectionGap"] = emb * 2
        self.assertIsNone(new_slot["HFCorrectionGap"])

    def test_separator_and_buttons_are_immediately_after_delete_video(self):
        buttons = self.w._center_pane.buttons
        row = buttons["DeleteVideoButton"].parentWidget()
        layout = row.layout()
        index = layout.indexOf(buttons["DeleteVideoButton"])
        self.assertEqual(layout.itemAt(index+1).widget().objectName(), "FaceSwapPresetSeparator")
        self.assertIs(layout.itemAt(index+2).widget(), buttons["AutoLowButton"])
        self.assertIs(layout.itemAt(index+3).widget(), buttons["AutoHighButton"])
        self.w._on_face_swap_preset("high")
        row.resize(1800, 44)
        layout.activate()
        path = Path("archive/diagnostics/auto-presets-row.png")
        self.assertTrue(row.grab().save(str(path)))


if __name__ == "__main__":
    unittest.main(verbosity=2)
