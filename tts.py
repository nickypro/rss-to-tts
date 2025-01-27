# 2️⃣ Remove model loading and keep just voice selection
VOICE_NAME = [
    'af', # Default voice is a 50-50 mix of Bella & Sarah
    'af_bella', 'af_sarah', 'am_adam', 'am_michael',
    'bf_emma', 'bf_isabella', 'bm_george', 'bm_lewis',
    'af_nicole', 'af_sky',
][1]
print(f'Selected voice: {VOICE_NAME}')

# 3️⃣ OpenAI client configuration
from openai import OpenAI
client = OpenAI(
    base_url="https://kokoro.nicky.pro/v1",
    api_key="not-needed"
)

def generate_default(text):
    response = client.audio.speech.create(
        model="kokoro",  # Not used but required for compatibility
        voice=VOICE_NAME,
        input=text,
        response_format="mp3"
    )
    return response

if __name__ == "__main__":
    text = "How could I know? It's an unanswerable question. Like asking an unborn child if they'll lead a good life. They haven't even been born."
    response = generate_default(text)
    print(text)

    print("type of response", type(response))

    # Save audio as MP3
    response.stream_to_file("output.mp3")

