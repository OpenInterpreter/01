# test_main.py
import pytest


import subprocess
import time

def test_poetry_run_01():
    process = subprocess.Popen(['poetry', 'run', '01'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    timeout = time.time() + 30  # 30 seconds from now

    while True:
        output = process.stdout.readline().decode('utf-8')
        if "Hold" in output:
            assert True
            return
        if time.time() > timeout:
            assert False, "Timeout reached without finding expected output."
            return

# @pytest.mark.skip(reason="pytest hanging")
# def test_ping(client):
#     response = client.get("/ping")
#     assert response.status_code == 200
#     assert response.text == "pong"


# def test_interpreter_chat(mock_interpreter):
#     # Set up a sample conversation
#     messages = [
#         {"role": "user", "type": "message", "content": "Hello."},
#         {"role": "assistant", "type": "message", "content": "Hi there!"},
#         # Add more messages as needed
#     ]

#     # Configure the mock interpreter with the sample conversation
#     mock_interpreter.messages = messages

#     # Simulate additional user input
#     user_input = {"role": "user", "type": "message", "content": "How are you?"}
#     mock_interpreter.chat([user_input])

#     # Ensure the interpreter processed the user input
#     assert len(mock_interpreter.messages) == len(messages)
#     assert mock_interpreter.messages[-1]["role"] == "assistant"
#     assert "don't have feelings" in mock_interpreter.messages[-1]["content"]

# def test_interpreter_configuration(mock_interpreter):
#     # Test interpreter configuration
#     interpreter = configure_interpreter(mock_interpreter)
#     assert interpreter is not None
