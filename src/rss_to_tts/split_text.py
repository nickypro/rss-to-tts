

TEXT_MAX_CHARS = 300

def split_text(text):
    # must be max 512 tokens, so approx like 1k characters
    # First split by paragraphs
    paragraphs = [p for p in text.split("\n\n") if p.strip()]

    split_texts = []
    for paragraph in paragraphs:
        if len(paragraph) <= TEXT_MAX_CHARS:
            split_texts.append(paragraph)
        else:
            # Split long paragraphs by sentences
            sentences = []
            for sent in paragraph.replace("\n", " ").split(". "):
                if sent:
                    sentences.append(sent + ("." if not sent.endswith(".") else ""))

            current_chunk = ""
            for sentence in sentences:
                if len(current_chunk) + len(sentence) <= TEXT_MAX_CHARS:
                    current_chunk += sentence + " " if current_chunk else sentence
                else:
                    # If a single sentence is too long, split by other punctuation
                    if not current_chunk:
                        chunks = split_by_punctuation(sentence, TEXT_MAX_CHARS)
                        split_texts.extend(chunks)
                    else:
                        split_texts.append(current_chunk.strip())
                        current_chunk = sentence

            if current_chunk:
                split_texts.append(current_chunk.strip())

    return split_texts

def split_by_punctuation(text, max_length):
    """Split text by punctuation marks if possible, otherwise by words or characters."""
    if len(text) <= max_length:
        return [text]

    chunks = []
    punctuation = [',', ';', ':', '-', ')', '(', '"', "'"]

    current_chunk = ""
    for char in text:
        current_chunk += char

        # Try to split at punctuation when approaching max length
        if len(current_chunk) > max_length * 0.7 and char in punctuation:
            chunks.append(current_chunk)
            current_chunk = ""
        # Force split if we're at max length
        elif len(current_chunk) >= max_length:
            # Try to split at word boundaries
            words = current_chunk.split()
            if len(words) > 1:
                # Keep most words in the current chunk
                split_point = max(1, len(words) - 1)
                chunks.append(" ".join(words[:split_point]))
                current_chunk = " ".join(words[split_point:])
            else:
                # If a single word is too long, just split at max_length
                chunks.append(current_chunk)
                current_chunk = ""

    if current_chunk:
        chunks.append(current_chunk)

    return chunks