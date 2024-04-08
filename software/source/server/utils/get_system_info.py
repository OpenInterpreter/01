import platform


def get_system_info():
    system = platform.system()
    if system == "Linux":
        # Attempt to identify specific Linux distribution
        distro = "linux"  # Default to generic 'linux'
        try:
            with open("/etc/os-release") as f:
                os_release_info = f.read().lower()
                if "raspbian" in os_release_info:
                    distro = "raspberry-pi-os"
                elif "ubuntu" in os_release_info:
                    distro = "ubuntu"
        except FileNotFoundError:
            pass

        # Check for Raspberry Pi hardware
        is_raspberry_pi = False
        try:
            with open("/proc/device-tree/model") as f:
                model_info = f.read()
                if "Raspberry Pi" in model_info:
                    is_raspberry_pi = True
        except FileNotFoundError:
            pass

        if is_raspberry_pi:
            if distro == "ubuntu":
                return "raspberry-pi-ubuntu"
            else:
                return "raspberry-pi"
        else:
            return distro
    elif system == "Darwin":
        return "darwin"
    elif system == "Windows":
        return "windows"
    else:
        return "unknown"
