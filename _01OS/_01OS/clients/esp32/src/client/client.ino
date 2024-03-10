#include <driver/i2s.h>
#include <M5Atom.h>
#include <Arduino.h>  //not needed in the arduino ide
#include <AsyncTCP.h> //https://github.com/me-no-dev/AsyncTCP using the latest dev version from @me-no-dev
#include <DNSServer.h>
#include <ESPAsyncWebServer.h> //https://github.com/me-no-dev/ESPAsyncWebServer using the latest dev version from @me-no-dev
#include <esp_wifi.h>          //Used for mpdu_rx_disable android workaround
#include <ArduinoHttpClient.h>
#include <WiFi.h>
#include <WiFiClient.h>
#include <WiFiMulti.h>
#include <WiFiClientSecure.h>
#include <WebSocketsClient.h>

String server_domain = "";
int server_port = 8000;

// ----------------------- START OF WIFI CAPTIVE PORTAL -------------------

// Pre reading on the fundamentals of captive portals https://textslashplain.com/2022/06/24/captive-portals/

const char *ssid = "captive"; // FYI The SSID can't have a space in it.
// const char * password = "12345678"; //Atleast 8 chars
const char *password = NULL; // no password

#define MAX_CLIENTS 4  // ESP32 supports up to 10 but I have not tested it yet
#define WIFI_CHANNEL 6 // 2.4ghz channel 6 https://en.wikipedia.org/wiki/List_of_WLAN_channels#2.4_GHz_(802.11b/g/n/ax)

const IPAddress localIP(4, 3, 2, 1);          // the IP address the web server, Samsung requires the IP to be in public space
const IPAddress gatewayIP(4, 3, 2, 1);        // IP address of the network should be the same as the local IP for captive portals
const IPAddress subnetMask(255, 255, 255, 0); // no need to change: https://avinetworks.com/glossary/subnet-mask/
const String localIPURL = "http://4.3.2.1";   // a string version of the local IP with http, used for redirecting clients to your webpage

// Number of milliseconds to wait without receiving any data before we give up
const int kNetworkTimeout = 30 * 1000;
// Number of milliseconds to wait if no data is available before trying again
const int kNetworkDelay = 1000;

String generateHTMLWithSSIDs()
{
    String html = "<!DOCTYPE html><html><body><h2>Select Wi-Fi Network</h2><form action='/submit' method='POST'><label for='ssid'>SSID:</label><select id='ssid' name='ssid'>";

    int n = WiFi.scanComplete();
    for (int i = 0; i < n; ++i)
    {
        html += "<option value='" + WiFi.SSID(i) + "'>" + WiFi.SSID(i) + "</option>";
    }

    html += "</select><br><label for='password'>Password:</label><input type='password' id='password' name='password'><br><input type='submit' value='Connect'></form></body></html>";

    return html;
}

const char index_html[] PROGMEM = R"=====(
<!DOCTYPE html>
<html>
<head>
  <title>WiFi Setup</title>
  <style>
    body {background-color:#06cc13;}
    h1 {color: white;}
    h2 {color: white;}
  </style>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body>
  <h1>WiFi Setup</h1>
  <form action="/submit" method="post">
    <label for="ssid">SSID:</label><br>
    <input type="text" id="ssid" name="ssid"><br>
    <label for="password">Password:</label><br>
    <input type="password" id="password" name="password"><br><br>
    <input type="submit" value="Connect">
  </form>
</body>
</html>
)=====";

const char post_connected_html[] PROGMEM = R"=====(
<!DOCTYPE html>
<html>
<head>
  <title>_01OS Setup</title>
  <style>
    body {background-color:white;}
    h1 {color: black;}
    h2 {color: black;}
  </style>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body>
  <h1>_01OS Setup</h1>
  <form action="/submit__01OS" method="post">
    <label for="server_address">_01OS Server Address:</label><br>
    <input type="text" id="server_address" name="server_address"><br>
    <input type="submit" value="Connect">
  </form>
</body>
</html>
)=====";

DNSServer dnsServer;
AsyncWebServer server(80);

