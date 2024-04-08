# ESP32 Playback

To set up audio recording + playback on the ESP32 (M5 Atom), do the following:

1. Open Arduino IDE, and open the `client/client.ino` file
2. Go to Tools -> Board -> Boards Manager, search "esp32", then install the boards by Arduino and Espressif
3. Go to Tools -> Manage Libraries, then install the following (_with_ dependencies, if it prompts you to install with/without dependencies):
    - M5Atom by M5Stack
    - WebSockets by Markus Sattler
    - ESPAsyncWebServer by lacamera
4. The board needs to connect to WiFi. Once you flash, connect to ESP32 wifi "captive" which will get wifi details. Once it connects, it will ask you to enter 01OS server address in the format "domain.com:port" or "ip:port". Once its able to connect you can use the device.
5. To flash the .ino to the board, connect the board to the USB port, select the port from the dropdown on the IDE, then select the M5Atom board (or M5Stack-ATOM if you have that). Click on upload to flash the board.

### Alternative - PlatformIO

You don't need anything, PlatformIO will install everything for you, dependencies, tool chains, etc.

Please install first [PlatformIO](http://platformio.org/) open source ecosystem for IoT development compatible with **Arduino** IDE and its command line tools (Windows, MacOs and Linux), and then enter to the firmware directory:

```bash
cd client/
```

And build and upload the firmware with a simple command:

```bash
pio run --target upload
```
