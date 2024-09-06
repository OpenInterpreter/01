---
title: "ESP32"
description: "How to setup the ESP32"
---

To set up the ESP32 for use with 01, follow this guide to install the firmware:

1. Download [Arduino IDE](https://www.arduino.cc/en/software).

2. Get the firmware by copying the contents of [client.ino](https://github.com/OpenInterpreter/01/blob/main/software/source/clients/esp32/src/client/client.ino) from the 01 repository.

<div style="display: flex; justify-content: center;">
  <img src="assets/copy-client.png" alt="Copy client.ino contents" width="60%" />
</div>

3. Open Arduino IDE and paste the client.ino contents.

<div style="display: flex; justify-content: center;">
  <img src="assets/paste-client.png" alt="Paste client.ino contents" width="60%" />

  <img src="assets/pasted-client.png" alt="Pasted client.ino contents" width="60%" />
</div>

4. Hardcode your WiFi SSID, WiFi password, and server URL into the code. 

<div style="display: flex; justify-content: center;">
  <img src="assets/hardcode-wifi-pass-server.png" alt="Hardcode WiFi SSID and password" width="60%" />
</div>

<div style="display: flex; justify-content: center;">
  <div style="width: 80%;">
    Hardcoding is recommended for a more streamlined setup and development environment. However, if you don't hardcode these values or if the ESP32 can't connect using the provided information, it will automatically default to a captive portal for configuration. 
  </div>
</div>

5. Go to Tools -> Board -> Boards Manager, search "esp32", then install the boards by Arduino and Espressif.

<div style="display: flex; justify-content: center;">
  <img src="assets/boards-manager.png" alt="Install ESP32 boards" width="60%" />
</div>

5. Go to Tools -> Manage Libraries, then install the following:

- M5Atom by M5Stack ([Reference](https://www.arduino.cc/reference/en/libraries/m5atom/))

<div style="display: flex; justify-content: center;">
  <img src="assets/M5-atom-library.png" alt="Install M5Atom library" width="60%" />

  <img src="assets/m5-atom-install-all.png" alt="Install all M5Atom dependencies" width="60%" />
</div>

- WebSockets by Markus Sattler ([Reference](https://www.arduino.cc/reference/en/libraries/websockets/))

<div style="display: flex; justify-content: center;">
  <img src="assets/WebSockets by Markus Sattler.png" alt="Install WebSockets library" width="60%" />
</div>

- AsyncTCP by dvarrel ([Reference](https://github.com/dvarrel/AsyncTCP))

<div style="display: flex; justify-content: center;">
  <img src="assets/AsyncTCP by dvarrel.png" alt="Install AsyncTCP library" width="60%" />
</div>

- ESPAsyncWebServer by lacamera ([Reference](https://github.com/lacamera/ESPAsyncWebServer))

<div style="display: flex; justify-content: center;">
  <img src="assets/ESPAsyncWebServer by lacamera.png" alt="Install ESPAsyncWebServer library" width="60%" />

  <img src="assets/ESPAsyncWebServer-install-all.png" alt="Install all ESPAsyncWebServer dependencies" width="60%" />
</div>

6. To flash the .ino to the board, connect the board to the USB port.

<div style="display: flex; justify-content: center;">
  <img src="assets/connect_usb.jpeg" alt="Connect USB" width="60%" />
</div>

7. Select the port from the dropdown on the IDE, then select the M5Atom board (or M5Stack-ATOM if you have that).

<div style="display: flex; justify-content: center;">
  <img src="assets/Select Board and Port.png" alt="Select Board and Port" width="60%" />
</div>

8. Click on upload to flash the board.

<div style="display: flex; justify-content: center;">
  <img src="assets/Upload.png" alt="Upload firmware" width="60%" />
</div>



---

Watch this video from Thomas for a step-by-step guide on flashing the ESP32 and connecting the 01.

[![ESP32 Flashing Tutorial](https://img.youtube.com/vi/Y76zed8nEE8/0.jpg)](https://www.youtube.com/watch?v=Y76zed8nEE8 "ESP32 Flashing Tutorial")
