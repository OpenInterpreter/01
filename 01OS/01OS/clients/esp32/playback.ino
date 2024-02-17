/*Press button to record,released button to playback*/

#include <driver/i2s.h>
#include <M5Atom.h>

#define CONFIG_I2S_BCK_PIN 19
#define CONFIG_I2S_LRCK_PIN 33
#define CONFIG_I2S_DATA_PIN 22
#define CONFIG_I2S_DATA_IN_PIN 23

#define SPEAKER_I2S_NUMBER I2S_NUM_0

#define MODE_MIC 0
#define MODE_SPK 1
#define DATA_SIZE 1024

uint8_t microphonedata0[1024 * 70];
int data_offset = 0;

void InitI2SSpeakerOrMic(int mode) {
  esp_err_t err = ESP_OK;

  i2s_driver_uninstall(SPEAKER_I2S_NUMBER);
  i2s_config_t i2s_config = {
    .mode = (i2s_mode_t)(I2S_MODE_MASTER),
    .sample_rate = 16000,
    .bits_per_sample =
      I2S_BITS_PER_SAMPLE_16BIT,  // is fixed at 12bit, stereo, MSB
    .channel_format = I2S_CHANNEL_FMT_ALL_RIGHT,
#if ESP_IDF_VERSION > ESP_IDF_VERSION_VAL(4, 1, 0)
    .communication_format =
      I2S_COMM_FORMAT_STAND_I2S,  // Set the format of the communication.
#else                             // 设置通讯格式
    .communication_format = I2S_COMM_FORMAT_I2S,
#endif
    .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
    .dma_buf_count = 6,
    .dma_buf_len = 60,
  };
  if (mode == MODE_MIC) {
    i2s_config.mode =
      (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX | I2S_MODE_PDM);
  } else {
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

void setup() {
  M5.begin(true, false, true);
  M5.dis.drawpix(0, CRGB(128, 128, 0));
  delay(2000);
}

void loop() {
  if (M5.Btn.isPressed()) {
    data_offset = 0;
    InitI2SSpeakerOrMic(MODE_MIC);
    M5.dis.drawpix(0, CRGB(128, 128, 0));
    size_t byte_read;

    while (1) {
      i2s_read(SPEAKER_I2S_NUMBER,
               (char *)(microphonedata0 + data_offset), DATA_SIZE,
               &byte_read, (100 / portTICK_RATE_MS));
      data_offset += 1024;
      M5.update();
      if (M5.Btn.isReleased() || data_offset >= 71679) break;
      // delay(60);
    }
    size_t bytes_written;
    InitI2SSpeakerOrMic(MODE_SPK);
    i2s_write(SPEAKER_I2S_NUMBER, microphonedata0, data_offset,
              &bytes_written, portMAX_DELAY);
  }
  M5.update();
}