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

**We need your help supporting & building more hardware.** The 01 should be able to run on any device with input (microphone, keyboard, etc.), output (speakers, screens, motors, etc.), and an internet connection (or sufficient compute to run everything locally). [Contribution Guide →](https://github.com/OpenInterpreter/01/blob/main/CONTRIBUTING.md)

<br>

# How does it work?

The 01 exposes a speech-to-speech websocket at `localhost:10001`.

If you stream raw audio bytes to `/` in [LMC format](https://docs.openinterpreter.com/protocols/lmc-messages), you will recieve its response in the same format.

Inspired in part by [Andrej Karpathy's LLM OS](https://twitter.com/karpathy/status/1723140519554105733), we point a [code-interpreting language model](https://github.com/OpenInterpreter/open-interpreter) at your computer's [kernel](https://github.com/OpenInterpreter/01/blob/main/01OS/01OS/server/utils/kernel.py), forming a **l**anguage **m**odel **c**omputer (LMC).

<br>

<img width="100%" alt="LMC" src="https://github.com/OpenInterpreter/01/assets/63927363/52417006-a2ca-4379-b309-ffee3509f5d4"><br><br>

This architecture fuses **classical computers**— precise, powerful machines— with **language models**— imprecise, intelligent machines.

We believe the 01 inherits the best of both, unifying the power and connectivity of classical computers with the natural, human-like usability of language models.

# Protocols

### LMC Messages

To communicate with different componnents of this system, we introduced [LMC Messages](https://docs.openinterpreter.com/protocols/lmc-messages) format, which extends OpenAI’s messages format to include the "computer" role, and a few more minor improvemets.

### Dynamic System Messages

Dynamic System Messages enable you to execute code inside the LLM's system message, moments before the "rendered" system message (which now includes the outputs of your code) is sent to the language model.

```python
interpreter.system_message = r" The time is {{time.time()}}. "
interpreter.chat("What time is it?") # It will know, without making a tool/API call
```

### Guides

# Local Mode

```
poetry run 01 --local
```

If you want to run local speech-to-text using Whisper, you must install Rust. Follow the instructions given [here](https://www.rust-lang.org/tools/install).

# Ubuntu Dependencies

```bash
sudo apt-get install portaudio19-dev ffmpeg cmake
```

# Contributing

Please see our [contributing guidelines](docs/CONTRIBUTING.md) for more details on how to get involved.

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

○
