<h1 align="center">○</h1>

<p align="center">
    <a href="https://discord.gg/Hvz9Axh84z"><img alt="Discord" src="https://img.shields.io/discord/1146610656779440188?logo=discord&style=social&logoColor=black"/></a>
    <br>
    <br>
    <strong>オープンソースの言語モデルコンピュータ。</strong><br>
    <br><a href="https://openinterpreter.com/01">Light の予約</a>‎ ‎ |‎ ‎ <a href="https://changes.openinterpreter.com">最新情報</a>‎ ‎ |‎ ‎ <a href="https://01.openinterpreter.com/">ドキュメント</a><br>
</p>

<br>

![OI-O1-BannerDemo-2](https://www.openinterpreter.com/OI-O1-BannerDemo-3.jpg)

あなたのビルドをサポートします。[1対1のサポートを申し込む。](https://0ggfznkwh4j.typeform.com/to/kkStE8WF)

<br>

> [!IMPORTANT]
> この実験的なプロジェクトは急速に開発が進んでおり、基本的な安全策が欠けています。安定した `1.0` リリースまでは、機密情報や有料サービスへのアクセスがないデバイスでのみこのリポジトリを実行してください。
>
> **これらの懸念やその他の懸念に対処するための大幅な書き換えが[ここ](https://github.com/KillianLucas/01-rewrite/tree/main)で行われています。**

<br>

**01 プロジェクト** は、AI 機器のためのオープンソースのエコシステムを構築しています。

私たちの主力オペレーティングシステムは、Rabbit R1、Humane Pin、[Star Trek computer](https://www.youtube.com/watch?v=1ZXugicgn6U) のような会話デバイスを動かすことができます。

私たちは、オープンでモジュラーでフリーであり続けることで、この分野の GNU/Linux になるつもりです。

<br>

# ソフトウェア

```shell
git clone https://github.com/OpenInterpreter/01 # リポジトリのクローン
cd 01/software # CD でソースディレクトリに移動
```

<!-- > うまくいきませんか？[セットアップガイド](https://docs.openinterpreter.com/getting-started/setup)をお読みください。 -->

```shell
brew install portaudio ffmpeg cmake # Mac OSXの依存関係のインストール
poetry install # Pythonの依存関係のインストール
export OPENAI_API_KEY=sk... # または、`poetry run 01 --local` を実行し、ローカルですべてを実行
poetry run 01 # 01 Light シミュレーターを作動させる（スペースバーを押しながら話し、放す）
```

<!-- > Windows のインストールについては、[セットアップガイド](https://docs.openinterpreter.com/getting-started/setup#windows)をお読みください。 -->

<br>

# ハードウェア

- **01 Light** は ESP32 ベースの音声インターフェースです。ビルド手順は[こちら](https://github.com/OpenInterpreter/01/tree/main/hardware/light)。買うべきもののリストは[こちら](https://github.com/OpenInterpreter/01/blob/main/hardware/light/BOM.md)。
- ご自宅のコンピューターで動作している **01 サーバー**（[下記のセットアップガイド](https://github.com/OpenInterpreter/01/blob/main/README.md#01-server)）と連動して動作します。
- **Mac OSX** と **Ubuntu** は `poetry run 01` を実行することでサポートされます（**Windows** は実験的にサポートされている）。これはスペースキーを使って 01 Light をシミュレートします。
- (近日発表) **01 Heavy** は、ローカルですべてを実行するスタンドアローンデバイスです。

**より多くのハードウェアをサポートし、構築するためには、皆さんの協力が必要です。** 01 は、入力（マイク、キーボードなど）、出力（スピーカー、スクリーン、モーターなど）、インターネット接続（またはローカルですべてを実行するのに十分な計算能力）があれば、どのようなデバイスでも実行できるはずです。[コントリビューションガイド →](https://github.com/OpenInterpreter/01/blob/main/CONTRIBUTING.md)

<br>

# 何をするのか？

01 は、`localhost:10001` で音声合成ウェブソケットを公開しています。

生のオーディオバイトを[ストリーミング LMC フォーマット](https://docs.openinterpreter.com/guides/streaming-response)で `/` にストリーミングすると、同じフォーマットで応答を受け取ります。

[Andrej Karpathy の LLM OS](https://twitter.com/karpathy/status/1723140519554105733) に一部インスパイアされ、[コード解釈言語モデル](https://github.com/OpenInterpreter/open-interpreter)を実行し、コンピュータの[カーネル](https://github.com/OpenInterpreter/01/blob/main/software/source/server/utils/kernel.py)で特定のイベントが発生したときにそれを呼び出します。

01 はこれを音声インターフェースで包んでいます:

<br>

<img width="100%" alt="LMC" src="https://github.com/OpenInterpreter/01/assets/63927363/52417006-a2ca-4379-b309-ffee3509f5d4"><br><br>

# プロトコル

## LMC メッセージ

このシステムのさまざまなコンポーネントと通信するために、[LMC メッセージ](https://docs.openinterpreter.com/protocols/lmc-messages)フォーマットを導入します。これは、OpenAI のメッセージフォーマットを拡張し、"computer" の役割を含むようにしたものです:

https://github.com/OpenInterpreter/01/assets/63927363/8621b075-e052-46ba-8d2e-d64b9f2a5da9

## ダイナミックシステムメッセージ

ダイナミックシステムメッセージは、LLM のシステムメッセージが AI に表示される一瞬前に、その中でコードを実行することを可能にします。

```python
# i.py の以下の設定を編集
interpreter.system_message = r" The time is {{time.time()}}. " # 二重括弧の中は Python として実行されます
interpreter.chat("What time is it?") # ツール/API を呼び出すことなく、次のことが分かります
```

# ガイド

## 01 サーバー

デスクトップ上でサーバーを起動し、01 Light に接続するには、以下のコマンドを実行します:

```shell
brew install ngrok/ngrok/ngrok
ngrok authtoken ... # ngrok authtoken を使用
poetry run 01 --server --expose
```

最後のコマンドは、サーバーの URL を表示します。これを 01 Light のキャプティブ WiFi ポータルに入力すると、01 Server に接続できます。

## ローカルモード

```
poetry run 01 --local
```

Whisper を使ってローカル音声合成を実行したい場合、Rust をインストールする必要があります。[こちら](https://www.rust-lang.org/tools/install)の指示に従ってください。

## カスタマイズ

システムの動作をカスタマイズするには、`i.py` 内の[システムメッセージ、モデル、スキルライブラリのパス](https://docs.openinterpreter.com/settings/all-settings)などを編集します。このファイルはインタープリターをセットアップするもので、Open Interpreter によって動作します。

## Ubuntu 依存関係

```bash
sudo apt-get install portaudio19-dev ffmpeg cmake
```

# コントリビューター

[![01 project contributors](https://contrib.rocks/image?repo=OpenInterpreter/01&max=2000)](https://github.com/OpenInterpreter/01/graphs/contributors)

参加方法の詳細については、[コントリビューションガイド](/CONTRIBUTING.md)をご覧ください。

<br>

# ロードマップ

01 の未来を見るには、[私達のロードマップ](/ROADMAP.md)をご覧ください。

<br>

## バックグラウンド

### [コンテキスト ↗](https://github.com/KillianLucas/01/blob/main/CONTEXT.md)

01 以前のデバイスの物語。

### [インスピレーション ↗](https://github.com/KillianLucas/01/tree/main/INSPIRATION.md)

素晴らしいアイデアは盗みたいと思うもの。

<br>

○
