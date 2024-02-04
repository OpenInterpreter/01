"""
Exposes a SSE streaming server endpoint at /run, which recieves language and code,
and streams the output.
"""

from interpreter import interpreter

for chunk in interpreter.run(language, code, stream=True):
    stream(chunk)