void setUpDNSServer(DNSServer &dnsServer, const IPAddress &localIP)
{
// Define the DNS interval in milliseconds between processing DNS requests
#define DNS_INTERVAL 30

    // Set the TTL for DNS response and start the DNS server
    dnsServer.setTTL(3600);
    dnsServer.start(53, "*", localIP);
}

void startSoftAccessPoint(const char *ssid, const char *password, const IPAddress &localIP, const IPAddress &gatewayIP)
{
// Define the maximum number of clients that can connect to the server
#define MAX_CLIENTS 4
// Define the WiFi channel to be used (channel 6 in this case)
#define WIFI_CHANNEL 6

    // Set the WiFi mode to access point and station
    // WiFi.mode(WIFI_MODE_AP);

    // Define the subnet mask for the WiFi network
    const IPAddress subnetMask(255, 255, 255, 0);

    // Configure the soft access point with a specific IP and subnet mask
    WiFi.softAPConfig(localIP, gatewayIP, subnetMask);

    // Start the soft access point with the given ssid, password, channel, max number of clients
    WiFi.softAP(ssid, password, WIFI_CHANNEL, 0, MAX_CLIENTS);

    // Disable AMPDU RX on the ESP32 WiFi to fix a bug on Android
    esp_wifi_stop();
    esp_wifi_deinit();
    wifi_init_config_t my_config = WIFI_INIT_CONFIG_DEFAULT();
    my_config.ampdu_rx_enable = false;
    esp_wifi_init(&my_config);
    esp_wifi_start();
    vTaskDelay(100 / portTICK_PERIOD_MS); // Add a small delay
}

void connectToWifi(String ssid, String password)
{
    WiFi.begin(ssid.c_str(), password.c_str());

    // Wait for connection to establish
    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 20)
    {
        delay(1000);
        Serial.print(".");
        attempts++;
    }

    if (WiFi.status() == WL_CONNECTED)
    {
        Serial.println("Connected to Wi-Fi");
    }
    else
    {
        Serial.println("Failed to connect to Wi-Fi. Check credentials.");
    }
}

bool connectTo_01OS(String server_address)
{
    int err = 0;

    String domain;
    String portStr;

    if (server_address.indexOf(":") != -1) {
        domain = server_address.substring(0, server_address.indexOf(':'));
        portStr = server_address.substring(server_address.indexOf(':') + 1);
    } else {
        domain = server_address;
        portStr = ""; // or any default value you want to assign
    }
    int port = 0; // Default port value
    if (portStr.length() > 0) {
        port = portStr.toInt();
    }

    WiFiClient c;
    HttpClient http(c, domain.c_str(), port);

    Serial.println("Connecting to _01OS at " + domain + ":" + port + "/ping");
    err = http.get("/ping");
    // err = http.get("arduino.cc", "/");
    bool connectionSuccess = false;

    if (err == 0)
    {
        Serial.println("Started the ping request");

        err = http.responseStatusCode();
        if (err >= 0)
        {
            Serial.print("Got status code: ");
            Serial.println(err);

            if (err == 200)
            {
                server_domain = domain;
                server_port = port;
                connectionSuccess = true;
            }

            err = http.skipResponseHeaders();
            if (err >= 0)
            {
                int bodyLen = http.contentLength();
                Serial.print("Content length is: ");
                Serial.println(bodyLen);
                Serial.println();
                Serial.println("Body returned follows:");

                // Now we've got to the body, so we can print it out
                unsigned long timeoutStart = millis();
                char c;
                // Whilst we haven't timed out & haven't reached the end of the body
                while ((http.connected() || http.available()) &&
                       ((millis() - timeoutStart) < kNetworkTimeout))
                {
                    if (http.available())
                    {
                        c = http.read();
                        // Print out this character
                        Serial.print(c);

                        bodyLen--;
                        // We read something, reset the timeout counter
                        timeoutStart = millis();
                    }
                    else
                    {
                        // We haven't got any data, so let's pause to allow some to
                        // arrive
                        delay(kNetworkDelay);
                    }
                }
            }
            else
            {
                Serial.print("Failed to skip response headers: ");
                Serial.println(err);
            }
        }
        else
        {
            Serial.print("Getting response failed: ");
            Serial.println(err);
        }
    }
    else
    {
        Serial.print("Connect failed: ");
        Serial.println(err);
    }
  return connectionSuccess;
}

