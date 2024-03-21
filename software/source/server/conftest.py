import os
import sys
import pytest
from source.server.i import configure_interpreter
from unittest.mock import Mock
from interpreter import OpenInterpreter
from fastapi.testclient import TestClient
from .server import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def mock_interpreter():
    interpreter = configure_interpreter(OpenInterpreter())
    return interpreter