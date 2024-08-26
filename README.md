<h1 align="center">○</h1>

<p align="center">
    <a href="https://discord.gg/Hvz9Axh84z"><img alt="Discord" src="https://img.shields.io/discord/1146610656779440188?logo=discord&style=social&logoColor=black"/></a>
    <br>
    <br>
    <strong>The #1 open-source voice interface.</strong><br>
    <br><a href="https://changes.openinterpreter.com">Get Updates</a>‎ ‎ |‎ ‎ <a href="https://01.openinterpreter.com/">Documentation</a><br>
</p>

<div align="center">


 | [中文版](docs/README_CN.md) | [日本語](docs/README_JA.md) | [English](README.md) |


</div>

<br>

![OI-O1-BannerDemo-2](https://www.openinterpreter.com/OI-O1-BannerDemo-3.jpg)

We want to help you build. [Apply for 1-on-1 support.](https://0ggfznkwh4j.typeform.com/to/kkStE8WF)

<br>

> [!IMPORTANT]
> This experimental project is under rapid development and lacks basic safeguards. Until a stable `1.0` release, only run this repository on devices without sensitive information or access to paid services.

<br>

The **01** is an open-source platform for conversational devices, inspired by the *Star Trek* computer.

With [Open Interpreter](https://github.com/OpenInterpreter/open-interpreter) at its core, the **01** is more natural, flexible, and capable than its predecessors. Assistants built on **01** can:

- Execute code
- Browse the web
- Read and create files
- Control third-party software
- ...

<br>

We intend to become the GNU/Linux of this space by staying open, modular, and free.

<br>

# Software

```shell
git clone https://github.com/OpenInterpreter/01 # Clone the repository
cd 01/software # CD into the source directory
```

<!-- > Not working? Read our [setup guide](https://docs.openinterpreter.com/getting-started/setup). -->

```shell
brew install portaudio ffmpeg cmake # Install Mac OSX dependencies
poetry install # Install Python dependencies
export OPENAI_API_KEY=sk... # OR run `poetry run 01 --local` to run everything locally
poetry run 01 # Runs the 01 Light simulator (hold your spacebar, speak, release)
```

<!-- > For a Windows installation, read our [setup guide](https://docs.openinterpreter.com/getting-started/setup#windows). -->

<br>

**Note:** The [RealtimeTTS](https://github.com/KoljaB/RealtimeTTS) and [RealtimeSTT](https://github.com/KoljaB/RealtimeSTT) libraries at the heart of the 01 are thanks to the voice interface work of [Kolja Beigel](https://github.com/KoljaB). Please star those repos and consider contributing to / utilizing those projects.

# Hardware

- The **01 Light** is an ESP32-based voice interface. Build instructions are [here](https://github.com/OpenInterpreter/01/tree/main/hardware/light). A list of what to buy [here](https://github.com/OpenInterpreter/01/blob/main/hardware/light/BOM.md).
- It works in tandem with the **01 Server** ([setup guide below](https://github.com/OpenInterpreter/01/blob/main/README.md#01-server)) running on your home computer.
- **Mac OSX** and **Ubuntu** are supported by running `poetry run 01` (**Windows** is supported experimentally). This uses your spacebar to simulate the 01 Light.

**We need your help supporting & building more hardware.** The 01 should be able to run on any device with input (microphone, keyboard, etc.), output (speakers, screens, motors, etc.), and an internet connection (or sufficient compute to run everything locally). [Contribution Guide →](https://github.com/OpenInterpreter/01/blob/main/CONTRIBUTING.md)

<br>

# What does it do?

The 01 exposes a speech-to-speech websocket at `localhost:10101`.

If you stream raw audio bytes to `/` in [Streaming LMC format](https://docs.openinterpreter.com/guides/streaming-response), you will receive its response in the same format.

Inspired in part by [Andrej Karpathy's LLM OS](https://twitter.com/karpathy/status/1723140519554105733), we run a [code-interpreting language model](https://github.com/OpenInterpreter/open-interpreter), and call it when certain events occur at your computer's [kernel](https://github.com/OpenInterpreter/01/blob/main/software/source/server/utils/kernel.py).

The 01 wraps this in a voice interface:

<br>

<img width="100%" alt="LMC" src="https://github.com/OpenInterpreter/01/assets/63927363/52417006-a2ca-4379-b309-ffee3509f5d4"><br><br>

# Protocols

## LMC Messages

To communicate with different components of this system, we introduce [LMC Messages](https://docs.openinterpreter.com/protocols/lmc-messages) format, which extends OpenAI’s messages format to include a "computer" role:

https://github.com/OpenInterpreter/01/assets/63927363/8621b075-e052-46ba-8d2e-d64b9f2a5da9

## Dynamic System Messages

Dynamic System Messages enable you to execute code inside the LLM's system message, moments before it appears to the AI.

```python
# Edit the following settings in Profiles
interpreter.system_message = r" The time is {{time.time()}}. " # Anything in double brackets will be executed as Python
interpreter.chat("What time is it?") # It will know, without making a tool/API call
```

# Guides

## 01 Server

To run the server on your Desktop and connect it to your 01 Light, run the following commands:

```shell
brew install ngrok/ngrok/ngrok
ngrok authtoken ... # Use your ngrok authtoken
poetry run 01 --server light --expose
```

The final command will print a server URL. You can enter this into your 01 Light's captive WiFi portal to connect to your 01 Server.

## Local Mode

```
poetry run 01 --profile local.py
```

## Customizations

To customize the behavior of the system, edit the [system message, model, skills library path,](https://docs.openinterpreter.com/settings/all-settings) etc. in the `profiles` directory under the `server` directory. This file sets up an interpreter, and is powered by Open Interpreter.

To specify the text-to-speech service for the 01 `base_device.py`, set `interpreter.tts` to either "openai" for OpenAI, "elevenlabs" for ElevenLabs, or "coqui" for Coqui (local) in a profile. For the 01 Light, set `SPEAKER_SAMPLE_RATE` in `client.ino` under the `esp32` client directory to 24000 for Coqui (local) or 22050 for OpenAI TTS. We currently don't support ElevenLabs TTS on the 01 Light.

## Ubuntu Dependencies

```bash
sudo apt-get install portaudio19-dev ffmpeg cmake
```

# Contributors

[![01 project contributors](https://contrib.rocks/image?repo=OpenInterpreter/01&max=2000)](https://github.com/OpenInterpreter/01/graphs/contributors)

Please see our [contributing guidelines](CONTRIBUTING.md) for more details on how to get involved.

<br>

# Roadmap

Visit [our roadmap](/ROADMAP.md) to see the future of the 01.

<br>

## Background

### [Context ↗](https://github.com/KillianLucas/01/blob/main/CONTEXT.md)

The story of devices that came before the 01.

<br>

○
