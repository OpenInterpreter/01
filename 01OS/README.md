The open-source language model computer.

```bash
pip install 01OS
```

```bash
01 # This will run a server + attempt to determine and run a client.
# (Behavior can be modified by changing the contents of `.env`)
```

**Expose an 01 server publically:**

```bash
01 --server --expose # This will print a URL that a client can point to.
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
01 --local --server --expose # Expose a local server
```
