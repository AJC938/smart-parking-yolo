"""Phase 8 milestone: FastAPI endpoints serve live pipeline state.

Run directly: python tests/test_phase8_api.py
"""
import sys
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import requests
import uvicorn

from config import config
from src.backend.state import app_state
from src.backend.pipeline import PipelineWorker
from src.backend.api import app


def main():
    worker = PipelineWorker(app_state)
    worker.start()

    server = uvicorn.Server(uvicorn.Config(app, host=config.BACKEND_HOST, port=config.BACKEND_PORT, log_level="warning"))
    server_thread = threading.Thread(target=server.run, daemon=True)
    server_thread.start()

    time.sleep(3)  # let the pipeline warm up and produce a few frames
    base = f"http://{config.BACKEND_HOST}:{config.BACKEND_PORT}"

    for path in ["/api/health", "/api/status", "/api/parking"]:
        resp = requests.get(base + path, timeout=5)
        print(f"GET {path} -> {resp.status_code}")
        print(resp.json())
        print()

    server.should_exit = True
    worker.stop()
    time.sleep(1)


if __name__ == "__main__":
    main()
