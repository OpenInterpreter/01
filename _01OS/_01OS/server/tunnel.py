import os
import subprocess
import re
import shutil
import time
from ..utils.print_markdown import print_markdown

def create_tunnel(tunnel_method='bore', server_host='localhost', server_port=8000):
    print_markdown(f"Exposing server to the internet...")

    if tunnel_method == "bore":
        try:
            output = subprocess.check_output('command -v bore', shell=True)
        except subprocess.CalledProcessError:
            print("The bore-cli command is not available. Please run 'cargo install bore-cli'.")
            print("For more information, see https://github.com/ekzhang/bore")
            exit(1)

        time.sleep(6)
        output = subprocess.check_output(f'bore local {server_port} --to bore.pub', shell=True)
        
        for line in output.split('\n'):
            if "listening at bore.pub:" in line:
                remote_port = re.search('bore.pub:([0-9]*)', line).group(1)
                print_markdown(f"Your server is being hosted at the following URL: bore.pub:{remote_port}")
                break

    
            

    elif tunnel_method == "localtunnel":
        if not subprocess.call('command -v lt', shell=True):
            print("The 'lt' command is not available.")
            print("Please ensure you have Node.js installed, then run 'npm install -g localtunnel'.")
            print("For more information, see https://github.com/localtunnel/localtunnel")
            exit(1)
        else:
            output = subprocess.check_output(f'npx localtunnel --port {server_port}', shell=True)
            for line in output.split('\n'):
                if "your url is: https://" in line:
                    remote_url = re.search('https://([a-zA-Z0-9.-]*)', line).group(0).replace('https://', '')
                    print(f"Your server is being hosted at the following URL: {remote_url}")
                    break

    elif tunnel_method == "ngrok":
        if not subprocess.call('command -v ngrok', shell=True):
            print("The ngrok command is not available.")
            print("Please install ngrok using the instructions at https://ngrok.com/docs/getting-started/")
            exit(1)
        else:
            output = subprocess.check_output(f'ngrok http {server_port} --log stdout', shell=True)
            for line in output.split('\n'):
                if "started tunnel" in line:
                    remote_url = re.search('https://([a-zA-Z0-9.-]*)', line).group(0).replace('https://', '')
                    print(f"Your server is being hosted at the following URL: {remote_url}")
                    break