void setUpWebserver(AsyncWebServer &server, const IPAddress &localIP)
{
    //======================== Webserver ========================
    // WARNING IOS (and maybe macos) WILL NOT POP UP IF IT CONTAINS THE WORD "Success" https://www.esp8266.com/viewtopic.php?f=34&t=4398
    // SAFARI (IOS) IS STUPID, G-ZIPPED FILES CAN'T END IN .GZ https://github.com/homieiot/homie-esp8266/issues/476 this is fixed by the webserver serve static function.
    // SAFARI (IOS) there is a 128KB limit to the size of the HTML. The HTML can reference external resources/images that bring the total over 128KB
    // SAFARI (IOS) popup browser has some severe limitations (javascript disabled, cookies disabled)

    // Required
    server.on("/connecttest.txt", [](AsyncWebServerRequest *request)
              { request->redirect("http://logout.net"); }); // windows 11 captive portal workaround
    server.on("/wpad.dat", [](AsyncWebServerRequest *request)
              { request->send(404); }); // Honestly don't understand what this is but a 404 stops win 10 keep calling this repeatedly and panicking the esp32 :)

    // Background responses: Probably not all are Required, but some are. Others might speed things up?
    // A Tier (commonly used by modern systems)
    server.on("/generate_204", [](AsyncWebServerRequest *request)
              { request->redirect(localIPURL); }); // android captive portal redirect
    server.on("/redirect", [](AsyncWebServerRequest *request)
              { request->redirect(localIPURL); }); // microsoft redirect
    server.on("/hotspot-detect.html", [](AsyncWebServerRequest *request)
              { request->redirect(localIPURL); }); // apple call home
    server.on("/canonical.html", [](AsyncWebServerRequest *request)
              { request->redirect(localIPURL); }); // firefox captive portal call home
    server.on("/success.txt", [](AsyncWebServerRequest *request)
              { request->send(200); }); // firefox captive portal call home
    server.on("/ncsi.txt", [](AsyncWebServerRequest *request)
              { request->redirect(localIPURL); }); // windows call home

    // B Tier (uncommon)
    //  server.on("/chrome-variations/seed",[](AsyncWebServerRequest *request){request->send(200);}); //chrome captive portal call home
    //  server.on("/service/update2/json",[](AsyncWebServerRequest *request){request->send(200);}); //firefox?
    //  server.on("/chat",[](AsyncWebServerRequest *request){request->send(404);}); //No stop asking Whatsapp, there is no internet connection
    //  server.on("/startpage",[](AsyncWebServerRequest *request){request->redirect(localIPURL);});

    // return 404 to webpage icon
    server.on("/favicon.ico", [](AsyncWebServerRequest *request)
              { request->send(404); }); // webpage icon

    // Serve Basic HTML Page
    server.on("/", HTTP_ANY, [](AsyncWebServerRequest *request)
              {
	String htmlContent = index_html;
    Serial.printf("wifi scan complete: %d . WIFI_SCAN_RUNNING: %d", WiFi.scanComplete(), WIFI_SCAN_RUNNING);
    if(WiFi.scanComplete() > 0) {
      // Scan complete, process results
      Serial.println("done scanning wifi");
      htmlContent = generateHTMLWithSSIDs();
      // WiFi.scanNetworks(true); // Start a new scan in async mode
    }
		AsyncWebServerResponse *response = request->beginResponse(200, "text/html", htmlContent);
		response->addHeader("Cache-Control", "public,max-age=31536000");  // save this file to cache for 1 year (unless you refresh)
		request->send(response);
		Serial.println("Served Basic HTML Page"); });

    // the catch all
    server.onNotFound([](AsyncWebServerRequest *request)
                      {
		request->redirect(localIPURL);
		Serial.print("onnotfound ");
		Serial.print(request->host());	// This gives some insight into whatever was being requested on the serial monitor
		Serial.print(" ");
		Serial.print(request->url());
		Serial.print(" sent redirect to " + localIPURL + "\n"); });

    server.on("/submit", HTTP_POST, [](AsyncWebServerRequest *request)
              {
    String ssid;
    String password;
    
    // Check if SSID parameter exists and assign it
    if(request->hasParam("ssid", true)) {
        ssid = request->getParam("ssid", true)->value();
    }

    // Check if Password parameter exists and assign it
    if(request->hasParam("password", true)) {
        password = request->getParam("password", true)->value();
    }

    // Attempt to connect to the Wi-Fi network with these credentials
    connectToWifi(ssid, password);

    // Redirect user or send a response back
    if (WiFi.status() == WL_CONNECTED) {
      String htmlContent = post_connected_html;
      AsyncWebServerResponse *response = request->beginResponse(200, "text/html", htmlContent);
      response->addHeader("Cache-Control", "public,max-age=31536000");  // save this file to cache for 1 year (unless you refresh)
      request->send(response);
      Serial.println("Served Post connection HTML Page"); 
    } else {
      request->send(200, "text/plain", "Failed to connect to " + ssid);
    } });

    server.on("/submit__01OS", HTTP_POST, [](AsyncWebServerRequest *request)
              {
    String server_address;
    
    // Check if SSID parameter exists and assign it
    if(request->hasParam("server_address", true)) {
        server_address = request->getParam("server_address", true)->value();
    }

    // Attempt to connect to the Wi-Fi network with these credentials
    bool connectedToServer = connectTo_01OS(server_address);

    // Redirect user or send a response back
    String connectionMessage;

    if (connectedToServer)
    {
      connectionMessage = "Connected to _01OS " + server_address;
    }
    else
    {
      connectionMessage = "Couldn't connect to _01OS " + server_address;
    }
    request->send(200, "text/plain", connectionMessage); });
}

