# TripTok

[(Versión en español)](https://github.com/ikkani/TripTok/blob/main/README-es.md)

**TripTok** is a Python project that:

1️⃣ Locates and downloads all videos and their information (title, description, etc.).

2️⃣ Transcribes the audio of each video.

3️⃣ Uses an agent to:

   - Detect the entities mentioned in each video.
   - Summarize what is said about each entity.
   - Search for additional information on the internet.
   - Generate an extended summary using that external information.

4️⃣ Outputs all the information into a clear, readable, and organized CSV file.

> ⚠️ **Legal notice**: Scraping and downloading TikTok content may violate its Terms of Service and/or copyright laws. Use this project for research or educational purposes only, and at your own risk.

---

## Requirements

* Python 3.9
* Google Chrome installed
* [ChromeDriver](https://chromedriver.chromium.org/) compatible with your Chrome version
* Dedicated GPU capable of running small LLMs and OpenAI Whisper

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Tech Stack

 - [Selenium](https://pypi.org/project/selenium/) for scraping TikTok videos.
 - [OpenAI Whisper](https://github.com/openai/whisper) for audio transcription.
 - [SearXNG](https://github.com/searxng/searxng) as a web search engine.
 - [Llama.cpp](https://github.com/ggml-org/llama.cpp) to run a local LLM (Qwen3 4B 2507) used by the agent.

## Project Structure

```
TripTok/
├── agent/               # LLM Agent (LangGraph + LangChain)
├── audio_to_text/       # Audio-to-text with Whisper
├── tiktok_scraping/     # Scrapers for collections and videos
├── data/                # Saved metadata
├── downloads/           # Downloaded videos
├── transcripts/         # Transcriptions
├── results/             # Combined results
├── main.py              # Main entry script
└── requirements.txt
```

---

## Initial Setup

### 1. ChromeDriver

By default, the code expects `chromedriver` at:

```
C://chromedriver-win64//chromedriver.exe
```

### 2. Required Local Services (for the agent)

* **LLM**: the agent uses `http://127.0.0.1:1234/v1` as an endpoint. You must have a local LLM running with an API compatible with OpenAI (e.g., [Ollama](https://ollama.ai), [LM Studio](https://lmstudio.ai), or [llama.cpp](https://github.com/ggml-org/llama.cpp)).
* **Web Search**: a [SearXNG](https://github.com/searxng/searxng) instance is expected at `http://localhost:8080/search` returning JSON results. If unavailable, disable the agent or implement a stub.
* **Prompts**: the agent loads prompts from `./prompts/*.txt` (`ner_prompt.txt`, `video_summarize_prompt.txt`).

---

## Usage

Run the main script with the parameter `--first-step` to specify from which step to start. If omitted, the full pipeline will run.

### 1. Scrape URLs from a TikTok collection

```bash
python main.py --first-step download-url
```

This will open a browser, load the collection set in `COLLECTION_URL`, and save the URLs to `tiktok_urls.json`.

### 2. Download videos and metadata

```bash
python main.py --first-step download-videos
```

This will process the URLs in `tiktok_urls.json` and save videos to `./downloads` and metadata to `./data`.

### 3. Transcribe videos

```bash
python main.py --first-step transcript
```

This will generate `.txt` transcription files in `./transcripts`.

### 4. Run the agent

```bash
python main.py --first-step agent
```

This processes video descriptions + transcripts with the LLM agent.

### 5. Clean / merge results

```bash
python main.py --first-step data-cleaning
```

This combines and cleans results into a final CSV in `./results`.

---

## ToDo's

* Parameterize ChromeDriver path automatically.
* Add error/captcha handling in scrapers.
* Make the scraper more robust against TikTok DOM changes.
* Improve and refine the agent.

---

## Credits

Project created by [ikkani](https://github.com/ikkani).
