# 1️⃣ Install dependencies silently
#!git lfs install
#!git clone https://huggingface.co/hexgrad/Kokoro-82M
#%cd Kokoro-82M
#!apt-get -qq -y install espeak-ng > /dev/null 2>&1
#!pip install -q phonemizer torch transformers scipy munch

# 2️⃣ Build the model and load the default voicepack
from kokoro.models import build_model
import torch
device = 'cuda' if torch.cuda.is_available() else 'cpu'
MODEL = build_model('./kokoro/kokoro-v0_19.pth', device)
VOICE_NAME = [
    'af', # Default voice is a 50-50 mix of Bella & Sarah
    'af_bella', 'af_sarah', 'am_adam', 'am_michael',
    'bf_emma', 'bf_isabella', 'bm_george', 'bm_lewis',
    'af_nicole', 'af_sky',
][1]
VOICEPACK = torch.load(f'./kokoro/voices/{VOICE_NAME}.pt', weights_only=True).to(device)
print(f'Loaded voice: {VOICE_NAME}')

# 3️⃣ Call generate, which returns 24khz audio and the phonemes used
from kokoro.kokoro import generate

def generate_default(text):
    audio, out_ps = generate(MODEL, text, VOICEPACK, lang=VOICE_NAME[0])
    return audio, out_ps

if __name__ == "__main__":
    text = "How could I know? It's an unanswerable question. Like asking an unborn child if they'll lead a good life. They haven't even been born."
    audio, out_ps = generate(MODEL, text, VOICEPACK, lang=VOICE_NAME[0])
    # Language is determined by the first letter of the VOICE_NAME:
    # 🇺🇸 'a' => American English => en-us
    # 🇬🇧 'b' => British English => en-gb
    print(text)
    print(out_ps)

    # Save audio
    # Option 1: Save as WAV (most basic and reliable)
    import scipy.io.wavfile as wav
    wav.write("output.wav", 24000, audio)

    # Option 2: Save as MP3 using soundfile (if audio is float)
    import soundfile as sf
    sf.write("output.mp3", audio, 24000)

