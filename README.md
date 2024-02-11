# ○

Official repository for [The 01 Project](https://twitter.com/hellokillian/status/1745875973583896950).

<br>

### [View task list ↗](https://github.com/KillianLucas/01/blob/main/TASKS.md)

<br>

## Setup

```bash
# MacOS
brew install portaudio ffmpeg

# Ubuntu
sudo apt-get install portaudio19-dev libav-tools
```

```bash
python -m pip install -r requirements.txt
```
NB: Depending on your local Python version, you may run into [this issue↗](https://github.com/TaylorSMarks/playsound/issues/150) installing playsound. Workarounds are provided in the issue.

If you want to run local speech-to-text from whisper, download the GGML Whisper model from [Huggingface](https://huggingface.co/ggerganov/whisper.cpp). Then in `OS/01/start.sh`, set `ALL_LOCAL=TRUE` and set `WHISPER_MODEL_PATH` to the path of the model.

## Usage

```bash
cd OS/01
bash start.sh
```

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

## Project Management

### [Tasks ↗](https://github.com/KillianLucas/01/blob/main/TASKS.md)

Our master task list.

<br>

> **13** days remaining until launch

