
# Setup

1. Install [Rust](https://www.rust-lang.org/tools/install) and Python dependencies `pip install -r requirements.txt`.
2. Go to **core/stt** and run `cargo build --release`.
3. Download GGML Whisper model from [Huggingface](https://huggingface.co/ggerganov/whisper.cpp).
4. In core, copy `.env.example` to `.env` and put the path to model.
5. Run `python core/i_endpoint.py` to start the server.
6. Run `python core/test_cli.py PATH_TO_FILE` to test sending audio to service and getting transcription back over websocket.