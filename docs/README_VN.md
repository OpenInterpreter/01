<h1 align="center">○</h1>

<p align="center">
    <a href="https://discord.gg/Hvz9Axh84z"><img alt="Discord" src="https://img.shields.io/discord/1146610656779440188?logo=discord&style=social&logoColor=black"/></a>
    <br>
    <br>
    <strong>Giao diện giọng nói (voice interface) mã nguồn mở số #1.</strong><br>
    <br><a href="https://changes.openinterpreter.com">Cập nhật mới nhất</a>‎ ‎ |‎ ‎ <a href="https://01.openinterpreter.com/">Tài liệu</a><br>
</p>

<br>

![OI-O1-BannerDemo-2](https://www.openinterpreter.com/OI-O1-BannerDemo-3.jpg)

Chúng tôi muốn hỗ trợ bạn phát triển ứng dụng. [Đăng ký hỗ trợ 1-1.](https://0ggfznkwh4j.typeform.com/to/kkStE8WF)

<br>

> [!QUAN TRỌNG]
> Dự án thử nghiệm này đang được phát triển khá nhanh và đang thiếu các bảo vệ cơ bản. Cho đến khi có bản phát hành `1.0` ổn định, bạn chỉ nên chạy repo này trên các thiết bị không có thông tin nhạy cảm hoặc quyền truy cập vào các dịch vụ phải trả phí.

<br>

**01** là nền tảng nguồn mở dành cho các thiết bị đàm thoại, lấy cảm hứng từ máy tính *Rabbit R1* và *Star Trek*.

Bằng cách xây dựng project này xoay quanh [Open Interpreter](https://github.com/OpenInterpreter/open-interpreter), **01** giờ đây tự nhiên, linh hoạt và sở hữu nhiều tiềm năng hơn nền tảng tiền nhiệm. Các trợ lý ảo được xây dựng từ repo này có thể:

- Thực thi code
- Duyệt web
- Đọc và tạo file
- Điều khiển các ứng dụng của bên thứ 3
- ...

<br>

Chúng tôi muốn trở thành một GNU/Linux của lĩnh vực mới này bằng cách duy trì mã nguồn mở theo hướng module và miễn phí như cách họ đã làm.

<br>

# Đối với phần mềm

```shell
git clone https://github.com/OpenInterpreter/01
cd 01/software
```

> Không cài đặt được? Hãy xem qua [hướng dẫn setup](https://01.openinterpreter.com/software/introduction).

```shell
brew install ffmpeg # Chỉ dành cho Mac. Cho Windows và Linux, hãy xem bên dưới.
poetry install
poetry run 01
```

<!-- > Để cài đặt trên Windows, hãy xem [hướng dẫn setup](https://docs.openinterpreter.com/getting-started/setup#windows). -->

<br>

**Lưu ý:**  Thư viện [RealtimeSTT](https://github.com/KoljaB/RealtimeSTT) và [RealtimeTTS](https://github.com/KoljaB/RealtimeTTS) là trái tim của 01, đồng thời là thành quả của [Kolja Beigel](https://github.com/KoljaB). Xin hãy tiếp tục đóng góp cho các repo đó và đừng quên tặng sao!

# Đối với phần cứng

**01** cũng là hub cho các thiết bị phần cứng chạy và kết nối tới phần mềm của chúng ta.

- Mac, Windows, và Linux đã được hỗ trợ, hãy chạy `poetry run 01`. [Server 01](https://01.openinterpreter.com/software/run) và client sử dụng nút `ctrl` để mô phỏng 01 Light.
- Ứng dụng Android và iOS đang trong quá trình phát triển [here](software/source/clients/mobile).
- 01 Light dựa trên ESP32, và là một giao diện nhấn-để-nói (push-to-talk interface). Tài liệu [ở đây.](https://01.openinterpreter.com/hardware/01-light/materials)
    - Hoạt động bằng cách kết nối với [Server 01](https://01.openinterpreter.com/software/run).

<br>

**Chúng tôi cần sự giúp đỡ của bạn để hỗ trợ và xây dựng thêm phần cứng.** 01 sẽ có thể chạy trên mọi thiết bị có đầu vào (micrô, bàn phím, v.v.), đầu ra (loa, màn hình, motor, v.v.) và với kết nối internet (hoặc tính toán đủ để chạy mọi thứ local). [Hướng dẫn đóng góp ↗️](https://github.com/OpenInterpreter/01/blob/main/CONTRIBUTING.md)

<br>

# Cách thức hoạt động

01 mở port websocket chuyển lời nói thành giọng nói (speech-to-speech) tại `localhost:10101`.

Nếu bạn truyền byte âm thanh thô (raw audio bytes) tới `/` trong [Streaming với định dạng LMC](https://docs.openinterpreter.com/guides/streaming-response), bạn sẽ nhận được phản hồi của nó ở cùng định dạng.

Dựa trên ý tưởng [Hệ điều hành LLM của Andrej Karpathy](https://twitter.com/karpathy/status/1723140519554105733), chúng ta chạy [mô hình ngôn ngữ thông dịch code (code-interpreting language model)](https://github.com/OpenInterpreter/open-interpreter), và gọi nó khi một event cụ thể xảy ra trên [kernel](https://github.com/OpenInterpreter/01/blob/main/software/source/server/utils/kernel.py) máy tính của bạn.

01 gói gọn nó trong một giao diện giọng nói (voice interface):

<br>

<img width="100%" alt="LMC" src="https://github.com/OpenInterpreter/01/assets/63927363/52417006-a2ca-4379-b309-ffee3509f5d4"><br><br>

# Các giao thức (Protocols)

## Thông báo LMC (LMC Messages)

Để giao tiếp với các thành phần khác nhau của hệ thống này, chúng tôi xin giới thiệu định dạng [Thông báo LMC (LMC Messages)](https://docs.openinterpreter.com/protocols/lmc-messages), thêm vào định dạng tin nhắn của OpenAI vai trò "computer":

https://github.com/OpenInterpreter/01/assets/63927363/8621b075-e052-46ba-8d2e-d64b9f2a5da9

## Thông báo hệ thống động (Dynamic System Messages)

Thông báo hệ thống động (Dynamic System Messages) cho phép bạn thực thi code bên trong thông báo hệ thống của LLM, ngay trước khi nó được xử lý với AI.

```python
# Chỉnh sửa các cài đặt dưới trong Profiles
interpreter.system_message = r" The time is {{time.time()}}. " # Mọi thứ trong ngoặc kép sẽ được thực thi dưới dạng Python
interpreter.chat("What time is it?") # Nó sẽ biết mà không cần gọi tool/API
```

# Hướng dẫn

## Server 01

Để chạy server trên Desktop và kết nối với 01 Light của bạn, chạy các lệnh sau:

```shell
brew install ngrok/ngrok/ngrok
ngrok authtoken ... # Sử dụng ngrok authtoken của bạn
poetry run 01 --server light --expose
```

Lệnh cuối cùng sẽ in URL máy chủ. Bạn có thể nhập thông tin này vào portal WiFi cố định của 01 Light để kết nối với Server 01 của bạn.

## Chạy trên Local 

```
poetry run 01 --profile local.py
```

## Tùy chỉnh

Để tùy chỉnh hoạt động của hệ thống, hãy chỉnh sửa [system message, model, skills library path,](https://docs.openinterpreter.com/settings/all-settings), v.v. trong folder `profiles` bên trong folder `server`. File này thiết lập một trình thông dịch (interpreter) và được hỗ trợ bởi Open Interpreter.

Để chỉ định dịch vụ chuyển văn bản thành giọng nói (text-to-speech) cho 01 `base_device.py`, hãy chỉnh sửa `interpreter.tts` thành "openai" cho OpenAI, "elevenlabs" cho ElevenLabs hoặc "coqui" cho Coqui (local) trong profile. Đối với 01 Light, chỉnh sửa `SPEAKER_SAMPLE_RATE` trong `client.ino` trong thư mục máy khách (client directory) `esp32` thành 24000 cho Coqui (cục bộ) hoặc 22050 cho OpenAI TTS. Hiện tại chúng tôi không hỗ trợ ElevenLabs TTS trên 01 Light.

## Package cần cài đặt (Ubuntu Dependencies)

```bash
sudo apt-get install ffmpeg
```

# Đóng góp

[![Những người đã đóng góp cho 01](https://contrib.rocks/image?repo=OpenInterpreter/01&max=2000)](https://github.com/OpenInterpreter/01/graphs/contributors)

Xin hãy xem qua [hướng dẫn đóng góp](CONTRIBUTING.md) để biết thêm chi tiết và cách tham gia.

<br>

## Directory

### [Context ↗](https://github.com/KillianLucas/01/blob/main/CONTEXT.md)

Tiêu chuẩn của 01.

### [Roadmap ↗](/ROADMAP.md)

Kế hoạch tương lai của 01.

<br>

○
