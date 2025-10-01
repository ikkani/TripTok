import requests
from bs4 import BeautifulSoup
import re
from typing import List, Dict, Optional

def search_tool(query):
    url = "http://localhost:8080/search"
    params = {
        "q": query,
        "format": "json",
        "num": 7
    }
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    }
    r = requests.get(url, params=params, headers=headers)
    r.raise_for_status()
    return r.json()

def extract_main_content(html_content: str) -> str:
    """
    Extrae el contenido principal del HTML usando selectores comunes
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Selectores comunes para contenido principal
    main_selectors = [
        'article',
        'main', 
        '[role="main"]',
        '.content',
        '.post-content',
        '.entry-content',
        '.article-body',
        '.story-body',
        '#content',
        '.main-content'
    ]
    
    # Intentar encontrar contenido principal
    main_content = None
    for selector in main_selectors:
        main_content = soup.select_one(selector)
        if main_content:
            break
    
    # Si no encuentra, usar el body pero limpiar elementos no deseados
    if not main_content:
        main_content = soup.find('body') or soup
    
    # Eliminar elementos no deseados
    unwanted_selectors = [
        'nav', 'header', 'footer', 'aside', 
        '.navigation', '.menu', '.sidebar',
        '.advertisement', '.ads', '.social-share',
        'script', 'style', 'noscript'
    ]
    
    for selector in unwanted_selectors:
        for element in main_content.select(selector):
            element.decompose()
    
    return main_content.get_text(strip=True, separator=' ')

def filter_relevant_content(content: str, query_terms: List[str], min_relevance: float = 0.3) -> str:
    """
    Filtra el contenido basándose en términos de búsqueda relevantes
    """
    sentences = re.split(r'[.!?]+', content)
    relevant_sentences = []
    
    query_terms_lower = [term.lower() for term in query_terms]
    
    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence) < 20:  # Ignorar oraciones muy cortas
            continue
            
        sentence_lower = sentence.lower()
        relevance_score = sum(1 for term in query_terms_lower if term in sentence_lower)
        relevance_ratio = relevance_score / len(query_terms_lower)
        
        if relevance_ratio >= min_relevance:
            relevant_sentences.append(sentence)
    
    return '. '.join(relevant_sentences)

def extract_key_paragraphs(content: str, query_terms: List[str], max_paragraphs: int = 5) -> str:
    """
    Extrae los párrafos más relevantes basándose en densidad de términos clave
    """
    paragraphs = [p.strip() for p in content.split('\n') if len(p.strip()) > 50]
    
    scored_paragraphs = []
    query_terms_lower = [term.lower() for term in query_terms]
    
    for paragraph in paragraphs:
        paragraph_lower = paragraph.lower()
        score = 0
        
        # Contar apariciones de términos clave
        for term in query_terms_lower:
            score += paragraph_lower.count(term)
        
        # Bonus por longitud apropiada (ni muy corto ni muy largo)
        length_score = min(len(paragraph) / 100, 5) * 0.1
        score += length_score
        
        if score > 0:
            scored_paragraphs.append((score, paragraph))
    
    # Ordenar por puntuación y tomar los mejores
    scored_paragraphs.sort(key=lambda x: x[0], reverse=True)
    top_paragraphs = [p[1] for p in scored_paragraphs[:max_paragraphs]]
    
    return '\n\n'.join(top_paragraphs)

def download_relevant_content(query: str, urls: List[str], max_urls: int = 3) -> List[Dict]:
    """
    Descarga y extrae solo el contenido relevante de las URLs
    """
    query_terms = query.split()
    results = []
    downloaded = 0
    
    for url in urls:
        if downloaded >= max_urls:
            break
            
        try:
            print(f"Descargando: {url}")
            r = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
            r.raise_for_status()
            
            # Extraer contenido principal
            main_content = extract_main_content(r.text)
            
            if len(main_content) < 100:
                print(f"Contenido muy corto en {url}, saltando...")
                continue
            
            # Filtrar contenido relevante
            relevant_content = filter_relevant_content(main_content, query_terms)
            
            # Si no hay suficiente contenido relevante, usar extracción por párrafos
            if len(relevant_content) < 200:
                relevant_content = extract_key_paragraphs(main_content, query_terms)
            
            if relevant_content:
                results.append({
                    'url': url,
                    'content': relevant_content,
                    'length': len(relevant_content)
                })
                downloaded += 1
                print(f"✓ Contenido relevante extraído ({len(relevant_content)} caracteres)")
            else:
                print(f"No se encontró contenido relevante en {url}")
                
        except Exception as e:
            print(f"Error descargando {url}: {e}")
    
    return results