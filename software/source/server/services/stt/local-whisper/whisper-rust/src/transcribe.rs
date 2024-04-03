use whisper_rs::{FullParams, SamplingStrategy, WhisperContext, WhisperContextParameters};
use std::path::PathBuf;


/// Transcribes the given audio file using the whisper-rs library.
///
/// # Arguments
/// * `model_path` - Path to Whisper model file
/// * `file_path` - A string slice that holds the path to the audio file to be transcribed.
///
/// # Returns
///
/// A Result containing a String with the transcription if successful, or an error message if not.
pub fn transcribe(model_path: &PathBuf, file_path: &PathBuf) -> Result<String, String> {

    let model_path_str = model_path.to_str().expect("Not valid model path");
    // Load a context and model
    let ctx = WhisperContext::new_with_params(
        model_path_str, // Replace with the actual path to the model
        WhisperContextParameters::default(),
    )
    .map_err(|_| "failed to load model")?;

    // Create a state
    let mut state = ctx.create_state().map_err(|_| "failed to create state")?;

    // Create a params object
    // Note that currently the only implemented strategy is Greedy, BeamSearch is a WIP
    let mut params = FullParams::new(SamplingStrategy::Greedy { best_of: 1 });

    // Edit parameters as needed
    params.set_n_threads(1); // Set the number of threads to use
    params.set_translate(true); // Enable translation
    params.set_language(Some("en")); // Set the language to translate to English
    // Disable printing to stdout
    params.set_print_special(false);
    params.set_print_progress(false);
    params.set_print_realtime(false);
    params.set_print_timestamps(false);

    // Load the audio file
    let audio_data = std::fs::read(file_path)
        .map_err(|e| format!("failed to read audio file: {}", e))?
        .chunks_exact(2)
        .map(|chunk| i16::from_ne_bytes([chunk[0], chunk[1]]))
        .collect::<Vec<i16>>();

    // Convert the audio data to the required format (16KHz mono i16 samples)
    let audio_data = whisper_rs::convert_integer_to_float_audio(&audio_data);

    // Run the model
    state.full(params, &audio_data[..]).map_err(|_| "failed to run model")?;

    // Fetch the results
    let num_segments = state.full_n_segments().map_err(|_| "failed to get number of segments")?;
    let mut transcription = String::new();
    for i in 0..num_segments {
        let segment = state.full_get_segment_text(i).map_err(|_| "failed to get segment")?;
        transcription.push_str(&segment);
        transcription.push('\n');
    }

    Ok(transcription)
}
