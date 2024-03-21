Official pre-release repository for [The 01 Project](https://twitter.com/hellokillian/status/1745875973583896950).

> **1** day remaining until launch

<br>
<br>

<h1 align="center">○</h1>

<p align="center">
    <a href="https://discord.gg/Hvz9Axh84z"><img alt="Discord" src="https://img.shields.io/discord/1146610656779440188?logo=discord&style=social&logoColor=black"/></a>
    <br>
    <br>
    <strong>The open-source language model computer.</strong><br>
    <!-- <br><a href="https://openinterpreter.com">Preorder the Light</a>‎ ‎ |‎ ‎ <a href="https://openinterpreter.com">Get Updates</a>‎ ‎ |‎ ‎ <a href="https://docs.openinterpreter.com/">Documentation</a><br> -->
</p>

<br>

![OI-O1-BannerDemo-2](https://github.com/OpenInterpreter/01/assets/63927363/fb80e880-9ae7-489c-b495-035be4d56414)

We want to help you build. [Apply for 1-on-1 support.](https://0ggfznkwh4j.typeform.com/to/kkStE8WF)

<br>

---

⚠️ **WARNING:** This experimental project is under rapid development and lacks basic safeguards. Until a stable `1.0` release, **ONLY** run this repository on devices without sensitive information or access to paid services. ⚠️

---

<br>

**The 01 Project** is building an open-source ecosystem for AI devices.

Our flagship operating system can power conversational devices like the Rabbit R1, Humane Pin, or [Star Trek computer](https://www.youtube.com/watch?v=1ZXugicgn6U).

We intend to become the GNU/Linux of this space by staying open, modular, and free.

<br>

# Software

```shell
git clone https://github.com/OpenInterpreter/01 # Clone the repository
cd software/source # CD into the source directory
```

> Not working? Read our [setup guide](https://docs.openinterpreter.com/getting-started/setup).

```shell
brew install portaudio ffmpeg cmake # Install Mac OSX dependencies
poetry install # Install Python dependencies
export OPENAI_API_KEY=sk... # OR run `poetry run 01 --local` to run everything locally
poetry run 01 # Runs the 01 Light simulator (hold your spacebar, speak, release)
```

<br>

# Hardware

- The **01 Light** is an ESP32-based voice interface. Build instructions are here. It works in tandem with the **01 Server** running on your home computer.
- **Mac OSX** and **Ubuntu** are supported by running `poetry run 01`. This uses your spacebar to simulate the 01 Light.
- The **01 Heavy** is a standalone device that runs everything locally.

**We need your help supporting & building more hardware.** The 01 should be able to run on any device with input (microphone, keyboard, etc.), output (speakers, screens, motors, etc.), and an internet connection (or sufficient compute to run everything locally). <br> [Contribution Guide →](https://github.com/OpenInterpreter/01/blob/main/CONTRIBUTING.md)

<br>

# How does it work?

The 01 exposes a speech-to-speech websocket at `localhost:10001`.

If you stream raw audio bytes to `/` in [LMC format](https://docs.openinterpreter.com/protocols/lmc-messages), you will recieve its response in the same format.

Inspired in part by [Andrej Karpathy's LLM OS](https://twitter.com/karpathy/status/1723140519554105733), we point a [code-interpreting language model](https://github.com/OpenInterpreter/open-interpreter) at your computer's [kernel](https://github.com/OpenInterpreter/01/blob/main/01OS/01OS/server/utils/kernel.py), forming a **l**anguage **m**odel **c**omputer (LMC).

<br>

<img width="100%" alt="LMC" src="https://github.com/OpenInterpreter/01/assets/63927363/52417006-a2ca-4379-b309-ffee3509f5d4"><br><br>

This architecture fuses **classical computers**— precise, powerful machines— with **language models**— imprecise, intelligent machines.

We believe the 01 inherits the best of both, unifying the power and connectivity of classical computers with the natural, human-like usability of language models.

---
---
---

# Protocols

### LMC Messages

### Dynamic System Messages



The 01OS 

The 01OS can be housed in many different bodies. We highly encourage PRs that add to this list:

The **01 Light** is an ESP32-based voice interface that controls your home computer over the internet. It's used in combination with the **01 Server**.

The **01 Heavy** is a device that runs everything locally.

# Software

### Install dependencies

```bash
# MacOS
brew install portaudio ffmpeg cmake

# Ubuntu
sudo apt-get install portaudio19-dev ffmpeg cmake
```

If you want to run local speech-to-text using Whisper, install Rust. Follow the instructions given [here](https://www.rust-lang.org/tools/install).

### Install and run the 01 CLI

```shell
pip install 01OS
```

```shell
01 --server # Start a server for a hardware device to listen to.
```

# Client Setup

### For ESP32 boards

Please visit our [ESP32 setup documentation](https://github.com/OpenInterpreter/01/tree/main/01OS/01OS/clients/esp32).

### For Mac, Windows, and Ubuntu machines

```
01 # Start a server and a client.

01 --server --expose # Start and expose a server via Ngrok. This will print a `server_url` for clients to connect to.

01 --client --server_url your-server.com # Start only a client.
```

### Swap out service providers

The 01 is model agnostic to speech-to-text, text-to-speech, and language model providers.

Select your provider by running:

```shell
01 --tts-service openai
01 --llm-service openai
01 --stt-service openai
```

[View all providers ↗](https://docs.litellm.ai/docs/providers/), or [join the 01 team by adding a service provider. ↗]()

### Run the 01 locally

Some service providers don't require an internet connection.

The following command will attempt to download and use the best providers for your hardware:

```shell
01 --local
```

## How Does it Work?

The 01 equips a language model (wrapped in a voice interface) with an `exec()` function, which allows it to write and run code to control computers.

We only stream speech to/from the end user's device.

# Contributing

Please see our [contributing guidelines](docs/CONTRIBUTING.md) for more details on how to get involved.

### Setup for development

```bash
# Clone the repo
git clone https://github.com/KillianLucas/01.git

# Go to the 01OS directory
cd 01OS

# Install python dependencies
poetry install

# Run it
poetry run 01
```

<br>

# Roadmap

Visit [our roadmap](https://github.com/KillianLucas/open-interpreter/blob/main/docs/ROADMAP.md) to see the future of the 01.

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
