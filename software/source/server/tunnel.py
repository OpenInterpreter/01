import ngrok
import pyqrcode
from ..utils.print_markdown import print_markdown

def create_tunnel(
    server_host="localhost", server_port=10001, qr=False, domain=None
):  
    """
    To use most of ngrok’s features, you’ll need an authtoken. To obtain one, sign up for free at ngrok.com and 
    retrieve it from the authtoken page in your ngrok dashboard. 

    https://dashboard.ngrok.com/get-started/your-authtoken

    You can set it as `NGROK_AUTHTOKEN` in your environment variables
    """
    print_markdown("Exposing server to the internet...")

    if domain:
        listener = ngrok.forward(f"{server_host}:{server_port}", authtoken_from_env=True, domain=domain)
    else:
        listener = ngrok.forward(f"{server_host}:{server_port}", authtoken_from_env=True)

    listener_url = listener.url()

    print(f"Ingress established at: {listener_url}");
    if listener_url and qr:
        text = pyqrcode.create(listener_url)
        print(text.terminal(quiet_zone=1))

    return listener_url
