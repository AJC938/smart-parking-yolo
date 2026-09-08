"""Main dashboard window for the Smart Parking Intelligence System."""
import cv2
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from config import config
from src.backend.state import AppState
from src.gui.styles import COLOR_BAD, COLOR_GOOD, COLOR_TEXT_MUTED, STYLESHEET
from src.gui.widgets import Card, SpaceGrid, StatTile, StatusDot


class MainWindow(QMainWindow):
    def __init__(self, state: AppState):
        super().__init__()
        self.state = state
        self.setWindowTitle(config.GUI_WINDOW_TITLE)
        self.resize(1280, 760)
        self.setStyleSheet(STYLESHEET)

        self._build_ui()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._refresh)
        self.timer.start(config.GUI_REFRESH_MS)

    # ---- UI construction -------------------------------------------------

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_header())

        body = QHBoxLayout()
        body.setContentsMargins(16, 16, 16, 16)
        body.setSpacing(16)
        root.addLayout(body, stretch=1)

        body.addWidget(self._build_left_panel(), stretch=0)
        body.addWidget(self._build_right_panel(), stretch=1)

    def _build_header(self) -> QWidget:
        header = QFrame()
        header.setObjectName("HeaderBar")
        header.setFixedHeight(56)
        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 0, 20, 0)

        title = QLabel("Smart Parking Intelligence")
        title.setObjectName("HeaderTitle")
        layout.addWidget(title)

        subtitle = QLabel("YOLO + ByteTrack Vehicle Detection & Occupancy Monitoring")
        subtitle.setObjectName("HeaderSubtitle")
        layout.addWidget(subtitle)
        layout.addStretch()

        self.system_status_dot = QLabel("● SYSTEM STARTING")
        self.system_status_dot.setStyleSheet(f"color: {COLOR_TEXT_MUTED}; font-weight: 600;")
        layout.addWidget(self.system_status_dot)

        return header

    def _build_left_panel(self) -> QWidget:
        panel = QWidget()
        panel.setFixedWidth(340)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        # Parking analytics card
        analytics = Card("Parking Analytics")
        stats_row1 = QHBoxLayout()
        self.tile_total = StatTile("TOTAL SPACES")
        self.tile_occupied = StatTile("OCCUPIED")
        stats_row1.addWidget(self.tile_total)
        stats_row1.addWidget(self.tile_occupied)
        stats_row2 = QHBoxLayout()
        self.tile_available = StatTile("AVAILABLE")
        self.tile_rate = StatTile("OCCUPANCY RATE")
        stats_row2.addWidget(self.tile_available)
        stats_row2.addWidget(self.tile_rate)
        analytics.body.addLayout(stats_row1)
        analytics.body.addLayout(stats_row2)
        layout.addWidget(analytics)

        # Parking space status card
        spaces_card = Card("Parking Space Status")
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMaximumHeight(280)
        self.space_grid = SpaceGrid()
        scroll.setWidget(self.space_grid)
        spaces_card.body.addWidget(scroll)
        layout.addWidget(spaces_card)

        # System status card
        system_card = Card("System Status")
        self.status_video = StatusDot("Video Source")
        self.status_yolo = StatusDot("YOLO Detection")
        self.status_tracking = StatusDot("Vehicle Tracking")
        self.status_backend = StatusDot("Backend Service")
        for w in (self.status_video, self.status_yolo, self.status_tracking, self.status_backend):
            system_card.body.addWidget(w)
        self.error_label = QLabel("")
        self.error_label.setStyleSheet(f"color: {COLOR_BAD}; font-size: 11px;")
        self.error_label.setWordWrap(True)
        system_card.body.addWidget(self.error_label)
        layout.addWidget(system_card)

        layout.addStretch()
        return panel

    def _build_right_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        self.video_label = QLabel()
        self.video_label.setObjectName("VideoFrame")
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setMinimumSize(640, 480)
        self.video_label.setText("Waiting for video stream...")
        layout.addWidget(self.video_label, stretch=1)

        footer = QFrame()
        footer.setProperty("class", "Card")
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(16, 8, 16, 8)

        self.footer_fps = QLabel("FPS: --")
        self.footer_yolo = StatusDot("YOLO Active")
        self.footer_tracking = StatusDot("Tracking Active")
        footer_layout.addWidget(self.footer_fps)
        footer_layout.addStretch()
        footer_layout.addWidget(self.footer_yolo)
        footer_layout.addWidget(self.footer_tracking)
        layout.addWidget(footer)

        return panel

    # ---- live refresh ------------------------------------------------------

    def _refresh(self):
        snap = self.state.snapshot()

        # System status
        online = snap.system.backend_ok and not snap.system.error_message
        self.system_status_dot.setText("● SYSTEM ONLINE" if online else "● SYSTEM ERROR")
        self.system_status_dot.setStyleSheet(
            f"color: {COLOR_GOOD if online else COLOR_BAD}; font-weight: 600;"
        )
        self.status_video.set_state(snap.system.video_ok)
        self.status_yolo.set_state(snap.system.yolo_ok)
        self.status_tracking.set_state(snap.system.tracking_ok)
        self.status_backend.set_state(snap.system.backend_ok)
        self.error_label.setText(snap.system.error_message)

        self.footer_fps.setText(f"FPS: {snap.fps:.1f}")
        self.footer_yolo.set_state(snap.system.yolo_ok)
        self.footer_tracking.set_state(snap.system.tracking_ok)

        # Analytics
        self.tile_total.set_value(str(snap.total_spaces))
        self.tile_occupied.set_value(str(snap.occupied_spaces), COLOR_BAD)
        self.tile_available.set_value(str(snap.available_spaces), COLOR_GOOD)
        self.tile_rate.set_value(f"{snap.occupancy_rate:.0f}%")

        # Parking space grid
        if snap.spaces:
            self.space_grid.ensure_spaces([s.id for s in snap.spaces])
            self.space_grid.update_statuses({s.id: s.occupied for s in snap.spaces})

        # Video frame
        if snap.frame is not None:
            self._set_video_frame(snap.frame)

    def _set_video_frame(self, frame_bgr):
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        qimage = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qimage).scaled(
            self.video_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.video_label.setPixmap(pixmap)

    def closeEvent(self, event):
        self.timer.stop()
        super().closeEvent(event)
