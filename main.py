"""Smart Parking Intelligence System -- application entry point.

Starts the CV pipeline worker, the FastAPI backend, and the PySide6 GUI.
"""
import sys
import threading

import uvicorn
from PySide6.QtWidgets import QApplication

from config import config
from src.backend.api import app as fastapi_app
from src.backend.state import app_state
from src.backend.pipeline import PipelineWorker
from src.gui.main_window import MainWindow


def start_backend_server():
    server = uvicorn.Server(
        uvicorn.Config(fastapi_app, host=config.BACKEND_HOST, port=config.BACKEND_PORT, log_level="warning")
    )
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    return server


def main():
    pipeline_worker = PipelineWorker(app_state)
    pipeline_worker.start()

    start_backend_server()

    qt_app = QApplication(sys.argv)
    window = MainWindow(app_state)
    window.show()

    exit_code = qt_app.exec()
    pipeline_worker.stop()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
