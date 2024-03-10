# test_main.py
import subprocess
import uuid
import pytest
from fastapi.testclient import TestClient



@pytest.mark.asyncio
def test_ping(client):
    response = client.get("/ping")
    assert response.status_code == 200
    assert response.text == "pong"
