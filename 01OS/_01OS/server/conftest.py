import os
import sys
import pytest
from fastapi.testclient import TestClient
from .server import app


@pytest.fixture
def client():
    return TestClient(app)
