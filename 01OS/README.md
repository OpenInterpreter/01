The open-source language model computer.

```bash
pip install 01OS
```

```bash
01 # This will run a server + attempt to determine and run a client.
# (Behavior can be modified by changing the contents of `.env`)
```

**Expose an 01 server publically:**

We currently support exposing the 01 server publicly via a couple of different tunnel services:

- bore.pub (https://github.com/ekzhang/bore)
  Requirements: Ensure that rust is installed (https://www.rust-lang.org/tools/install), then run `cargo install bore-cli`

    ```bash
    01 --server --expose-with-bore
    ```

- localtunnel (https://github.com/localtunnel/localtunnel)
  Requirements: Ensure that Node is installed (https://nodejs.org/en/download), then run `npm install -g localtunnel`

    ```bash
    01 --server --expose-with-localtunnel
    ```

- ngrok (https://ngrok.com/)
  Requirements: Install ngrok (https://ngrok.com/docs/getting-started/), and set up an ngrok account.
  Get your auth key from https://dashboard.ngrok.com/get-started/your-authtoken, then set it in
  your local configuration by running `ngrok config add-authtoken your_auth_token_here`
    
    ```bash
    01 --server --expose-with-ngrok
    ```


**Run a specific client:**

```bash
01 --client macos # Options: macos, rpi
```

**Run locally:**

The current default uses OpenAI's services.

The `--local` flag will install and run the [whisper.cpp](https://github.com/ggerganov/whisper.cpp) STT and [Piper](https://github.com/rhasspy/piper) TTS models.

```bash
01 --local # Local client and server
01 --local --server --expose-with-bore # Expose a local server
```
