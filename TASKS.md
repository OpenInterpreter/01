**OI**

- [ ] Finish skill library.
  - [ ] Create a system message that includes instructions on how to use the skill library.
  - [ ] Test it end-to-end.
    - [ ] Make sure it works with computer.skills.search (it should already work)
  - [ ] Create computer.skills.teach()
    - [ ]  Displays a tkinter message asking users to complete the task via text (eventually voice) in the most generalizable way possible. OI should use computer.mouse and computer.keyboard to fulfill each step, then save the generalized instruction as a skill. Clicking the mouse cancels teach mode. When OI invokes this skill in the future, it will just list those steps (it needs to figure out how to flexibly accomplish each step).
    - [ ] Computer: "What do you want to name this skill?"
    - [ ] User: Enters name in textbox
    - [ ] Computer: "Whats the First Step"
    - [ ] User: textbox appears types instructions
    - [ ] Textbox disappears
    - [ ] OI follows instruction
    - [ ] "Did that work?" Yes/No?
      - [ ] If No: repeat step training
    - [ ] Computer: "Great! What's the next step?" ....
    - [ ] Repeat until all steps of skill are completed
    - [ ] Save skill as a function next() steps through user's steps
  - [ ] Expose ^ via `01 --teach`.
- [ ] pip install 01
  - [ ] Add `01 --server --expose`.
  - [ ] Add --server --expose which will expose the server via something like Ngrok, display the public URL and a password, so the 01 Light can connect to it. This will let people use OI on their computer via their Light — i.e. "Check my emails" will run Applescript on their home computer.
- [ ] Sync Interpreter/Computer between code blocks
- [ ] New default dynamic system message with computer API + skills.
  - [ ] Develop default system message for executive assistant.
  - [ ] Better local system message
- [ ] write good docstrings for computer API
- [ ] Inject computer API into python routine
- [ ] determine streaming LMC protocol
  - [ ] inlcude headers?
- [ ] Why is OI starting so slowly? We could use time.time() around things to track it down.
- [ ] Create moondream-powered computer.camera.
  - [ ] Computer.camera.view(query) should take a picture and ask moondream the query. Defaults to "Describe this image in detail."
    - [ ] Takes Picture
    - [ ] Sends to describe API
    - [ ] prints and returns description
  - [ ] Llamafile for phi-2 + moondream
    - [ ] test on rPi + Jetson (+android mini phone?)

**OS**

- [ ] Queue speech results
  - [ ] TTS sentences should be queued + playback should stop once button is pressed
- [ ] expose server using Ngrok
- [ ] Swap out the current hosted functions for local ones.
  - [ ] TTS — Piper? OpenVoice? Rasspy?
  - [ ] STT — Whisper? Canary?
  - [ ] LLM — Phi-2 Q4 Llamafile, just need to download it, OI knows how to use Llamafiles
- [ ] Functional Requirements
  - [ ] for initial user setup and first experience
  - [ ] If Light and no internet, open a captive wifi page with text boxes: Wifi Name, Wifi Pass, (optional) Server URL, (optional) Server Pass
    - [ ] in device.py
- [ ] Camera input from user in device.py
- [ ] Can tapping the mic twice = trigger pressing the "button"? Simple sensing, just based on volume spikes?
- [ ] Update Architecture
  - [ ] Base Devise Class
  - [ ] Separate folders for Rasberry Pi, Desktop, Droid, App, Web
  - [ ] device.py for each folder has input logic for that device
    - [ ] Add basic TUI to device.py. Just renders messages and lets you add messages. Can easily copy OI's TUI.
  - [ ] index.html for each folder has user interface for that device
    - [ ] Web is just index.html
    - [ ] Display.html? gui.html?
- [ ] Replace bootloader and boot script— should just run 01, full screen TUI.
- [ ] Package it as an ISO, or figure out some other simple install instructions. How to easily install on a Pi?

**Hardware**

- [ ] (Hardware and software) Get the 01OS working on the **Jetson** or Pi. Pick one to move forward with.
- [ ] Connect the Seeed Sense (ESP32 with Wifi, Bluetooth and a mic) to a small DAC + amplifier + speaker.
- [ ] Connect the Seeed Sense to a battery.
- [ ] Configure the ESP32 to be a wireless mic + speaker for the Jetson or Pi.
- [ ] Connect the Jetson or Pi to a battery.
- [ ] Make a rudimentary case for the Seeed Sense + speaker. Optional.
- [ ] Make a rudimentary case for the Jetson or Pi. Optional.
- [ ] Determine recommended minimal hardware for the light & heavy.

**Release Day**

- [ ] Launch video "cambriah explosion" 3d Sketch
- [ ] Create form to get pre-release feedback from 200 interested people (who responded to Killian's tweet)

**DONE**
- [ ] Get Local TTS working on Mac [Shiven]
- [ ] Get Local SST working on Mac [Zohaib + Shiven]
- [ ] Debug level logging/printing [Tom]
- [ ] Get hardware (mic, speaker, button) working on the rPi (running on battery) [Ty]
- [ ] device.py conditionals for platform [Ty]
- [ ] Kernal filtering issues [Tom]
- [ ] .env file [Tom]
- [ ] Save computer messages in User.json [Kristijan]
- [ ] Service Management [Zach]
