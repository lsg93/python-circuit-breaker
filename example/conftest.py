from typing import Generator

import pytest
from fastapi.testclient import TestClient

from .app import app


@pytest.fixture()
def client() -> Generator:
    with TestClient(app) as c:
        yield c