// ----------------------- END OF WIFI CAPTIVE PORTAL -------------------

// ----------------------- START OF PLAYBACK -------------------

#define CONFIG_I2S_BCK_PIN 19
#define CONFIG_I2S_LRCK_PIN 33
#define CONFIG_I2S_DATA_PIN 22
#define CONFIG_I2S_DATA_IN_PIN 23
#define SPEAKER_I2S_NUMBER I2S_NUM_0
#define MODE_MIC 0
#define MODE_SPK 1
#define DATA_SIZE 1024

uint8_t microphonedata0[1024 * 10];
uint8_t speakerdata0[1024 * 1];
int speaker_offset;
int data_offset;

bool recording = false;
WebSocketsClient webSocket;

class ButtonChecker
{
public:
    void loop()
    {
        lastTickState = thisTickState;
        thisTickState = M5.Btn.isPressed() != 0;
    }

    bool justPressed()
    {
        return thisTickState && !lastTickState;
    }

    bool justReleased()
    {
        return !thisTickState && lastTickState;
    }

private:
    bool lastTickState = false;
    bool thisTickState = false;
};

ButtonChecker button = ButtonChecker();

void InitI2SSpeakerOrMic(int mode)
{
    Serial.printf("InitI2sSpeakerOrMic %d\n", mode);
    esp_err_t err = ESP_OK;

    i2s_driver_uninstall(SPEAKER_I2S_NUMBER);
    i2s_config_t i2s_config = {
        .mode = (i2s_mode_t)(I2S_MODE_MASTER),
        .sample_rate = 16000,
        .bits_per_sample =
            I2S_BITS_PER_SAMPLE_16BIT, // is fixed at 12bit, stereo, MSB
        .channel_format = I2S_CHANNEL_FMT_ALL_RIGHT,
#if ESP_IDF_VERSION > ESP_IDF_VERSION_VAL(4, 1, 0)
        .communication_format =
            I2S_COMM_FORMAT_STAND_I2S, // Set the format of the communication.
#else                                  // 设置通讯格式
        .communication_format = I2S_COMM_FORMAT_I2S,
#endif
        .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
        .dma_buf_count = 6,
        .dma_buf_len = 60,
    };
    if (mode == MODE_MIC)
    {
        i2s_config.mode =
            (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX | I2S_MODE_PDM);
    }
    else
    {
        i2s_config.mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_TX);
        i2s_config.use_apll = false;
        i2s_config.tx_desc_auto_clear = true;
    }

    err += i2s_driver_install(SPEAKER_I2S_NUMBER, &i2s_config, 0, NULL);
    i2s_pin_config_t tx_pin_config;

