import os
import platform


def get_system_info():
    system = platform.system()
    
    if system == "Linux":
        # Attempt to identify specific Linux distribution
        distro = "linux"  # Default to generic 'linux'
        try:
            with open("/etc/os-release") as f:
                os_release_info = f.read().lower()
            if "ubuntu" in os_release_info:
                return "raspberry-pi-ubuntu"
            elif "raspbian" in os_release_info:
                return "raspberry-pi-os"
        except FileNotFoundError:
            pass
        
        # Check for Raspberry Pi hardware
        try:
            with open("/proc/device-tree/model") as f:
                model_info = f.read()
            if "Raspberry Pi" in model_info:
                if distro == "ubuntu":
                    return "raspberry-pi-ubuntu"
                return "raspberry-pi"
        except FileNotFoundError:
            pass
        
        return distro
    elif system == "Darwin":
        return "darwin"
    elif system == "Windows":
        return "windows"
    else:
        return "unknown"
