import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv("./env")

default_prompt_question = "\n\n---\n\n The above is a chunk of text from an article. Please convert, word-by-word into an idential text chunk, but converted into a format that can be read using text-to-speech. Convert any math into the equivalent in written English (e.g: \frac{1}{2} -> 'one over two') and html code into relevant symbols if possible (it&#x2019;s -> '). REMOVE any artifacts such as html tags like <p> or <h2>. If the above does not seem to be part of a text, simply return '' "


client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=os.getenv("OPENROUTER_API_KEY"),
)

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
    input_blocks = split_into_blocks(text)
    output = ""
    for block in input_blocks:
        output += raw_completion(block + prompt_question)
    return output

import time
import concurrent.futures

def exponential_backoff(func, max_retries=5, initial_delay=1, backoff_factor=2):
    """
    A wrapper function to implement exponential backoff for retries.
    """
    def wrapper(*args, **kwargs):
        retries = 0
        delay = initial_delay
        while retries < max_retries:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                retries += 1
                if retries == max_retries:
                    print(f"Max retries reached. Error: {e}")
                    raise
                print(f"Retry {retries}/{max_retries}. Waiting {delay} seconds...")
                time.sleep(delay)
                delay *= backoff_factor  # Exponential increase in delay
    return wrapper

import concurrent.futures

def get_parallel(text, prompt_question=default_prompt_question, max_workers=10):
    """
    Main function to split text into blocks and process them in parallel.
    Returns the results in the original order of the blocks.
    """
    input_blocks = split_into_blocks(text)
    output = [None] * len(input_blocks)  # Pre-allocate a list to store results in order

    def process_block(block, index):
        """ Processes a block and returns its result along with its original index. """
        try:
            result = raw_completion(block + prompt_question)
            return index, result
        except Exception as e:
            print(f"Error processing block {index}: {e}")
            return index, None  # Return None for failed blocks

    # Use ThreadPoolExecutor for parallel processing
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit tasks with both the block and its index
        futures = [executor.submit(process_block, block, idx) for idx, block in enumerate(input_blocks)]

        # Collect results in the order they complete
        for future in concurrent.futures.as_completed(futures):
            idx, result = future.result()
            if result is not None:
                output[idx] = result  # Place the result in the correct position

    # Combine the results in the original order
    return "\n".join([result for result in output if result is not None])


if __name__ == "__main__":
    print(raw_completion("Hello! What is 3 squared?"))
    print(get_parallel("Hello! What is 3 squared?"))