#if (ESP_IDF_VERSION > ESP_IDF_VERSION_VAL(4, 3, 0))
    tx_pin_config.mck_io_num = I2S_PIN_NO_CHANGE;
#endif
    tx_pin_config.bck_io_num = CONFIG_I2S_BCK_PIN;
    tx_pin_config.ws_io_num = CONFIG_I2S_LRCK_PIN;
    tx_pin_config.data_out_num = CONFIG_I2S_DATA_PIN;
    tx_pin_config.data_in_num = CONFIG_I2S_DATA_IN_PIN;

    // Serial.println("Init i2s_set_pin");
    err += i2s_set_pin(SPEAKER_I2S_NUMBER, &tx_pin_config);
    // Serial.println("Init i2s_set_clk");
    err += i2s_set_clk(SPEAKER_I2S_NUMBER, 16000, I2S_BITS_PER_SAMPLE_16BIT,
                       I2S_CHANNEL_MONO);
}

void speaker_play(uint8_t *payload, uint32_t len)
{
    Serial.printf("received %lu bytes", len);
    size_t bytes_written;
    InitI2SSpeakerOrMic(MODE_SPK);
    i2s_write(SPEAKER_I2S_NUMBER, payload, len,
              &bytes_written, portMAX_DELAY);
}

void webSocketEvent(WStype_t type, uint8_t *payload, size_t length)
{
    switch (type)
    {
    case WStype_DISCONNECTED:
        Serial.printf("[WSc] Disconnected!\n");
        break;
    case WStype_CONNECTED:
        Serial.printf("[WSc] Connected to url: %s\n", payload);

        // send message to server when Connected
        break;
    case WStype_TEXT:
        Serial.printf("[WSc] get text: %s\n", payload);
        {
            std::string str(payload, payload + length);
            bool isAudio = str.find("\"audio\"") != std::string::npos;
            if (isAudio && str.find("\"start\"") != std::string::npos)
            {
                Serial.println("start playback");
                speaker_offset = 0;
                InitI2SSpeakerOrMic(MODE_SPK);
            }
            else if (isAudio && str.find("\"end\"") != std::string::npos)
            {
                Serial.println("end playback");
                // speaker_play(speakerdata0, speaker_offset);
                // speaker_offset = 0;
            }
        }
        // send message to server
        // webSocket.sendTXT("message here");
        break;
    case WStype_BIN:
        Serial.printf("[WSc] get binary length: %u\n", length);
        memcpy(speakerdata0 + speaker_offset, payload, length);
        speaker_offset += length;
        size_t bytes_written;
        i2s_write(SPEAKER_I2S_NUMBER, speakerdata0, speaker_offset, &bytes_written, portMAX_DELAY);
        speaker_offset = 0;

        // send data to server
        // webSocket.sendBIN(payload, length);
        break;
    case WStype_ERROR:
    case WStype_FRAGMENT_TEXT_START:
    case WStype_FRAGMENT_BIN_START:
    case WStype_FRAGMENT:
    case WStype_FRAGMENT_FIN:
        break;
    }
}

void websocket_setup(String server_domain, int port)
{
    if (WiFi.status() != WL_CONNECTED)
    {
        Serial.println("Not connected to WiFi. Abandoning setup websocket");
        return;
    }
    Serial.println("connected to WiFi");
    webSocket.begin(server_domain, port, "/");
    webSocket.onEvent(webSocketEvent);
    //    webSocket.setAuthorization("user", "Password");
    webSocket.setReconnectInterval(5000);
}

