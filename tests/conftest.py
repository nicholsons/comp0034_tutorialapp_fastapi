import os

import pytest

from backend.core.config import get_settings


@pytest.fixture(scope="session", autouse=True)
def set_test_env():
    os.environ["ENV"] = "testing"
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()
