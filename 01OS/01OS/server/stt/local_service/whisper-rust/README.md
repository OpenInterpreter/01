# Setup

To rebuild the `whisper-rust` executable, do the following:

1. Install [Rust](https://www.rust-lang.org/tools/install), cmake, and Python dependencies `pip install -r requirements.txt`.
2. Go to **core/stt** and run `cargo build --release`.
3. Move the `whisper-rust` executable from target/release to this directory.
