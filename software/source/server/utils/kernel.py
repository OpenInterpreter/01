import asyncio
import subprocess
import platform
from dotenv import load_dotenv
from .logs import setup_logging, logger

load_dotenv()  # take environment variables from .env.
setup_logging()

class KernelChecker:
    def __init__(self):
        self._last_messages = ""

    def get_kernel_messages(self):
        """
        Fetch system logs or kernel message from the operating system.

        - For MacOS, it uses syslog.
        - For Linux, it uses dmesg.
        - For Windows, it uses wevtutil with the 'qe' (query events) from the 'System' log
          with the '/f:text' (format text) flag.
        """
        current_platform = platform.system().lower()

        if current_platform == "darwin":
            process = subprocess.Popen(['syslog'], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
            output, _ = process.communicate()
            return output.decode('utf-8')
        elif current_platform == "linux":
            with open('/var/log/dmesg', 'r') as file:
                return file.read()
        elif current_platform == "windows":
            process = subprocess.Popen(['wevtutil', 'qe', 'System', '/f:text'], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
            output, _ = process.communicate()
            try:
                return output.decode('utf-8')
            except UnicodeDecodeError:
                try:
                    return output.decode('utf-16')
                except UnicodeDecodeError:
                    return output.decode('cp1252')
        else:
            logger.info("Unsupported platform.")
            return ""

    def custom_filter(self, message):
        if '{TO_INTERPRETER{' in message and '}TO_INTERPRETER}' in message:
            start = message.find('{TO_INTERPRETER{') + len('{TO_INTERPRETER{')
            end = message.find('}TO_INTERPRETER}', start)
            return message[start:end]
        else:
            return None

    def check_filtered_kernel(self):
        try:
            messages = self.get_kernel_messages()
            messages = messages.replace(self._last_messages, "")
            messages = messages.split("\n")

            filtered_messages = [message for message in messages if self.custom_filter(message)]

            self._last_messages = "\n".join(filtered_messages)
            return self._last_messages
        except Exception as e:
            logger.error(f"Error while checking kernel messages: {e}")
            return None


async def put_kernel_messages_into_queue(kernel_checker, queue):
    while True:
        text = kernel_checker.check_filtered_kernel()
        if text:
            if isinstance(queue, asyncio.Queue):
                await queue.put({"role": "computer", "type": "console", "start": True})
                await queue.put({"role": "computer", "type": "console", "format": "output", "content": text})
                await queue.put({"role": "computer", "type": "console", "end": True})
            else:
                queue.put({"role": "computer", "type": "console", "start": True})
                queue.put({"role": "computer", "type": "console", "format": "output", "content": text})
                queue.put({"role": "computer", "type": "console", "end": True})

        await asyncio.sleep(5)
