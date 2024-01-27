"""
Responsible for setting up the language model, downloading it if necessary.

Ideally should pick the best LLM for the hardware.

Should this be a shell script?
"""

import os
import subprocess


### LLM SETUP

# Define the path to the models directory
models_dir = "models/"

# Check and create the models directory if it doesn't exist
if not os.path.exists(models_dir):
    os.makedirs(models_dir)

# Define the path to a llamafile
llamafile_path = os.path.join(models_dir, "phi-2.Q4_K_M.llamafile")

# Check if the new llamafile exists, if not download it
if not os.path.exists(llamafile_path):
    subprocess.run(
        [
            "wget",
            "-O",
            llamafile_path,
            "https://huggingface.co/jartine/phi-2-llamafile/resolve/main/phi-2.Q4_K_M.llamafile",
        ],
        check=True,
    )
    # Make the new llamafile executable
    subprocess.run(["chmod", "+x", llamafile_path], check=True)

# Run the new llamafile in the background
subprocess.Popen([llamafile_path])