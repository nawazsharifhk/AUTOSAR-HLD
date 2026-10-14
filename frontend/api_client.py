import os
import sys
import time
import socket
import subprocess
import threading
import requests
import streamlit as st
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = str(Path(__file__).resolve().parent.parent)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

_server_process = None
_lock = threading.Lock()


def get_api_url() -> str:
    """
    Get the active Backend API URL.
    Checks st.secrets and environment variables, defaulting to local 127.0.0.1:8000.
    """
    # 1. Check Streamlit secrets
    try:
        if hasattr(st, "secrets") and "BACKEND_URL" in st.secrets:
            return st.secrets["BACKEND_URL"].rstrip("/")
        if hasattr(st, "secrets") and "API_URL" in st.secrets:
            return st.secrets["API_URL"].rstrip("/")
    except Exception:
        pass

    # 2. Check environment variables
    env_url = os.getenv("BACKEND_URL") or os.getenv("API_URL")
    if env_url:
        return env_url.rstrip("/")

    # 3. Default to localhost
    return "http://127.0.0.1:8000"


def is_backend_healthy(url: str, timeout: float = 1.0) -> bool:
    """Quick health check ping to backend."""
    try:
        r = requests.get(f"{url}/api/health", timeout=timeout)
        return r.status_code == 200
    except Exception:
        return False


def _auto_seed_if_empty():
    """Seed benchmark AUTOSAR documents if the database has zero documents."""
    try:
        from backend.database.session import SessionLocal, init_db
        from backend.models.db_models import DocumentModel
        from scripts.seed_sample_data import seed_database

        init_db()
        db = SessionLocal()
        count = db.query(DocumentModel).count()
        db.close()

        if count == 0:
            print("[AutoHLD-AI] Fresh deployment detected: Auto-seeding benchmark AUTOSAR HLD documents...")
            seed_database()
            print("[AutoHLD-AI] Seeding complete! Benchmark documents are ready.")
    except Exception as e:
        print(f"[AutoHLD-AI] Note during auto-seeding check: {e}")


def _start_local_backend(host: str = "127.0.0.1", port: int = 8000):
    """Start uvicorn server in background subprocess or thread."""
    global _server_process
    try:
        cmd = [sys.executable, "-m", "uvicorn", "backend.main:app", "--host", host, "--port", str(port)]
        kwargs = {"cwd": PROJECT_ROOT}
        if os.name == "nt":
            kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
        _server_process = subprocess.Popen(cmd, **kwargs)
        print(f"[AutoHLD-AI] Spawned background FastAPI backend process (PID {_server_process.pid})")
    except Exception as e:
        print(f"[AutoHLD-AI] Subprocess startup note: {e}, attempting thread runner fallback")
        def run():
            try:
                import uvicorn
                from backend.main import app
                config = uvicorn.Config(app=app, host=host, port=port, log_level="warning")
                server = uvicorn.Server(config)
                server.run()
            except Exception as thread_err:
                print(f"[AutoHLD-AI] Thread runner error: {thread_err}")

        t = threading.Thread(target=run, daemon=True, name="FastAPI-Backend-Thread")
        t.start()


def ensure_backend_alive() -> str:
    """
    Ensures that the backend is running and reachable.
    If running in a single-instance deployment (e.g. Streamlit Cloud),
    this starts the FastAPI backend in a background process and auto-seeds initial data.
    """
    api_url = get_api_url()

    # If backend points to an external remote server, return directly
    if not any(loc in api_url for loc in ["127.0.0.1", "localhost", "0.0.0.0"]):
        return api_url

    # Check session cache
    if st.session_state.get("backend_connected", False):
        if is_backend_healthy(api_url, timeout=0.6):
            return api_url

    # Check if backend is already responding
    if is_backend_healthy(api_url, timeout=0.8):
        st.session_state["backend_connected"] = True
        _auto_seed_if_empty()
        return api_url

    with _lock:
        # Re-check inside lock
        if is_backend_healthy(api_url, timeout=0.8):
            st.session_state["backend_connected"] = True
            _auto_seed_if_empty()
            return api_url

        print("[AutoHLD-AI] Starting background FastAPI backend server on 127.0.0.1:8000...")
        _start_local_backend("127.0.0.1", 8000)

        # Wait up to 60 seconds with user-visible feedback if inside Streamlit
        start_time = time.time()
        timeout = 60.0
        
        # Helper to wait
        def _wait_for_health():
            while time.time() - start_time < timeout:
                if is_backend_healthy(api_url, timeout=0.6):
                    return True
                time.sleep(1.0)
            return False

        try:
            with st.spinner("🚀 Launching AutoHLD-AI backend services and loading architecture intelligence models..."):
                ready = _wait_for_health()
        except Exception:
            ready = _wait_for_health()

        if ready:
            print(f"[AutoHLD-AI] Backend successfully connected after {time.time() - start_time:.1f}s")
            st.session_state["backend_connected"] = True
            _auto_seed_if_empty()
        else:
            print(f"[AutoHLD-AI] Backend startup timed out after {timeout}s")

    return api_url
