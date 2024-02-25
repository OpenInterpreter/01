# ○

Official pre-release repository for [The 01 Project](https://twitter.com/hellokillian/status/1745875973583896950).

> **11** days remaining until launch

<br>

### [View task list ↗](https://github.com/KillianLucas/01/blob/main/TASKS.md)

<br>

## Install dependencies:

```bash
# MacOS
brew install portaudio ffmpeg cmake

# Ubuntu
sudo apt-get install portaudio19-dev ffmpeg cmake
```

If you want to run local speech-to-text using Whisper, install Rust. Follow the instructions given [here](https://www.rust-lang.org/tools/install).

## Setup for usage (experimental):

```bash
pip install 01OS
```

**Run the 01 end-to-end:**

```bash
01 # This will run a server + attempt to determine and run a client.
# (Behavior can be modified by changing the contents of `.env`)
```

**Expose an 01 Server Publicly**

We currently support exposing the 01 server publicly via a couple of different tunnel services:

- **bore.pub** ([GitHub](https://github.com/ekzhang/bore))
  - **Requirements:** Ensure that Rust is installed ([Rust Installation](https://www.rust-lang.org/tools/install)), then run:
    ```
    cargo install bore-cli
    ```
  - **To Expose:**
    ```bash
    01 --server --expose-with-bore
    ```

- **localtunnel** ([GitHub](https://github.com/localtunnel/localtunnel))
  - **Requirements:** Ensure that Node.js is installed ([Node.js Download](https://nodejs.org/en/download)), then run:
    ```
    npm install -g localtunnel
    ```
  - **To Expose:**
    ```bash
    01 --server --expose-with-localtunnel
    ```

- **ngrok** ([Website](https://ngrok.com/))
  - **Requirements:** Install ngrok ([Getting Started with ngrok](https://ngrok.com/docs/getting-started/)), and set up an ngrok account. Get your auth key from [ngrok dashboard](https://dashboard.ngrok.com/get-started/your-authtoken), then set it in your local configuration by running:
    ```
    ngrok config add-authtoken your_auth_token_here
    ```
  - **To Expose:**
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
01 --local --server --expose-with-bore  # Expose the local server with a public tunnel
```

**Teach Mode (experimental)**

Running `01 --teach` runs 01 in teach mode, where you can add your own skills for Open Interpreter to use, through an easy-to-follow GUI.

<br>

## Setup for development:

```bash
# Clone the repo, cd into the 01OS directory
git clone https://github.com/KillianLucas/01.git
cd 01OS

# Install dependencies, run the commands above
poetry install
poetry run 01
```

**Configuration:**

Copy the `01OS/.env.example` file to `01OS/.env` then configure the environment variables within the file.

<br>

## Background

### [Context ↗](https://github.com/KillianLucas/01/blob/main/CONTEXT.md)

The story of devices that came before the 01.

### [Inspiration ↗](https://github.com/KillianLucas/01/tree/main/INSPIRATION.md)

Things we want to steal great ideas from.

<br>

## Direction

### [Goals ↗](https://github.com/KillianLucas/01/blob/main/GOALS.md)

What we're going to do.

### [Use Cases ↗](https://github.com/KillianLucas/01/blob/main/USE_CASES.md)

What the 01 will be able to do.

<br>
