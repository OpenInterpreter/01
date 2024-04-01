import subprocess
import sys
import ctypes
import os


def main():
    """Run pytest in the software directory.

    This script is intended to be used as a pre-commit hook to run the tests from the root of the repository.
    """

    # Additional setup for Windows (10 at least) to prevent issues with Unicode characters in the console.
    # see https://www.reddit.com/r/learnpython/comments/350c8c/unicode_python_3_and_the_windows_console/
    if sys.platform.startswith("win"):
        # Force UTF-8 encoding in Python
        os.environ["PYTHONUTF8"] = "1"

        # Change Windows console code page to UTF-8
        ctypes.windll.kernel32.SetConsoleCP(65001)
        ctypes.windll.kernel32.SetConsoleOutputCP(65001)

    # Define the target directory relative to this script location.
    target_directory = os.path.join(os.path.dirname(__file__), "software")

    os.chdir(target_directory)

    # Run pytest with any additional arguments passed to this script.
    result = subprocess.run(["pytest"] + sys.argv[1:])

    # Exit with pytest's exit code to reflect the test outcome in the pre-commit hook.
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
