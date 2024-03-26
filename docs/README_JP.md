[The 01 Project](https://twitter.com/hellokillian/status/1745875973583896950)の公式プレリリースリポジトリ。

> 発売まで残り**3**日

<h1 align="center">○</h1>

<p align="center">
    <a href="https://discord.gg/Hvz9Axh84z"><img alt="Discord" src="https://img.shields.io/discord/1146610656779440188?logo=discord&style=social&logoColor=black"/></a> <a href="https://0ggfznkwh4j.typeform.com/to/kkStE8WF"><img alt="Partner" src="https://img.shields.io/badge/become%20a%20partner-20B2AA?style=for-the-badge&color=black"/></a>
    <br>
    <br>
    <strong>オープンソースの言語モデルコンピューター</strong><br>
    <!-- <br><a href="https://openinterpreter.com">Lightを予約注文</a>‎ ‎ |‎ ‎ <a href="https://openinterpreter.com">最新情報を入手</a>‎ ‎ |‎ ‎ <a href="https://docs.openinterpreter.com/">ドキュメント</a><br> -->
</p>

<div align="center">

 | [日本語](README_JP.md) | [English](../README.md) |

</div>

<br>

![ポスター](https://pbs.twimg.com/media/GDqTVYzbgAIfLJf?format=png&name=4096x4096)

<br>

<!-- <p align="center">
今日は発売日です。私たちの<a href="https://changes.openinterpreter.com/log/the-new-computer-update">創業ステートメントを読む →</a>
</p>
<br> -->

```shell
git clone https://github.com/OpenInterpreter/01
cd 01/01OS
```

<!-- > うまくいかない場合は、私たちの[セットアップガイド](https://docs.openinterpreter.com/getting-started/setup)をお読みください。 -->

```shell
poetry install
poetry run 01
```

<br>

**The 01 Project**は、AIデバイス向けのエコシステムを構築しています。

私たちの主力オペレーティングシステムは、Rabbit R1、Humane Pin、[Star Trekコンピューター](https://www.youtube.com/watch?v=1ZXugicgn6U)のような会話型デバイスを動作させることができます。

私たちは、オープンソース、モジュール性、無料であり続けることを約束することで、この分野のGNU/Linuxになることを目指しています。

## 統一API

統一APIは、01で使用される主要サービスの標準的なPythonインターフェースです。

- `/stt` 音声認識用
- `/llm` 言語モデル用
- `/tts` 音声合成用

## ボディ

01OSは、さまざまなボディに収容できます。このリストに追加するPRを大歓迎します。

**01 Light**は、ESP32ベースの音声インターフェースで、インターネット経由でホームコンピューターを制御します。**01 Server**と組み合わせて使用します。

**01 Heavy**は、すべてをローカルで実行するデバイスです。

## セットアップ

### 依存関係のインストール

```bash
# MacOS
brew install portaudio ffmpeg cmake

# Ubuntu 
sudo apt-get install portaudio19-dev ffmpeg cmake
```

Whisperを使用してローカルで音声認識を行う場合は、Rustをインストールしてください。[ここ](https://www.rust-lang.org/tools/install)に記載されている手順に従ってください。

### 01 CLIのインストールと実行

```shell
pip install 01OS
```

```shell
01 --server # ハードウェアデバイスがリスンするサーバーを起動します。
```

# クライアントのセットアップ

### ESP32ボード用

[ESP32セットアップドキュメント](https://github.com/OpenInterpreter/01/tree/main/01OS/01OS/clients/esp32)をご覧ください。

### Mac、Windows、Ubuntuマシン用

```
01 # サーバーとクライアントを起動します。

01 --server --expose # サーバーを起動し、Ngrok経由で公開します。クライアントが接続するための`server_url`が表示されます。

01 --client --server_url your-server.com # クライアントのみを起動します。
```

### サービスプロバイダーの切り替え

01は、音声認識、音声合成、言語モデルのプロバイダーに依存しません。

以下のコマンドを実行して、プロバイダーを選択します。

```shell 
01 --tts-service openai
01 --llm-service openai 
01 --stt-service openai
```

[すべてのプロバイダーを見る ↗](https://docs.litellm.ai/docs/providers/)、または[サービスプロバイダーを追加して01チームに参加する。↗]()

### 01をローカルで実行する

一部のサービスプロバイダーはインターネット接続を必要としません。

次のコマンドを実行すると、ハードウェアに最適なプロバイダーをダウンロードして使用しようとします。

```shell
01 --local
```

## 仕組み

01は、言語モデル（音声インターフェースでラップされている）に`exec()`関数を装備し、コードを書いて実行してコンピューターを制御できるようにします。

音声はエンドユーザーのデバイスとの間でのみストリーミングされます。

# 貢献

詳細については、[コントリビューションガイドライン](docs/CONTRIBUTING.md)をご覧ください。

### 開発のためのセットアップ

```bash
# リポジトリをクローン
git clone https://github.com/KillianLucas/01.git

# 01OSディレクトリに移動
cd 01OS 

# Pythonの依存関係をインストール
poetry install

# 実行
poetry run 01  
```

<br>

# ロードマップ

01の未来を見るには、[私たちのロードマップ](https://github.com/KillianLucas/open-interpreter/blob/main/docs/ROADMAP.md)をご覧ください。

<br>

## 背景

### [コンテキスト ↗](https://github.com/KillianLucas/01/blob/main/CONTEXT.md)

01以前のデバイスの物語。

### [インスピレーション ↗](https://github.com/KillianLucas/01/tree/main/INSPIRATION.md)  

素晴らしいアイデアを盗みたいもの。

<br>

## 方向性

### [目標 ↗](https://github.com/KillianLucas/01/blob/main/GOALS.md)

私たちがやろうとしていること。

### [ユースケース ↗](https://github.com/KillianLucas/01/blob/main/USE_CASES.md)

01ができるようになること。

<br>