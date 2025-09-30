import json

from tiktok_collection_scraper import TikTokCollectionScraper
from tiktok_video_scraper import TikTokVideoScraper
from audio_to_text import transcribe_videos

# Config
COLLECTION_URL = "https://vm.tiktok.com/ZNHtWyhtf5SMc-otqBJ/"

# Url collection scraper
COLLECTION_URL_FILE = "tiktok_urls.json"

# Video transcriptions
VIDEOS_FOLDER = "./downloads"
TRANSCRIPTS_FOLDER = "./transcripts"
WHISPER_MODEL = "turbo"  # tiny, base, small, medium, large, large-v2, large-v3, turbo

if __name__ == "__main__":
    # DESCARGA DE URLS

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
    scraper = TikTokVideoScraper(headless=False)

    # Load TikTok URLs from the JSON file
    with open(COLLECTION_URL_FILE, 'r') as file:
        tiktok_urls = json.load(file)

    for url in tiktok_urls["urls"]:
        print(f"Processing URL: {url}")
        scraper.process_video(url)

    # TRANSCRIPCIÓN DE AUDIOS
    transcribe_videos(VIDEOS_FOLDER, TRANSCRIPTS_FOLDER, WHISPER_MODEL)
