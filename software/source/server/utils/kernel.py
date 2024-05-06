from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.

import asyncio
import subprocess
import platform
import os
import shutil

from .logs import setup_logging
from .logs import logger

setup_logging()

# dmesg process created at boot time
dmesg_proc = None


def get_kernel_messages():
    """
    Is this the way to do this?
    """
    current_platform = platform.system()

    if current_platform == "Darwin":
        process = subprocess.Popen(
            ["syslog"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL
        )
        output, _ = process.communicate()
        return output.decode("utf-8")
    elif current_platform == "Linux":
        log_path = get_dmesg_log_path()
        with open(log_path, 'r') as file:
            return file.read()
    else:
        logger.info("Unsupported platform.")


def get_dmesg_log_path():
    """
    Check for the existence of a readable dmesg log file and return its path.
    Create an accessible path if not found.
    """
    if os.access('/var/log/dmesg', os.F_OK | os.R_OK):
        return '/var/log/dmesg'

    global dmesg_proc
    dmesg_log_path = '/tmp/dmesg'
    if dmesg_proc:
        return dmesg_log_path

    logger.info("Created /tmp/dmesg.")
    subprocess.run(['touch', dmesg_log_path])
    dmesg_path = shutil.which('dmesg')
    if dmesg_path:
        logger.info(f"Writing to {dmesg_log_path} from dmesg.")
        dmesg_proc = subprocess.Popen([dmesg_path, '--follow'], text=True, stdout=subprocess.PIPE)
        subprocess.Popen(['tee', dmesg_log_path], text=True, stdin=dmesg_proc.stdout, stdout=subprocess.DEVNULL)
    
    return dmesg_log_path


def custom_filter(message):
    # Check for {TO_INTERPRETER{ message here }TO_INTERPRETER} pattern
    if "{TO_INTERPRETER{" in message and "}TO_INTERPRETER}" in message:
        start = message.find("{TO_INTERPRETER{") + len("{TO_INTERPRETER{")
        end = message.find("}TO_INTERPRETER}", start)
        return message[start:end]
    # Check for USB mention
    # elif 'USB' in message:
    #     return message
    # # Check for network related keywords
    # elif any(keyword in message for keyword in ['network', 'IP', 'internet', 'LAN', 'WAN', 'router', 'switch']) and "networkStatusForFlags" not in message:

    #     return message
    else:
        return None


last_messages = ""


def check_filtered_kernel():
    messages = get_kernel_messages()
    if messages is None:
        return ""  # Handle unsupported platform or error in fetching kernel messages

    global last_messages
    messages.replace(last_messages, "")
    messages = messages.split("\n")

    filtered_messages = []
    for message in messages:
        if custom_filter(message):
            filtered_messages.append(message)

    return "\n".join(filtered_messages)


async def put_kernel_messages_into_queue(queue):
    while True:
        text = check_filtered_kernel()
        if text:
            if isinstance(queue, asyncio.Queue):
                await queue.put({"role": "computer", "type": "console", "start": True})
                await queue.put(
                    {
                        "role": "computer",
                        "type": "console",
                        "format": "output",
                        "content": text,
                    }
                )
                await queue.put({"role": "computer", "type": "console", "end": True})
            else:
                queue.put({"role": "computer", "type": "console", "start": True})
                queue.put(
                    {
                        "role": "computer",
                        "type": "console",
                        "format": "output",
                        "content": text,
                    }
                )
                queue.put({"role": "computer", "type": "console", "end": True})

        await asyncio.sleep(5)
