# ○

Official repository for [The 01 Project](https://twitter.com/hellokillian/status/1745875973583896950).

<br>

### [View task list ↗](https://github.com/KillianLucas/01/blob/main/TASKS.md)

<br>

## Configuration:

Copy the OS/01/.env.example file to OS/01/.env and then configure the environment variables within the file.

## Install Required Libraries:

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

## Usage

```bash
cd OS/01
bash start.sh
```

If you want to run local text-to-speech and speech-to-text, set `ALL_LOCAL` in your `OS/01/.env` config to True. This will use the [whisper.cpp](https://github.com/ggerganov/whisper.cpp) and [Piper](https://github.com/rhasspy/piper) models.
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

