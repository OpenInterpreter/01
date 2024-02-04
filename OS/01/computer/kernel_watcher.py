"""
Watches the kernel. When it sees something that passes a filter,
it sends POST request with that to /computer.
"""

import subprocess
import time
import requests
import platform

class Device:
    def __init__(self, device_type, device_info):
        self.device_type = device_type
        self.device_info = device_info

    def get_device_info(self):
        info = f"Device Type: {self.device_type}\n"
        for key, value in self.device_info.items():
            info += f"{key}: {value}\n"
        return info

    def __eq__(self, other):
        if isinstance(other, Device):
            return self.device_type == other.device_type and self.device_info == other.device_info
        return False


def get_connected_devices():
    """
    Get all connected devices on macOS using system_profiler
    """
    devices = []
    usb_output = subprocess.check_output(['system_profiler', 'SPUSBDataType'])
    network_output = subprocess.check_output(['system_profiler', 'SPNetworkDataType'])

    usb_lines = usb_output.decode('utf-8').split('\n')
    network_lines = network_output.decode('utf-8').split('\n')

    device_info = {}
    for line in usb_lines:
        if 'Product ID:' in line or 'Serial Number:' in line or 'Manufacturer:' in line:
            key, value = line.strip().split(':')
            device_info[key.strip()] = value.strip()
        if 'Manufacturer:' in line:
            devices.append(Device('USB', device_info))
            device_info = {}

    for line in network_lines:
        if 'Type:' in line or 'Hardware:' in line or 'BSD Device Name:' in line:
            key, value = line.strip().split(':')
            device_info[key.strip()] = value.strip()
        if 'BSD Device Name:' in line:
            devices.append(Device('Network', device_info))
            device_info = {}

    return devices


def run_kernel_watch_darwin():
    prev_connected_devices = None
    while True:
        messages_to_send = []
        connected_devices = get_connected_devices()
        if prev_connected_devices is not None:
            for device in connected_devices:
                if device not in prev_connected_devices:
                    messages_to_send.append(f'New device connected: {device.get_device_info()}')
            for device in prev_connected_devices:
                if device not in connected_devices:
                    messages_to_send.append(f'Device disconnected: {device.get_device_info()}')
        
        if messages_to_send:
            requests.post('http://localhost:8000/computer', json = {'messages': messages_to_send})
        prev_connected_devices = connected_devices

        time.sleep(2)


def get_dmesg(after):
    """
    Is this the way to do this?
    """
    messages = []
    with open('/var/log/dmesg', 'r') as file:
        lines = file.readlines()
        for line in lines:
            timestamp = float(line.split(' ')[0].strip('[]'))
            if timestamp > after:
                messages.append(line)
    return messages


def custom_filter(message):
    # Check for {TO_INTERPRETER{ message here }TO_INTERPRETER} pattern
    if '{TO_INTERPRETER{' in message and '}TO_INTERPRETER}' in message:
        start = message.find('{TO_INTERPRETER{') + len('{TO_INTERPRETER{')
        end = message.find('}TO_INTERPRETER}', start)
        return message[start:end]
    # Check for USB mention
    elif 'USB' in message:
        return message
    # Check for network related keywords
    elif any(keyword in message for keyword in ['network', 'IP', 'internet', 'LAN', 'WAN', 'router', 'switch']):
        return message
    else:
        return None


def run_kernel_watch_linux():
    last_timestamp = time.time()

    while True:
        messages = get_dmesg(after=last_timestamp)
        last_timestamp = time.time()
        
        messages_for_core = []
        for message in messages:
            if custom_filter(message):
                messages_for_core.append(message)
        if messages_for_core:
            requests.post('http://localhost:8000/computer', json = {'messages': messages_for_core})

        time.sleep(2)


if __name__ == "__main__":
    current_platform = platform.system()
    if current_platform == "Darwin":
        run_kernel_watch_darwin()
    elif current_platform == "Linux":
        run_kernel_watch_linux()
    else:
        print("Unsupported platform. Exiting.")
