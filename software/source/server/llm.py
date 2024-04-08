from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.

import os
import subprocess
from pathlib import Path

### LLM SETUP

# Define the path to a llamafile
llamafile_path = Path(__file__).parent / "model.llamafile"

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

# Run the new llamafile
subprocess.run([str(llamafile_path)], check=True)
