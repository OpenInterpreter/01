import os
import subprocess
import re
import shutil
import pyqrcode
import time
from ..utils.print_markdown import print_markdown

def create_tunnel(tunnel_method='ngrok', server_host='localhost', server_port=10001, qr=False):
    print_markdown(f"Exposing server to the internet...")

    server_url = ""
    if tunnel_method == "bore":
        try:
            output = subprocess.check_output('command -v bore', shell=True)
        except subprocess.CalledProcessError:
            print("The bore-cli command is not available. Please run 'cargo install bore-cli'.")
            print("For more information, see https://github.com/ekzhang/bore")
            exit(1)

        time.sleep(6)
        # output = subprocess.check_output(f'bore local {server_port} --to bore.pub', shell=True)
        process = subprocess.Popen(f'bore local {server_port} --to bore.pub', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        
        while True:
            line = process.stdout.readline()
            print(line)
            if not line:
                break
            if "listening at bore.pub:" in line:
                remote_port = re.search('bore.pub:([0-9]*)', line).group(1)
                server_url = f"bore.pub:{remote_port}"
                print_markdown(f"Your server is being hosted at the following URL: bore.pub:{remote_port}")
                break

    


    elif tunnel_method == "localtunnel":
        if subprocess.call('command -v lt', shell=True):
            print("The 'lt' command is not available.")
            print("Please ensure you have Node.js installed, then run 'npm install -g localtunnel'.")
            print("For more information, see https://github.com/localtunnel/localtunnel")
            exit(1)
        else:
            process = subprocess.Popen(f'npx localtunnel --port {server_port}', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)

            found_url = False
            url_pattern = re.compile(r'your url is: https://[a-zA-Z0-9.-]+')

            while True:
                line = process.stdout.readline()
                if not line:
                    break  # Break out of the loop if no more output
                match = url_pattern.search(line)
                if match:
                    found_url = True
                    remote_url = match.group(0).replace('your url is: ', '')
                    server_url = remote_url
                    print(f"\nYour server is being hosted at the following URL: {remote_url}")
                    break  # Exit the loop once the URL is found

            if not found_url:
                print("Failed to extract the localtunnel URL. Please check localtunnel's output for details.")

    elif tunnel_method == "ngrok":

        # Check if ngrok is installed
        is_installed = subprocess.check_output('command -v ngrok', shell=True).decode().strip()
        if not is_installed:
            print("The ngrok command is not available.")
            print("Please install ngrok using the instructions at https://ngrok.com/docs/getting-started/")
            exit(1)

        # If ngrok is installed, start it on the specified port
        # process = subprocess.Popen(f'ngrok http {server_port} --log=stdout', shell=True, stdout=subprocess.PIPE)
        process = subprocess.Popen(f'ngrok http {server_port} --scheme http,https --domain=marten-advanced-dragon.ngrok-free.app --log=stdout', shell=True, stdout=subprocess.PIPE)

        # Initially, no URL is found
        found_url = False
        # Regular expression to match the ngrok URL
        url_pattern = re.compile(r'https://[a-zA-Z0-9-]+\.ngrok(-free)?\.app')

        # Read the output line by line
        while True:
            line = process.stdout.readline().decode('utf-8')
            if not line:
                break  # Break out of the loop if no more output
            match = url_pattern.search(line)
            if match:
                found_url = True
                remote_url = match.group(0)
                server_url = remote_url
                print(f"\nYour server is being hosted at the following URL: {remote_url}")
                break  # Exit the loop once the URL is found
        
        if not found_url:
            print("Failed to extract the ngrok tunnel URL. Please check ngrok's output for details.")

    if server_url and qr:
        text = pyqrcode.create(remote_url)
        print(text.terminal(quiet_zone=1))

    return server_url

