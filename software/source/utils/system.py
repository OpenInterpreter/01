"""
System utility functions
"""

import os


def handle_exit(signum, frame) -> None:  # pylint: disable=unused-argument
    """
    Handle exit signal.
    """
    os._exit(0)
