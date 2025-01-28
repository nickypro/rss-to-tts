import os
from dotenv import load_dotenv
from openai import OpenAI
from parallel import exponential_backoff, process_in_parallel

load_dotenv("./env")

default_prompt_question = "\n\n---\n\n The above is a chunk of text from an article. Please convert, word-by-word into an idential text chunk, but converted into a format that can be read using text-to-speech. Convert any math into the equivalent in written English (e.g: \frac{1}{2} -> 'one over two') and html code into relevant symbols if possible (it&#x2019;s -> '). REMOVE any artifacts such as html tags like <p> or <h2>. If the above does not seem to be part of a text, simply return '' "

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=os.getenv("OPENROUTER_API_KEY"),
)

@exponential_backoff
def raw_completion(text):
    completion = client.chat.completions.create(
      model="google/gemini-flash-1.5-8b",
      max_tokens=500_000,
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

def split_into_blocks(text, block_size=10_000):
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
    return "\n".join(processed_blocks)

get_parallel = get_completion

if __name__ == "__main__":
    print(raw_completion("Hello! What is 3 squared?"))
    print(get_completion("Hello! What is 3 squared?"))
