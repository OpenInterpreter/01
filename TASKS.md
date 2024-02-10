**OI**

- [ ] Finish skill library.
  - [ ] Create a system message that includes instructions on how to use the skill library.
  - [ ] Test it end-to-end.
  - [ ] Create computer.skills.teach(), which displays a message asking users to complete the task via voice in the most generalizable way possible. OI should use computer.mouse and computer.keyboard to fulfill each step, then save the generalized instruction as a skill. Clicking the mouse cancels teach mode. When OI invokes this skill in the future, it will just list those steps (it needs to figure out how to flexibly accomplish each step).
  - [ ] Expose ^ via `interpreter --teach`.
- [ ] Add `interpreter --server --expose`.
  - [ ] Include the 01's --server in the next OI update.
  - [ ] Add --server --expose which will expose the server via something like Ngrok, display the public URL and a password, so the 01 Light can connect to it. This will let people use OI on their computer via their Light — i.e. "Check my emails" will run Applescript on their home computer.
- [ ] Why is OI starting so slowly? We could use time.time() around things to track it down.
- [ ] Create moondream-powered computer.camera.
  - [ ] Computer.camera.view(query) should take a picture and ask moondream the query. Defaults to "Describe this image in detail."

**OS**

- [ ] Queue speech results
- [ ] Swap out the current hosted functions for local ones.
  - [ ] TTS — Piper? OpenVoice? Rasspy?
  - [ ] STT — Whisper? Canary?
  - [ ] LLM — Phi-2 Q4 Llamafile, just need to download it, OI knows how to use Llamafiles
- [ ] If Light and no internet, open a captive wifi page with text boxes: Wifi Name, Wifi Pass, (optional) Server URL, (optional) Server Pass
- [ ] Can tapping the mic twice = pressing the "button"? Simple sensing, just based on volume spikes?
- [ ] Add basic TUI to device.py. Just renders messages and lets you add messages. Can easily copy OI's TUI.
- [ ] Replace bootloader and boot script— should just run 01, full screen TUI.
- [ ] Package it as an ISO, or figure out some other simple install instructions. How to easily install on a Pi?

**Hardware**

- [ ] (Hardware and software) Get the 01OS working on the Jetson or Pi. Pick one to move forward with.
- [ ] Connect the Seeed Sense (ESP32 with Wifi, Bluetooth and a mic) to a small DAC + amplifier + speaker.
- [ ] Connect the Seeed Sense to a battery.
- [ ] Configure the ESP32 to be a wireless mic + speaker for the Jetson or Pi.
- [ ] Connect the Jetson or Pi to a battery.
- [ ] Make a rudimentary case for the Seeed Sense + speaker. Optional.
- [ ] Make a rudimentary case for the Jetson or Pi. Optional.

Misc.

- [ ] Develop default system message for executive assistant.
- [ ] Determine recommended minimal hardware for the light & heavy.
