# rss-to-tts

A tool to convert RSS feeds to TTS audio podcast feeds.

## Setup

You need to have poetry and git installed.

```
git clone https://github.com/nicky-pro/rss-to-tts.git
cd rss-to-tts
poetry install
```

## Usage

### Configure feeds

Edit the `config.json` file to add/remove feeds.

### Convert RSS feeds to TTS audio

```
# convert RSS feeds to TTS audio
poetry run python rss_to_tts.process_feed

# generate RSS feed
poetry run python rss_to_tts.generate_rss
```

### Serve the RSS feed

Serve the rss feed using a static file server. I recommend nginx for this.



