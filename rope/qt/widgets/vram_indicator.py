"""VRAM usage bar — QProgressBar with QSS chunk-color flip at >90%.

Replaces rope/GUIElements.py:VRAM_Indicator.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QProgressBar, QWidget


class VRAMIndicator(QProgressBar):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setRange(0, 100)
        self.setValue(0)
        self.setFormat("VRAM: --")
        self.setAlignment(Qt.AlignCenter)
        self.setProperty("overLimit", "false")

    def set(self, used_mib: float, total_mib: float) -> None:
        if total_mib <= 0:
            pct = 0.0
        else:
            pct = max(0.0, min(100.0, (float(used_mib) / float(total_mib)) * 100.0))
        used_gib = float(used_mib) / 1024.0
        total_gib = float(total_mib) / 1024.0
        self.setValue(int(round(pct)))
        self.setFormat(f"VRAM {used_gib:.1f} / {total_gib:.1f} GB - {pct:.0f}%")
        over = pct >= 90.0
        self.setProperty("overLimit", "true" if over else "false")
        self.style().unpolish(self); self.style().polish(self)
