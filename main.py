import json
import argparse
import os
import pandas as pd

from collections import defaultdict
from tiktok_scraping.tiktok_collection_scraper import TikTokCollectionScraper
from tiktok_scraping.tiktok_video_scraper import TikTokVideoScraper
from audio_to_text.audio_to_text import transcribe_videos
from agent.agent import app

# Config
COLLECTION_URL = "https://vm.tiktok.com/ZNHWssk5wSBYk-PnpGF/"

# Url collection scraper
COLLECTION_URL_FILE = "tiktok_urls.json"

# Video transcriptions
VIDEOS_FOLDER = "./downloads"
TRANSCRIPTS_FOLDER = "./transcripts"
WHISPER_MODEL = "turbo"  # tiny, base, small, medium, large, large-v2, large-v3, turbo

# Agent
RESULT_FOLDER = "./results"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Example script with arguments.")
    
    parser.add_argument("--url", help="Url of the TikTok collection", default=COLLECTION_URL)
    parser.add_argument("--first-step", help="First step to do. Possible values:\n-download-url\n-download-videos\n-transcript\n-agent", default="download-url")

    args = parser.parse_args()
    COLLECTION_URL = args.url

    first_step = args.first_step
    possible_steps = ["download-url", "download-videos", "transcript", "agent", "data-cleaning"]
    if first_step not in possible_steps:
        raise ValueError(f"Invalid first step. Possible values: {possible_steps}")
    first_step_num = dict(map(reversed, enumerate(possible_steps)))[first_step]
    

    print(f"Using collection URL: {COLLECTION_URL}")
    # DESCARGA DE URLS
    if first_step_num > 0:
        print("Skipping URL download step.")
    else:
        # URL de la colección de TikTok

        # Crear el scraper
        scraper = TikTokCollectionScraper(headless=False)  # Cambiar a True para modo headless

        try:
            # Hacer scraping
            urls = scraper.scrape_collection(COLLECTION_URL, max_scrolls=15)
            
            # Mostrar resultados
            print("\n=== RESULTADOS ===")
            for i, url in enumerate(urls, 1):
                print(f"{i}. {url}")
            
            # Guardar en archivo
            if urls:
                scraper.save_urls(urls, COLLECTION_URL_FILE)
            
        finally:
            scraper.close()

    # DESCARGA DE VIDEOS
    if first_step_num > 1:
        print("Skipping video download.")
    else:
        # Crear el scraper
        scraper = TikTokVideoScraper(headless=False)

        # Load TikTok URLs from the JSON file
        with open(COLLECTION_URL_FILE, 'r') as file:
            tiktok_urls = json.load(file)

        for url in tiktok_urls["urls"]:
            print(f"Processing URL: {url}")
            scraper.process_video(url)

    # TRANSCRIPCIÓN DE AUDIOS
    if first_step_num > 2:
        print("Skipping transcription step.")
    else:
        transcribe_videos(VIDEOS_FOLDER, TRANSCRIPTS_FOLDER, WHISPER_MODEL)

    # AGENTE
    if first_step_num > 3:
        print("Skipping agent step.")
    else:
        ids_total = [file[13:-4] for file in os.listdir(TRANSCRIPTS_FOLDER)]
        if not os.path.exists(RESULT_FOLDER):
            os.makedirs(RESULT_FOLDER)
        ids_done = [file[7:-5] for file in os.listdir(RESULT_FOLDER)]
        ids_pending = list(set(ids_total) - set(ids_done))
        for id in ids_pending:
            print(f"Processing video ID: {id}")
            description_path = f"./data/tiktok_data_{id}.json"
            with open(description_path, "r", encoding="utf-8") as f:
                description = json.load(f)["basic_info"]["description"]

            transcript_path = f"./transcripts/tiktok_video_{id}.txt"
            with open(transcript_path, "r", encoding="utf-8") as f:
                transcript = f.read()
            example = {
                "text": f"Descripción: {description}\nTranscripción: {transcript}"
            }
            result = app.invoke(example)
            with open(f'{RESULT_FOLDER}/result_{id}.json', 'w') as f:
                json.dump(result, f)

    # DATA CLEANING
    if first_step_num > 4:
        print("Skipping data cleaning step.")
    else:
        entities = {}
        summaries = defaultdict(list)
        web_summaries = {}

        for file_path in os.listdir(RESULT_FOLDER):
            print(f"Processing {file_path}...")
            with open(f"{RESULT_FOLDER}/{file_path}", "r", encoding="utf-8") as file:
                data = json.load(file)
                # Entities
                entities.update(data["entities"])

                # Entities. Recorremos 1 a 1 porque puede haber solape y no nos interesa perder info de, por ejemplo, resumenes de videos
                for k, v in json.loads(data["summaries"])["Summaries"].items():
                    summaries[k].append(v)

                # Web summaries
                web_summaries.update(data["entities_web_summaries"])

        # Unimos descripciones de distintos videos pero misma entidad
        summaries = {x[0]: ' '.join(x[1]) for x in list(summaries.items())}
        # Unimos toda la info en un solo dataframe
        df = pd.DataFrame(summaries.items(), columns=["entity_location", "summary"]).merge(
            pd.DataFrame(entities.items(), columns=["entity_location", "entity_description"]), 
            on="entity_location", 
            how="left"
        ).merge(
            pd.DataFrame(web_summaries.items(), columns=["entity_location", "web_summary"]), 
            on="entity_location", 
            how="left"
        )

        df["entity"] = df["entity_location"].str.split(",").str[0]
        df["location_info"] = df["entity_location"].str.split(",").str[1:].str.join(",")
        df[["entity", "entity_description", "location_info", "summary", "web_summary"]].to_csv(f"{RESULT_FOLDER}/cleaned_data.csv", index=False)