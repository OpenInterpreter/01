import os
import psutil
import signal


def kill_process_tree():
    pid = os.getpid()  # Get the current process ID
    try:
        # Send SIGTERM to the entire process group to ensure all processes are targeted
        try:
            os.killpg(os.getpgid(pid), signal.SIGKILL)
        # Windows implementation
        except AttributeError:
            os.kill(pid, signal.SIGTERM)
        parent = psutil.Process(pid)
        children = parent.children(recursive=True)
        for child in children:
            print(f"Forcefully terminating child PID {child.pid}")
            child.kill()  # Forcefully kill the child process immediately
        gone, still_alive = psutil.wait_procs(children, timeout=3)

        if still_alive:
            for child in still_alive:
                print(f"Child PID {child.pid} still alive, attempting another kill")
                child.kill()

        print(f"Forcefully terminating parent PID {pid}")
        parent.kill()  # Forcefully kill the parent process immediately
        parent.wait(3)  # Wait for the parent process to terminate
    except psutil.NoSuchProcess:
        print(f"Process {pid} does not exist or is already terminated")
    except psutil.AccessDenied:
        print("Permission denied to terminate some processes")
