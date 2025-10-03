# TripTok

**TripTok** es un proyecto en Python que:

1️⃣ Localiza y descarga todos los vídeos y su información (título, descripción, etc.).

2️⃣ Transcribiese el audio de cada video.

3️⃣ Mediante un agente:

	- Detecta las entidades de las que se habla en cada video.
	- Resume qué se dice de cada entidad.
	- Busca información adicional en internet.
	- Genera un resumen extra extendido con la información de internet.

4️⃣ Vuelca toda la información en un csv legible, claro y ordenado.

> ⚠️ **Aviso legal**: El scraping y descarga de contenido de TikTok puede violar sus Términos de Servicio y/o derechos de autor. Usa este proyecto solo con fines de investigación o educativos y bajo tu propia responsabilidad.

---

## Requisitos

* Python 3.9.
* Google Chrome instalado
* [ChromeDriver](https://chromedriver.chromium.org/) compatible con tu versión de Chrome
* GPU dedicada capaz de ejecutar LLMs pequeños y OpenAI Whisper.

Instala dependencias:

```bash
pip install -r requirements.txt
```

---

## Stack utilizado

 - [Selenium](https://pypi.org/project/selenium/) para el scraper de videos.
 - [Whisper de OpenAI](https://github.com/openai/whisper) para las transcripciones.
 - [SearXNG](https://github.com/searxng/searxng) como motor de búsqueda web.
 - [Llama.cpp](https://github.com/ggml-org/llama.cpp) para montar un LLM local (Qwen3 4B 2507) sobre el que construir el agente. 



## Estructura del proyecto

```
TripTok/
├── agent/               # Agente LLM (LangGraph + LangChain)
├── audio_to_text/       # Conversión de audio a texto con Whisper
├── tiktok_scraping/     # Scrapers para colecciones y videos
├── data/                # Metadatos guardados
├── downloads/           # Videos descargados
├── transcripts/         # Transcripciones
├── results/             # Resultados combinados
├── main.py              # Script de entrada principal
└── requirements.txt
```

---

## Configuración inicial

### 1. ChromeDriver

Por defecto, el código espera `chromedriver` en:

```
C://chromedriver-win64//chromedriver.exe
```

### 2. Servicios locales requeridos (para el agente)

* **LLM**: el agente usa `http://127.0.0.1:1234/v1` como endpoint. Debes tener un modelo LLM local corriendo con una API compatible con el modelo de OpenAI (ej. [Ollama](https://ollama.ai), [LM Studio](https://lmstudio.ai) o [llama.cpp](https://github.com/ggml-org/llama.cpp)).
* **Buscador web**: se espera un servicio SearXNG en `http://localhost:8080/search` que devuelva resultados en JSON. Si no lo tienes, desactiva la parte del agente o implementa un stub.
* **Prompts**: el agente carga prompts desde `./prompts/*.txt` (`ner_prompt.txt`, `video_summarize_prompt.txt`)

---

## Uso

Ejecuta el script principal con el parámetro `--first-step` para indicar desde qué paso empezar. Si no indicamos nada, se ejecutará el flujo al completo.

### 1. Scrappear URLs de una colección

```bash
python main.py --first-step download-url
```

Esto abrirá el navegador, cargará la colección indicada en `COLLECTION_URL` y guardará las URLs en `tiktok_urls.json`.

### 2. Descargar videos y metadatos

```bash
python main.py --first-step download-videos
```

Se procesarán las URLs de `tiktok_urls.json` y se guardarán videos en `./downloads` y datos en `./data`.

### 3. Transcribir videos

```bash
python main.py --first-step transcript
```

Se generarán archivos `.txt` en `./transcripts`.

### 4. Ejecutar el agente

```bash
python main.py --first-step agent
```

Esto procesa las descripciones + transcripciones con el agente LLM.

### 5. Limpieza / combinación de resultados

```bash
python main.py --first-step data-cleaning
```

Se combinan y limpian los resultados en un CSV final en `./results`.

---

## ToDo's

* Parametrizar la ruta del ChromeDriver automáticamente.
* Añadir manejo de errores/captchas en los scrapers.
* Robustecer el scraper en caso de cambio del DOM de TikTok.
* Pulir y mejorar el agente.

---

## Créditos

Proyecto creado por [ikkani](https://github.com/ikkani).