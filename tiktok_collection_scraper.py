import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import json

class TikTokCollectionScraper:
    def __init__(self, headless=True):
        self.setup_driver(headless)
        
    def setup_driver(self, headless):
        """Configura el driver de Chrome"""
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        
        # Opciones para evitar detección
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # User agent para parecer un navegador real
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        self.driver = webdriver.Chrome(executable_path = 'C://chromedriver-win64//chromedriver.exe', options=chrome_options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
    def scroll_to_load_more(self, pause_time=2, max_scrolls=20):
        """Hace scroll para cargar más videos"""
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        scrolls = 0
        
        while scrolls < max_scrolls:
            # Scroll hacia abajo
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(pause_time)
            
            # Calcula nueva altura
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            
            if new_height == last_height:
                print(f"No hay más contenido que cargar después de {scrolls} scrolls")
                break
                
            last_height = new_height
            scrolls += 1
            print(f"Scroll {scrolls}/{max_scrolls} completado")
            
    def extract_video_urls(self):
        """Extrae las URLs de los videos de la colección"""
        video_urls = set()
        
        try:
            # Espera a que carguen los elementos de video
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "a"))
            )
            
            # Busca todos los enlaces que contengan patrones de TikTok
            links = self.driver.find_elements(By.TAG_NAME, "a")
            
            for link in links:
                href = link.get_attribute("href")
                if href and self.is_tiktok_video_url(href):
                    video_urls.add(href)
                    
        except TimeoutException:
            print("Timeout esperando a que carguen los videos")
            
        return list(video_urls)
    
    def is_tiktok_video_url(self, url):
        """Verifica si la URL es de un video de TikTok"""
        patterns = [
            r'https://www\.tiktok\.com/@[^/]+/video/\d+',
            r'https://vm\.tiktok\.com/[A-Za-z0-9]+',
            r'https://www\.tiktok\.com/t/[A-Za-z0-9]+',
        ]
        
        for pattern in patterns:
            if re.match(pattern, url):
                return True
        return False
    
    def scrape_collection(self, collection_url, max_scrolls=10):
        """Función principal para hacer scraping de una colección"""
        print(f"Iniciando scraping de: {collection_url}")
        
        try:
            self.driver.get(collection_url)
            time.sleep(5)  # Espera inicial para que cargue la página
            
            # Hacer scroll para cargar más contenido
            print("Haciendo scroll para cargar más videos...")
            self.scroll_to_load_more(max_scrolls=max_scrolls, pause_time=4)
            
            # Extraer URLs
            print("Extrayendo URLs de videos...")
            urls = self.extract_video_urls()
            
            print(f"Se encontraron {len(urls)} URLs de videos")
            return urls
            
        except Exception as e:
            print(f"Error durante el scraping: {str(e)}")
            return []
    
    def save_urls(self, urls, filename="tiktok_urls.json"):
        """Guarda las URLs en un archivo JSON"""
        data = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_urls": len(urls),
            "urls": urls
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"URLs guardadas en {filename}")
    
    def close(self):
        """Cierra el driver"""
        self.driver.quit()