# tests currently hang after completion

"""
import pytest
import signal
import os
from .profiles.default import interpreter
from async_interpreter import AsyncInterpreter
from fastapi.testclient import TestClient
from .async_server import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def mock_interpreter():
    async_interpreter = AsyncInterpreter(interpreter)
    yield async_interpreter
    async_interpreter.shutdown()


@pytest.fixture(scope="function", autouse=True)
def term_handler():

    orig = signal.signal(signal.SIGTERM, signal.getsignal(signal.SIGINT))
    yield
    signal.signal(signal.SIGTERM, orig)


    yield
    # Send SIGTERM signal to the current process and its children
    os.kill(os.getpid(), signal.SIGTERM)
"""
