import yt_dlp
import time
import json
import re
import requests
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from urllib.parse import urlparse, parse_qs

class TikTokVideoScraper:
    def __init__(self, headless=True):
        self.setup_driver(headless)
        self.session = requests.Session()
        self.setup_session()
        
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
        
        # User agent realista
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        self.driver = webdriver.Chrome(executable_path = 'C://chromedriver-win64//chromedriver.exe', options=chrome_options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
    def setup_session(self):
        """Configura la sesión de requests"""
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def extract_video_data(self, video_url):
        """Extrae toda la información del video de TikTok"""
        print(f"Procesando video: {video_url}")
        
        try:
            self.driver.get(video_url)
            time.sleep(5)  # Espera a que cargue completamente
            
            video_data = {
                'url': video_url,
                'scraped_at': datetime.now().isoformat(),
                'basic_info': self.extract_basic_info(),
                'engagement': self.extract_engagement_data(),
                'author': self.extract_author_info(),
                'video_details': self.extract_video_details(),
                'metadata': self.extract_metadata(),
                'download_urls': self.extract_download_urls()
            }
            
            return video_data
            
        except Exception as e:
            print(f"Error extrayendo datos del video: {str(e)}")
            return None
    
    def extract_basic_info(self):
        """Extrae información básica del video"""
        basic_info = {}
        
        try:
            # Título/descripción del video
            selectors = [
                '[data-e2e="browse-video-desc"]',
                '[data-e2e="video-desc"]',
                'h1[data-e2e="browse-video-desc"]',
                '.tiktok-j2a19a-SpanText'
            ]
            
            description = self.find_text_by_selectors(selectors)
            basic_info['description'] = description
            
            # Hashtags
            hashtags = self.extract_hashtags()
            basic_info['hashtags'] = hashtags
            
            # Música/sonido
            music_selectors = [
                '[data-e2e="browse-music"]',
                '[data-e2e="video-music"]',
                '.tiktok-kdeneb-SpanText'
            ]
            
            music = self.find_text_by_selectors(music_selectors)
            basic_info['music'] = music
            
        except Exception as e:
            print(f"Error extrayendo información básica: {str(e)}")
            
        return basic_info
    
    def extract_engagement_data(self):
        """Extrae datos de engagement (likes, shares, etc.)"""
        engagement = {}
        
        try:
            # Likes
            like_selectors = [
                '[data-e2e="like-count"]',
                '[data-e2e="browse-like-count"]',
                '.tiktok-1bs0hyz-SpanText'
            ]
            likes = self.find_text_by_selectors(like_selectors)
            engagement['likes'] = self.parse_count(likes)
            
            # Comentarios
            comment_selectors = [
                '[data-e2e="comment-count"]',
                '[data-e2e="browse-comment-count"]'
            ]
            comments = self.find_text_by_selectors(comment_selectors)
            engagement['comments'] = self.parse_count(comments)
            
            # Shares
            share_selectors = [
                '[data-e2e="share-count"]',
                '[data-e2e="browse-share-count"]'
            ]
            shares = self.find_text_by_selectors(share_selectors)
            engagement['shares'] = self.parse_count(shares)
            
            # Vistas (si está disponible)
            view_selectors = [
                '[data-e2e="video-views"]',
                '.video-count'
            ]
            views = self.find_text_by_selectors(view_selectors)
            engagement['views'] = self.parse_count(views)
            
        except Exception as e:
            print(f"Error extrayendo datos de engagement: {str(e)}")
            
        return engagement
    
    def extract_author_info(self):
        """Extrae información del autor"""
        author_info = {}
        
        try:
            # Nombre de usuario
            username_selectors = [
                '[data-e2e="browse-username"]',
                '[data-e2e="video-username"]',
                '.tiktok-1w9r2es-SpanUniqueId'
            ]
            username = self.find_text_by_selectors(username_selectors)
            author_info['username'] = username
            
            # Nombre mostrado
            display_name_selectors = [
                '[data-e2e="browse-user-displayname"]',
                '.tiktok-qi72ht-SpanNickName'
            ]
            display_name = self.find_text_by_selectors(display_name_selectors)
            author_info['display_name'] = display_name
            
            # Avatar/foto de perfil
            avatar_selectors = [
                '[data-e2e="browse-user-avatar"] img',
                '.tiktok-1zpj2q-ImgAvatar'
            ]
            avatar_url = self.find_attribute_by_selectors(avatar_selectors, 'src')
            author_info['avatar_url'] = avatar_url
            
            # Verificación
            verified_selectors = [
                '[data-e2e="browse-user-verified"]',
                '.tiktok-1443suu-DivWrapper'
            ]
            is_verified = len(self.driver.find_elements(By.CSS_SELECTOR, ','.join(verified_selectors))) > 0
            author_info['is_verified'] = is_verified
            
        except Exception as e:
            print(f"Error extrayendo información del autor: {str(e)}")
            
        return author_info
    
    def extract_video_details(self):
        """Extrae detalles técnicos del video"""
        video_details = {}
        
        try:
            # Buscar elemento video
            video_elements = self.driver.find_elements(By.TAG_NAME, "video")
            
            if video_elements:
                video_element = video_elements[0]
                
                # Duración
                duration = self.driver.execute_script("return arguments[0].duration", video_element)
                video_details['duration'] = duration
                
                # Dimensiones
                video_width = self.driver.execute_script("return arguments[0].videoWidth", video_element)
                video_height = self.driver.execute_script("return arguments[0].videoHeight", video_element)
                video_details['width'] = video_width
                video_details['height'] = video_height
                video_details['aspect_ratio'] = f"{video_width}:{video_height}" if video_width and video_height else None
                
                # URL del video (si está disponible)
                video_src = video_element.get_attribute('src')
                video_details['video_src'] = video_src
                
        except Exception as e:
            print(f"Error extrayendo detalles del video: {str(e)}")
            
        return video_details
    
    def extract_metadata(self):
        """Extrae metadatos adicionales"""
        metadata = {}
        
        try:
            # Fecha de publicación (si está disponible)
            time_selectors = [
                '[data-e2e="browser-nickname"] + div',
                '.tiktok-1ed61qv-SpanText'
            ]
            publish_time = self.find_text_by_selectors(time_selectors)
            metadata['publish_time'] = publish_time
            
            # ID del video (extraer de la URL)
            video_id = self.extract_video_id_from_url(self.driver.current_url)
            metadata['video_id'] = video_id
            
            # Obtener datos del JSON-LD si existe
            json_ld_data = self.extract_json_ld_data()
            if json_ld_data:
                metadata['json_ld'] = json_ld_data
                
        except Exception as e:
            print(f"Error extrayendo metadatos: {str(e)}")
            
        return metadata
    
    def extract_download_urls(self):
        """Intenta extraer URLs de descarga del video"""
        download_urls = {}
        
        try:
            # Buscar en el código fuente patrones de URLs de video
            page_source = self.driver.page_source
            
            # Patrones comunes para URLs de video de TikTok
            patterns = [
                r'"playAddr":"([^"]+)"',
                r'"downloadAddr":"([^"]+)"',
                r'"playapi":"([^"]+)"',
                r'videoUrl":"([^"]+)"'
            ]
            
            for i, pattern in enumerate(patterns):
                matches = re.findall(pattern, page_source)
                if matches:
                    # Limpiar URLs (TikTok a veces las codifica)
                    clean_urls = [url.replace('\\u002F', '/').replace('\\', '') for url in matches]
                    download_urls[f'pattern_{i+1}'] = clean_urls
            
            # También buscar en elementos video
            video_elements = self.driver.find_elements(By.TAG_NAME, "video")
            for i, video in enumerate(video_elements):
                src = video.get_attribute('src')
                if src:
                    download_urls[f'video_element_{i+1}'] = src
                    
        except Exception as e:
            print(f"Error extrayendo URLs de descarga: {str(e)}")
            
        return download_urls
    
    def extract_hashtags(self):
        """Extrae hashtags del video"""
        try:
            # Buscar hashtags en la descripción
            description_elements = self.driver.find_elements(By.CSS_SELECTOR, '[data-e2e="browse-video-desc"] a, [data-e2e="video-desc"] a')
            hashtags = []
            
            for element in description_elements:
                text = element.get_attribute('textContent') or element.text
                if text and text.startswith('#'):
                    hashtags.append(text)
                    
            return hashtags
        except:
            return []
    
    def extract_json_ld_data(self):
        """Extrae datos estructurados JSON-LD si existen"""
        try:
            json_scripts = self.driver.find_elements(By.XPATH, '//script[@type="application/ld+json"]')
            json_data = []
            
            for script in json_scripts:
                try:
                    data = json.loads(script.get_attribute('innerHTML'))
                    json_data.append(data)
                except:
                    continue
                    
            return json_data if json_data else None
        except:
            return None
    
    def find_text_by_selectors(self, selectors):
        """Busca texto usando múltiples selectores"""
        for selector in selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    text = elements[0].get_attribute('textContent') or elements[0].text
                    if text and text.strip():
                        return text.strip()
            except:
                continue
        return None
    
    def find_attribute_by_selectors(self, selectors, attribute):
        """Busca un atributo usando múltiples selectores"""
        for selector in selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    attr_value = elements[0].get_attribute(attribute)
                    if attr_value:
                        return attr_value
            except:
                continue
        return None
    
    def parse_count(self, count_str):
        """Convierte strings como '1.2M' a números"""
        if not count_str:
            return None
            
        count_str = count_str.replace(',', '').upper()
        
        if 'K' in count_str:
            return int(float(count_str.replace('K', '')) * 1000)
        elif 'M' in count_str:
            return int(float(count_str.replace('M', '')) * 1000000)
        elif 'B' in count_str:
            return int(float(count_str.replace('B', '')) * 1000000000)
        else:
            try:
                return int(count_str)
            except:
                return count_str
    
    def extract_video_id_from_url(self, url):
        """Extrae el ID del video de la URL"""
        try:
            # Para URLs como /video/1234567890
            match = re.search(r'/video/(\d+)', url)
            if match:
                return match.group(1)
            
            # Para URLs cortas
            parsed_url = urlparse(url)
            if 'vm.tiktok.com' in parsed_url.netloc:
                return parsed_url.path.strip('/')
                
        except:
            pass
        return None
    
    def download_video(self, video_url, custom_filename=None, output_dir="downloads"):
        """Descarga el archivo de video"""
        if not video_url:
            return None
            
        try:
            os.makedirs(output_dir, exist_ok=True)
            
            response = self.session.get(video_url, stream=True)
            if response.status_code == 200:
                # Generar nombre de archivo
                if custom_filename is None:
                    filename = f"tiktok_video_{int(time.time())}.mp4"
                else:
                    filename = custom_filename
                filepath = os.path.join(output_dir, filename)
                
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                print(f"Video descargado: {filepath}")
                return filepath
                
        except Exception as e:
            print(f"Error descargando video: {str(e)}")
            
        return None
    
    def save_data(self, video_data, filename=None):
        """Guarda los datos en un archivo JSON"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            video_id = video_data.get('metadata', {}).get('video_id', 'unknown')
            filename = f"tiktok_data_{video_id}_{timestamp}.json"
        
        os.makedirs("data", exist_ok=True)
        filepath = os.path.join("data", filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(video_data, f, indent=2, ensure_ascii=False)
        
        print(f"Datos guardados en: {filepath}")
        return filepath
    
    def close(self):
        """Cierra el driver"""
        self.driver.quit()

    def process_video(self, video_url, custom_filename=None):
        """Procesa un video completo: extrae datos y descarga el video"""
        video_data = self.extract_video_data(video_url)
        if video_data:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            # Guardar datos con timestamp unificado
            json_filename = f"tiktok_data_{timestamp}.json"
            self.save_data(video_data, json_filename)
            # Descargar video
            try:
                ydl_opts = {
                    'outtmpl': f'downloads/tiktok_video_{timestamp}.%(ext)s',
                    'format': 'best[ext=mp4]',
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([video_data['url']])
                    print("Video descargado con yt-dlp")
                    video_downloaded = True
                    
            except ImportError:
                print("yt-dlp no está instalado. Instala con: pip install yt-dlp")
            except Exception as e:
                print(f"Error con yt-dlp: {str(e)}")


if __name__ == "__main__":
    scraper = TikTokVideoScraper(headless=False)  # Cambiar a True para modo headless
    try:
        test_url = "https://www.tiktok.com/@scout2015/video/6718335390845095173"
        scraper.process_video(test_url)
    finally:
        scraper.close()