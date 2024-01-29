# What is this?

This is the operating system that powers the 01.

# No, I mean what's this folder?

It's the `diff` between 01OS and Ubuntu.

01OS should be a customized version of Linux. Ubuntu is popular, stable, runs on lots of different hardware. **(open question: Should this be Xubuntu, which is lighter? or something else?)**

We want to _build on_ Ubuntu by customizing the stable branch programatically, not by forking it — which would mean we'd have to maintain the underlying OS, merge in security patches, etc. Yuck.

This folder contains everything we want to change from the base Ubuntu. A folder here represents a folder added/modified at the `root`. You can think of it like the `diff` between 01OS and Ubuntu.

I imagine we'll use something like Cubic to then press this + Ubuntu into an ISO image.

# Setup & Usage

Clone this repo, then run `OS/01/start.sh`.

# Structure

### `start.sh`

The start script's job is to start the `core` and the `app` (in full-screen mode).

### `/core`

The `core`'s job is to:

1. Set up the language model
2. Set up the interpreter
3. Serve the interpreter at "/"

### `/app`

The `app`'s job is to be the interface between the user and the interpreter (text in). This could be text only, audio, video, who knows, but it becomes LMC messages or plain text.

For the first version, I think we should just handle audio in/out. So the `app`'s job here is to:

1. Be a fullscreen app for the user to use 01
2. Turn the user's speech into text and send it to "/"
3. Turn the interpreter's text into speech and play it for the user

### Changes to Linux

We need to make the following changes:

1. Modify the bootloader to just show white circle on black
2. Auto start the start script, `start.sh`
3. Put detectors everywhere, which will put [LMC Messages](https://docs.openinterpreter.com/protocols/lmc-messages) from the computer into `/01/core/queue`. Michael suggested we simply watch and filter the `dmesg` stream (I think that's what it's called?), so I suppose we could have a script like `/01/core/kernel_watcher.py` that puts things into the queue? Honestly knowing we could get it all from one place like that— maybe this should be simpler. Is the queue necessary? How about we just expect the computer to send computer messages to the websocket at `/`? Then yeah, maybe we do have redis there, then instead of looking at that folder, we check the redis queue...
4. (open question: should we do this? do we want the first 01 to be ready for GUI control?) Make the display that's shown to the user (and filled with the `app`) the _secondary_ display. The primary display will be a normal Ubuntu desktop, invisible to the user. Why? So the interpreter can control the primary display "under the hood".
