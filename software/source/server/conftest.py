import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock

# Assuming your project structure includes these modules
from source.server.server import app  # Adjusted import to reflect typical project structure
from source.server.interpreter import OpenInterpreter, configure_interpreter

@pytest.fixture(scope="module")
def client():
    """
    Pytest fixture to create a test client for the FastAPI app.
    This client can be used to make requests to the API and
    assert the responses.

    Using 'scope="module"' to instantiate the client once per test module,
    which can improve test performance.
    """
    return TestClient(app)

@pytest.fixture(scope="function")
def mock_interpreter():
    """
    Pytest fixture to create a mocked interpreter.
    This mock can be used to replace the actual interpreter in tests,
    allowing for isolated testing of components that depend on the interpreter.

    Using 'scope="function"' to ensure a fresh mock for each test function,
    which helps prevent side effects between tests.
    """
    # Using MagicMock to mock the OpenInterpreter instance for more complex mocking scenarios.
    interpreter = configure_interpreter(MagicMock(spec=OpenInterpreter))
    return interpreter
