import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from .parallel import exponential_backoff, process_in_parallel

load_dotenv("./env")

default_prompt_question = """
\n\n--- END OF TEXT BLOCK ---

The above is a chunk of text from an article. Please convert, word-by-word into an idential text chunk, but converted into a format that can be read using text-to-speech.

- Convert any math into the equivalent in written English (e.g: \frac{1}{2} -> 'one over two')
- Convert html unicode into relevant symbols if possible (it&#x2019;s -> it's. &#8217; -> ’, etc...).
- REMOVE any artifacts such as html tags like <p> or <h2>, or long links.
- REMOVE long html strings, such as <form class=\"subscription-widget-subscribe\">, replace with ''
- Replace links with '[link in text]'
- If the above does not seem to be part of a text, simply return ''

Do NOT repeat the instructions or reasoning. Return ONLY the processed text block, upto but NOT including --- END OF TEXT BLOCK ---. You may begin your final answer now:
"""

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=os.getenv("OPENROUTER_API_KEY"),
)

#MODEL = "google/gemini-flash-1.5-8b"
#MODEL = "thedrummer/unslopnemo-12b"
#MODEL = "meta-llama/llama-3.3-70b-instruct"
MODEL = "qwen/qwq-32b"
#MODEL = "google/gemma-3-27b-it:free"

DO_LOGGING = True
LOG_FILE = "data/article-parsing.log"

@exponential_backoff
def raw_completion(text):
    completion = client.chat.completions.create(
      model=MODEL,
      messages=[
        {
          "role": "user",
          "content": [
            {
              "type": "text",
              "text": text,
            },
          ]
        }
      ]
    )
    return completion.choices[0].message.content

def split_into_blocks(text, block_size=2_000):
    blocks = []
    current_block = ""
    for line in text.split("\n"):
        if len(current_block) + len(line) + 1 > block_size:
            blocks.append(current_block)
            current_block = line + "\n"
        else:
            current_block += line + "\n"
    if current_block:
        blocks.append(current_block)
    return blocks

def get_completion(text, prompt_question=default_prompt_question):
    blocks = split_into_blocks(text)
    processed_blocks = process_in_parallel(
        blocks,
        lambda block: raw_completion(block + prompt_question)
    )
    if DO_LOGGING:
        data = [{"orig": b, "parsed": o} for (b, o) in zip(blocks, processed_blocks)]
        with open(LOG_FILE, "a") as f:
            f.write(json.dumps(data, indent=2))
    return "\n".join(processed_blocks)

get_parallel = get_completion

if __name__ == "__main__":
    print(raw_completion("Hello! What is 3 squared?"))
    print(get_completion("Hello! What is 3 squared?"))
