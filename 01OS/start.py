"""
This is just for the Python package — we need a Python entrypoint.
Just starts `start.sh` with all the same command line arguments. Aliased to 01.
"""

import os
import subprocess
import sys

def main():

    # Get command line arguments
    args = sys.argv[1:]

    # Get the directory of the current script
    dir_path = os.path.dirname(os.path.realpath(__file__))

    # Prepare the command
    command = [os.path.join(dir_path, 'start.sh')] + args

    # Start start.sh with the command line arguments
    try:
        subprocess.run(command, check=True)
    except KeyboardInterrupt:
        print("Exiting...")
    