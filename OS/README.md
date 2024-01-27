# 01OS

This folder contains everything we would change about Ubuntu. A folder here represents a folder added to `root`.

# Plan

1. We modify the bootloader to show a circle.
2. We modify linux so that the primary display is a virtual display, and the display the user sees is the secondary display.
3. We make a fullscreen app auto-start on the secondary display, kiosk mode chromium, in /01/app/index.html.
4. We also make it so that 01/core/main.py is run on start-up. This is the interpreter.
5. We put monoliths around the system, which put information into /01/core/queue.
