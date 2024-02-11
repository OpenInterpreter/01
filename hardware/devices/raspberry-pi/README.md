# How to set up 01 on a Raspberry Pi

## Supplies needed

- Raspberry Pi 5
- Micro SD Card
- USB-C cable
- Micro HDMI to HDMI cable
- Monitor
- Keyboard
- Mouse
- USB Microphone ([like this one](https://www.amazon.com/dp/B071WH7FC6?psc=1&ref=ppx_yo2ov_dt_b_product_details))
- USB or Bluetooth speaker
- Breadboard, jumper wires, 220R resistor and button (a kit like [this one](https://www.amazon.com/Smraza-Electronics-Potentiometer-tie-Points-Breadboard/dp/B0B62RL725/ref=sr_1_20?crid=MQDBAOQU7RYY&keywords=breadboard+kit&qid=1707665692&s=electronics&sprefix=breadboard%2Celectronics%2C346&sr=1-20) has everything you need)

## SD card setup

- Flash a new sd card using [Raspberry Pi Imager](https://www.raspberrypi.com/software/)
  - Pick your device (only tested on Raspberry Pi 5)
  - Select the OS: Scroll down to "Other General OS" Then select Ubuntu Desktop 64bit
  - Select the storage: Select your sd card
  - Proceed to flashing by selecting "Write"

## Hardware set up

- Connect Raspberry pi board to USB-C power
- Connect a keyboard, mouse, and mic to the USB ports
- Connect a monitor to the micro HDMI port
- Insert your newly flashed SD card into the slot under the device by the power button
- Power it on with the power button
- Hook up the Button to the breadboard,it should look like this:
  ![Button](button-diagram.png)

## Ubuntu set up

- Go through the system configuration on start up:
  - Make sure to connect to wifi, we will need it to install 01 and it's packages
  - Choose a password you will remember, you will need it later
- Open terminal
- `sudo apt update && sudo apt upgrade -y`
  - Sometimes `dpkg` will complain, if it does, run `sudo dpkg --configure -a` and then run the update and upgrade commands again

Clone the repo:

- `sudo apt install git -y`
- `git clone https://github.com/KillianLucas/01`
- `cd 01/OS/01/`

Set up a virtual environment:

- `sudo apt install python3-venv -y`
- `python3 -m venv venv`
- `source venv/bin/activate`

Install packages:

- `sudo apt install ffmpeg portaudio19-dev` (ffmpeg and portaudio19-dev need to be installed with apt on linux)
- `sudo apt-get update`
- `sudo apt-get install gpiod`
- `pip install -r requirements.txt`
- pyaudio install might fail, these commands should fix it:

  - `sudo apt-get install gcc make python3-dev portaudio19-dev`
  - `pip install pyaudio`

Rename and edit the .env file:

- `mv .env.example .env` (rename the .env file)
- Add your OpenAI key to the .env file, or by running `export OPENAI_API_KEY="sk-..."`
  - To add it to the .env in the terminal, run `nano .env`
  - Add the key to the `OPENAI_API_KEY` line
  - Save and exit by pressing `ctrl + x`, then `y`, then `enter`

Run the start script:

- `bash start.sh`
  - There may be a few packages that didn't install, yielding a 'ModuleNotFoundError' error. If you see this, manually install each of them with pip and retry the `bash start.sh` command.

Done! You should now be able to use 01 on your Raspberry Pi 5, and use the button to invoke the assistant.
