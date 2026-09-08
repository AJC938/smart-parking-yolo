"""Small reusable dashboard widgets: stat tiles, status dots, space badges."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QGridLayout, QWidget

from src.gui.styles import COLOR_BAD, COLOR_GOOD, COLOR_TEXT_MUTED, COLOR_WARN


class Card(QFrame):
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setProperty("class", "Card")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 14)
        layout.setSpacing(8)

        title_label = QLabel(title.upper())
        title_label.setProperty("class", "CardTitle")
        layout.addWidget(title_label)

        self.body = QVBoxLayout()
        self.body.setSpacing(6)
        layout.addLayout(self.body)


class StatTile(QWidget):
    def __init__(self, label: str, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        self.value_label = QLabel("--")
        self.value_label.setProperty("class", "StatValue")
        layout.addWidget(self.value_label)

        text_label = QLabel(label)
        text_label.setProperty("class", "StatLabel")
        layout.addWidget(text_label)

    def set_value(self, value: str, color: str | None = None):
        self.value_label.setText(value)
        if color:
            self.value_label.setStyleSheet(f"color: {color};")


class StatusDot(QWidget):
    """A colored dot + text label, e.g. for 'YOLO Active'."""

    def __init__(self, label: str, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        self.dot = QLabel("●")
        self.dot.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-size: 12px;")
        layout.addWidget(self.dot)

        self.text = QLabel(label)
        layout.addWidget(self.text)
        layout.addStretch()

    def set_state(self, ok: bool, warn: bool = False):
        color = COLOR_WARN if warn else (COLOR_GOOD if ok else COLOR_BAD)
        self.dot.setStyleSheet(f"color: {color}; font-size: 12px;")


class SpaceBadge(QFrame):
    """A small badge showing one parking space's id + status."""

    def __init__(self, space_id: str, parent=None):
        super().__init__(parent)
        self.space_id = space_id
        self.setMinimumHeight(40)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 4, 6, 4)
        layout.setSpacing(0)

        self.id_label = QLabel(space_id)
        self.id_label.setAlignment(Qt.AlignCenter)
        self.id_label.setStyleSheet("font-weight: 600; font-size: 12px;")
        layout.addWidget(self.id_label)

        self.status_label = QLabel("--")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-size: 9px;")
        layout.addWidget(self.status_label)

        self.set_status(None)

    def set_status(self, occupied: bool | None):
        if occupied is None:
            bg, fg, text = "#252b3b", COLOR_TEXT_MUTED, "UNKNOWN"
        elif occupied:
            bg, fg, text = "#3a2029", COLOR_BAD, "OCCUPIED"
        else:
            bg, fg, text = "#1d3327", COLOR_GOOD, "AVAILABLE"
        self.setStyleSheet(f"QFrame {{ background-color: {bg}; border-radius: 6px; }}")
        self.id_label.setStyleSheet(f"font-weight: 600; font-size: 12px; color: {fg};")
        self.status_label.setStyleSheet(f"font-size: 9px; color: {fg};")
        self.status_label.setText(text)


class SpaceGrid(QWidget):
    """Grid of SpaceBadge widgets, rebuilt once space ids are known."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.grid = QGridLayout(self)
        self.grid.setSpacing(6)
        self.badges: dict[str, SpaceBadge] = {}

    def ensure_spaces(self, space_ids: list[str], columns: int = 3):
        if set(space_ids) == set(self.badges.keys()):
            return
        for badge in self.badges.values():
            badge.setParent(None)
        self.badges.clear()
        for i, sid in enumerate(space_ids):
            badge = SpaceBadge(sid)
            self.grid.addWidget(badge, i // columns, i % columns)
            self.badges[sid] = badge

    def update_statuses(self, statuses: dict[str, bool]):
        for sid, occupied in statuses.items():
            if sid in self.badges:
                self.badges[sid].set_status(occupied)
