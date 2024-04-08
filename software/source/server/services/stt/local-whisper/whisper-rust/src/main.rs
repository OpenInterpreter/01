mod transcribe;

use clap::Parser;
use std::path::PathBuf;
use transcribe::transcribe;

#[derive(Parser, Debug)]
#[command(author, version, about, long_about = None)]
struct Args {
    /// This is the model for Whisper STT
    #[arg(short, long, value_parser, required = true)]
    model_path: PathBuf,

    /// This is the wav audio file that will be converted from speech to text
    #[arg(short, long, value_parser, required = true)]
    file_path: Option<PathBuf>,
}

fn main() {

    let args = Args::parse();

    let file_path = match args.file_path {
        Some(fp) => fp,
        None => panic!("No file path provided")
    };

    let result = transcribe(&args.model_path, &file_path);

    match result {
        Ok(transcription) => print!("{}", transcription),
        Err(e) => panic!("Error: {}", e),
    }
}
