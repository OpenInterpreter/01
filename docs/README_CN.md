<h1 align="center">○</h1>

<p align="center">
    <a href="https://discord.gg/Hvz9Axh84z"><img alt="Discord" src="https://img.shields.io/discord/1146610656779440188?logo=discord&style=social&logoColor=black"/></a>
    <br>
    <br>
    <strong>The open-source language model computer.（开源大语言模型计算机）</strong><br>
    <br><a href="https://openinterpreter.com/01">预订 Light‎</a>‎ ‎ |‎ ‎ <a href="https://changes.openinterpreter.com">获取更新‎</a>‎ ‎ |‎ ‎ <a href="https://01.openinterpreter.com/">文档</a><br>
</p>

<br>

![OI-O1-BannerDemo-2](https://www.openinterpreter.com/OI-O1-BannerDemo-3.jpg)

我们想帮助您构建。 [申请 1 对 1 的支持。](https://0ggfznkwh4j.typeform.com/to/kkStE8WF)

<br>

---

⚠️ **警告：** 这个实验性项目正在快速开发中，并且缺乏基本的安全保障。在稳定的 1.0 版本发布之前， **仅在**没有敏感信息或访问付费服务的设备上运行此存储库。⚠️

---

<br>

**01 项目** 正在构建一个用于 AI 设备的开源生态系统。

我们的旗舰操作系统可以为对话设备提供动力，比如 Rabbit R1、Humane Pin 或 [Star Trek computer](https://www.youtube.com/watch?v=1ZXugicgn6U)。

我们打算成为这个领域的 GNU/Linux，保持开放、模块化和免费。

<br>

# 软件

```shell
git clone https://github.com/OpenInterpreter/01 # Clone the repository
cd 01/software # CD into the source directory
```

<!-- > 不起作用？阅读我们的[安装指南](https://docs.openinterpreter.com/getting-started/setup)。 -->

```shell
brew install portaudio ffmpeg cmake # Install Mac OSX dependencies
poetry install # Install Python dependencies
export OPENAI_API_KEY=sk... # OR run `poetry run 01 --local` to run everything locally
poetry run 01 # Runs the 01 Light simulator (hold your spacebar, speak, release)
```

<!-- > 对于Windows安装，请阅读我们的[专用安装指南](https://docs.openinterpreter.com/getting-started/setup#windows)。 -->

<br>

# 硬件

- **01 Light** 是基于 ESP32 的语音接口。 [构建说明在这里。](https://github.com/OpenInterpreter/01/tree/main/hardware/light) 它与运行在你家庭电脑上的 **01 Server** ([下面有设置指南](https://github.com/OpenInterpreter/01/blob/main/README.md#01-server)) 配合使用。
- **Mac OSX** and **Ubuntu** 支持通过运行 `poetry run 01`。 这会使用你的空格键来模拟 01 Light。
- （即将推出） **01 Heavy** 是一个独立设备，可以在本地运行所有功能。

**我们需要您的帮助来支持和构建更多硬件。** 01 应该能够在任何具有输入（麦克风、键盘等）、输出（扬声器、屏幕、电机等）和互联网连接（或足够的计算资源以在本地运行所有内容）的设备上运行。 [ 贡献指南 →](https://github.com/OpenInterpreter/01/blob/main/CONTRIBUTING.md)

<br>

# 它是做什么的？

01 在 `localhost:10001` 上暴露了一个语音到语音的 WebSocket。

如果你以 [LMC 格式](https://docs.openinterpreter.com/protocols/lmc-messages) 将原始音频字节流传送到 `/`，你将会以相同的格式收到其回复。

受 [Andrej Karpathy's LLM OS](https://twitter.com/karpathy/status/1723140519554105733) 的启发，我们运行了一个 [code-interpreting language model](https://github.com/OpenInterpreter/open-interpreter)，并在你的计算机 [ 内核 ](https://github.com/OpenInterpreter/01/blob/main/01OS/01OS/server/utils/kernel.py) 发生某些事件时调用它。

01 将其包装成一个语音界面：

<br>

<img width="100%" alt="LMC" src="https://github.com/OpenInterpreter/01/assets/63927363/52417006-a2ca-4379-b309-ffee3509f5d4"><br><br>

# 协议

## LMC 消息

为了与系统的不同组件进行通信，我们引入了 [LMC 消息](https://docs.openinterpreter.com/protocols/lmc-messages) 格式，它扩展了 OpenAI 的消息格式以包含一个 "computer" 角色：

https://github.com/OpenInterpreter/01/assets/63927363/8621b075-e052-46ba-8d2e-d64b9f2a5da9

## 动态系统消息

动态系统消息使您能够在 LLM 系统消息出现在 AI 前的片刻内执行代码。

```python
# Edit the following settings in i.py
interpreter.system_message = r" The time is {{time.time()}}. " # Anything in double brackets will be executed as Python
interpreter.chat("What time is it?") # It will know, without making a tool/API call
```

# 指南

## 01 服务器

要在您的桌面上运行服务器并将其连接到您的 01 Light，请运行以下命令：

```shell
brew install ngrok/ngrok/ngrok
ngrok authtoken ... # Use your ngrok authtoken
poetry run 01 --server --expose
```

最后一个命令将打印一个服务器 URL。您可以将其输入到您的 01 Light 的 captive WiFi 门户中，以连接到您的 01 服务器。

## 本地模式

```
poetry run 01 --local
```

如果您想要使用 Whisper 运行本地语音转文本，您必须安装 Rust。请按照 [这里](https://www.rust-lang.org/tools/install) 给出的说明进行操作。

## 自定义

要自定义系统的行为，请编辑 `i.py` 中的 [系统消息、模型、技能库路径](https://docs.openinterpreter.com/settings/all-settings) 等。这个文件设置了一个解释器，并由 Open Interpreter 提供支持。

## Ubuntu 依赖项

```bash
sudo apt-get install portaudio19-dev ffmpeg cmake
```

# 贡献者

[![01 project contributors](https://contrib.rocks/image?repo=OpenInterpreter/01&max=2000)](https://github.com/OpenInterpreter/01/graphs/contributors)

请查看我们的 [贡献指南](CONTRIBUTING.md) 以获取更多的参与详情。

<br>

# 路线图

访问 [我们的路线图](/ROADMAP.md) 以了解 01 的未来。

<br>

## 背景

### [背景说明 ↗](https://github.com/KillianLucas/01/blob/main/CONTEXT.md)

关于 01 之前设备的故事。

### [灵感来源 ↗](https://github.com/KillianLucas/01/tree/main/INSPIRATION.md)

我们想要从中获取优秀想法的事物。

<br>

○
