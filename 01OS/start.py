"""
This is just for the Python package — we need a Python entrypoint.
Just starts `start.sh` with all the same command line arguments. Aliased to 01.
"""

import os
import subprocess
import sys
import psutil
import importlib
# Can't import normally because it starts with a number
process_utils = importlib.import_module("01OS.server.utils.process_utils")
kill_process_tree = process_utils.kill_process_tree

def main():

    # Get command line arguments
    args = sys.argv[1:]

    # Get the directory of the current script
    dir_path = os.path.dirname(os.path.realpath(__file__))

    # Prepare the command
    command = [os.path.join(dir_path, 'start.sh')] + args

    try:
        # Start start.sh using psutil for better process management, and to kill all processes
        psutil.Popen(command)
    except KeyboardInterrupt:
        print("Exiting...")
        kill_process_tree()