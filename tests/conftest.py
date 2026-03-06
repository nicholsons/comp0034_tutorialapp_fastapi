import shutil
import subprocess
import threading
import time
from pathlib import Path
from urllib.request import urlopen

import pytest
import uvicorn
from streamlit.testing.v1 import AppTest


def wait_for_http(url, timeout=10):
    start = time.time()
    while True:
        try:
            urlopen(url, timeout=1)
            return
        except Exception:
            if time.time() - start > timeout:
                raise RuntimeError(f"Server did not start in time: {url}")
            time.sleep(0.1)


@pytest.fixture(scope="session", autouse=True)
def api_server():
    """Start the REST API server before Dash app tests.

     Makes a copy of the database before the server starts, and to replace
     the original at the end of the tests.
     NB this is not a recommended approach, this will be covered when the REST API is tested
    """

    # Create a copy of the database
    root = Path(__file__).parent.parent
    _orig_db = root.joinpath("src", "data", "paralympics.db")
    _backup_db = _orig_db.with_suffix(_orig_db.suffix + ".orig")

    if not _orig_db.exists():
        raise RuntimeError(f"Original DB not found: {_orig_db}")

    # backup original
    shutil.copy2(_orig_db, _backup_db)

    from data.api import app

    thread = threading.Thread(
        target=uvicorn.run,
        kwargs={
            "app": app,
            "host": "127.0.0.1",
            "port": 8000,
            "reload": False
        },
        daemon=True,
    )
    thread.start()

    wait_for_http("http://127.0.0.1:8000")

    yield

    # Teardown: restore original DB
    if _backup_db.exists():
        shutil.copy2(_backup_db, _orig_db)
        try:
            _backup_db.unlink()
        except Exception:
            pass


@pytest.fixture(scope="session")
def app_server():
    """Start a Streamlit app server for Playwright tests using the subprocess library."""

    app_path = "src/paralympics/paralympics_dashboard.py"
    port = "8501"
    url = f"http://127.0.0.1:{port}"

    process = subprocess.Popen([
        *('streamlit', 'run', app_path),
        *('--server.port', port),
        *('--server.headless', 'false'),
    ])

    # Wait for Streamlit app to be ready
    wait_for_http(url)

    yield url

    # Clean shutdown        
    if process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()


@pytest.fixture()
def at():
    app_file = Path(__file__).parent.parent.joinpath("src", "paralympics",
                                                     "paralympics_dashboard.py")
    at = AppTest.from_file(app_file)
    at.run()
    yield at
