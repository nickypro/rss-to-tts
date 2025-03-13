# 1️⃣ Install dependencies silently
#!pip install -q kokoro>=0.8.4 soundfile
#!apt-get -qq -y install espeak-ng > /dev/null 2>&1

# 2️⃣ Initialize the pipeline
from kokoro import KPipeline
import torch
import numpy as np

# Create pipeline with American English
device = 'cuda' if torch.cuda.is_available() else 'cpu'
PIPELINE = KPipeline(lang_code='a', device=device)
VOICE_NAME = 'af_bella'  # Using the same voice as before

# 3️⃣ Generate function using the pipeline
from .split_text import split_text

def generate_default(text):
    split_texts = split_text(text)

    audio_chunks = []
    phonemes = None

    for t in split_texts:
        if not t or len(t) <= 1:
            continue

        try:
            # Generate audio for each chunk using the pipeline
            generator = PIPELINE(t, voice=VOICE_NAME, speed=1)

            # Process each generated segment
            for _, ps, audio in generator:
                audio_chunks.append(audio)
                if phonemes is None:
                    phonemes = ps  # Keep the first phoneme set as reference

                # Add a short pause between segments
                silence_duration = 0.15  # seconds
                sample_rate = 24000
                silence = np.zeros(int(silence_duration * sample_rate))
                audio_chunks.append(silence)

        except Exception as e:
            print(f"Error generating audio for text: {t}")
            print(f"Error: {e}")
            continue

    # Concatenate all audio chunks into a single numpy array
    if audio_chunks:
        concatenated_audio = np.concatenate(audio_chunks)
        return concatenated_audio, phonemes
    else:
        # Return empty array if no chunks
        return np.array([]), None

if __name__ == "__main__":
    text = "How could I know? It's an unanswerable question. Like asking an unborn child if they'll lead a good life. They haven't even been born."

    # Using the pipeline directly for testing
    generator = PIPELINE(text, voice=VOICE_NAME, speed=1)

    # Get the first (and only) generated segment
    for gs, ps, audio in generator:
        print(text)
        print(ps)

        # Save audio
        # Option 1: Save as WAV
        #import scipy.io.wavfile as wav
        #wav.write("output.wav", 24000, audio)

        # Option 2: Save as MP3 using soundfile
        import soundfile as sf
        sf.write("output.mp3", audio, 24000)
        break

