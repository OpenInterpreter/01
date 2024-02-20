# ESP32 Playback

To set up audio recording + playback on the ESP32 (M5 Atom), do the following:

1. Open Arduino IDE, and open the `playback/playback.ino` file
2. Go to Tools -> Board -> Boards Manager, search "esp32", then install the boards by Arduino and Espressif
3. Go to Tools -> Manage Libraries, then install the following:
    - M5Atom by M5Stack
    - WebSockets by Markus Sattler
4. The board needs to connect to WiFi. Go to the playback.ino code, then add your IP to COMPUTER_IP (line 15) and add your WiFi details (line 180). To find IP on macOS run `ipconfig getifaddr en0` in a terminal window.
5. To flash the .ino to the board, connect the board to the USB port, select the port from the dropdown on the IDE, then select the M5Atom board (or M5Stack-ATOM if you have that). Click on upload to flash the board.