void flush_microphone()
{
    Serial.printf("[microphone] flushing %d bytes of data\n", data_offset);
    if (data_offset == 0)
        return;
    webSocket.sendBIN(microphonedata0, data_offset);
    data_offset = 0;
}

// ----------------------- END OF PLAYBACK -------------------

bool hasSetupWebsocket = false;

void setup()
{
    // Set the transmit buffer size for the Serial object and start it with a baud rate of 115200.
    Serial.setTxBufferSize(1024);
    Serial.begin(115200);

    // Wait for the Serial object to become available.
    while (!Serial)
        ;

    WiFi.mode(WIFI_AP_STA);

    // Print a welcome message to the Serial port.
    Serial.println("\n\nCaptive Test, V0.5.0 compiled " __DATE__ " " __TIME__ " by CD_FER"); //__DATE__ is provided by the platformio ide
    Serial.printf("%s-%d\n\r", ESP.getChipModel(), ESP.getChipRevision());

    startSoftAccessPoint(ssid, password, localIP, gatewayIP);

    setUpDNSServer(dnsServer, localIP);

    WiFi.scanNetworks(true);

    setUpWebserver(server, localIP);
    server.begin();

    Serial.print("\n");
    Serial.print("Startup Time:"); // should be somewhere between 270-350 for Generic ESP32 (D0WDQ6 chip, can have a higher startup time on first boot)
    Serial.println(millis());
    Serial.print("\n");

    M5.begin(true, false, true);
    M5.dis.drawpix(0, CRGB(128, 128, 0));
}

void loop()
{
    dnsServer.processNextRequest(); // I call this atleast every 10ms in my other projects (can be higher but I haven't tested it for stability)
    delay(DNS_INTERVAL);            // seems to help with stability, if you are doing other things in the loop this may not be needed

    // Check WiFi connection status
    if (WiFi.status() == WL_CONNECTED && !hasSetupWebsocket)
    {
        if (server_domain != "")
        {
            Serial.println("Setting up websocket to _01OS " + server_domain + ":" + server_port);

            websocket_setup(server_domain, server_port);
            InitI2SSpeakerOrMic(MODE_SPK);

            hasSetupWebsocket = true;

            Serial.println("Websocket connection flow completed");
        }
        else
        {
            Serial.println("No valid _01OS server address yet...");
        }
        // If connected, you might want to do something, like printing the IP address
        // Serial.println("Connected to WiFi!");
        // Serial.println("IP Address: " + WiFi.localIP().toString());
        // Serial.println("SSID " + WiFi.SSID());
    }
    if (WiFi.status() == WL_CONNECTED && hasSetupWebsocket)
    {
        button.loop();
        if (button.justPressed())
        {
            Serial.println("Recording...");
            webSocket.sendTXT("{\"role\": \"user\", \"type\": \"audio\", \"format\": \"bytes.raw\", \"start\": true}");
            InitI2SSpeakerOrMic(MODE_MIC);
            recording = true;
            data_offset = 0;
            Serial.println("Recording ready.");
        }
        else if (button.justReleased())
        {
            Serial.println("Stopped recording.");
            webSocket.sendTXT("{\"role\": \"user\", \"type\": \"audio\", \"format\": \"bytes.raw\", \"end\": true}");
            flush_microphone();
            recording = false;
            data_offset = 0;
        }
        else if (recording)
        {
            Serial.printf("Reading chunk at %d...\n", data_offset);
            size_t bytes_read;
            i2s_read(
                SPEAKER_I2S_NUMBER,
                (char *)(microphonedata0 + data_offset),
                DATA_SIZE, &bytes_read, (100 / portTICK_RATE_MS));
            data_offset += bytes_read;
            Serial.printf("Read %d bytes in chunk.\n", bytes_read);

            if (data_offset > 1024 * 9)
            {
                flush_microphone();
            }
        }

        M5.update();
        webSocket.loop();
    }
}