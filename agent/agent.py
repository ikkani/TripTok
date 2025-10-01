import ast
from langgraph.graph import StateGraph, END, START
from langchain_openai import ChatOpenAI
from typing import TypedDict, List, Dict, Union
import requests
import pprint 

# Tools #
from agent.agent_tools import search_tool, download_relevant_content

# Definimos el modelo y el estado
llm = ChatOpenAI(
    openai_api_base="http://127.0.0.1:1234/v1",
    openai_api_key="not-needed",
    model="qwen/qwen3-4b-2507"
)

# Definimos el estado
class State(TypedDict):
    text: str
    entities: List[str]  # Simplificamos a una lista de strings para este ejemplo
    summaries: Dict[str, str]
    entities_web_content: Dict[str, str]
    entities_web_summaries: Dict[str, str]

# Carga los prompts
with open("./prompts/ner_prompt.txt", "r", encoding="utf-8") as f:
    ner_prompt = f.read()

with open("./prompts/video_summarize_prompt.txt", "r", encoding="utf-8") as f:
    video_summarize_prompt = f.read()

with open("./prompts/web_summarize_prompt.txt", "r", encoding="utf-8") as f:
    web_summarize_prompt = f.read()


# Nodo 1: Detección de entidades
def ner_node(state: State):
    input_text = state["text"]
    messages = [
        {"role": "system", "content": ner_prompt},
        {"role": "user", "content": input_text}
    ]
    response = llm.invoke(messages)
    # Por simplicidad, asumimos que el LLM devuelve una lista de entidades en formato string
    # En un caso real, necesitarías un parser para obtener una lista de Python
    parsed_dict = ast.literal_eval(response.content)
    return {"entities": parsed_dict}

# Nodo 2: Resumen de entidades
def summary_node(state: State):
    input_text = state["text"]
    entities = state["entities"]
    
    # Formateamos la lista de entidades para el prompt
    formatted_entities = "\n".join([f"- {e}" for e in entities])
    
    # Usamos f-string para insertar el texto y las entidades en el prompt
    messages = [
        {"role": "system", "content": video_summarize_prompt.format(input_text=input_text, entities=formatted_entities)}
    ]
    
    response = llm.invoke(messages)
    return {"summaries": response.content}

# Nodo 3: Búsqueda y descarga de contenido relevante
def web_download_node(state: State, query_suffix: str = " review"):
    web_dict = {}
    for entity in state["entities"]:
        print(f"Buscando información sobre: {entity}")
        search_results = search_tool(entity + query_suffix)
        # Formateamos el contenido de los resultados
        results_txt = 'NEW DOCUMENT:\n'.join(
        f'title: {result["title"]}\ncontent: {result["content"]}\n' for result in search_results.get('results', [])
        )
        web_dict[entity] = results_txt

    return {"entities_web_content": web_dict}

# Nodo 4: En base a los artículos descargados, generar un resumen adicional
def web_summary_node(state: State):
    web_summary_dict = {}
    for entity, content in state["entities_web_content"].items():
        if not content.strip():
            web_summary_dict[entity] = "No se encontró contenido relevante."
            continue
        
        messages = [
            {"role": "system", "content": web_summarize_prompt.format(entity=entity, documents=content)},
            {"role": "user", "content": content}
        ]
        response = llm.invoke(messages)
        web_summary_dict[entity] = response.content

    return {"entities_web_summaries": web_summary_dict}



# Construimos el grafo
graph = StateGraph(State)
graph.add_node("ner", ner_node)
graph.add_node("summary", summary_node)
graph.add_node("web_download", web_download_node)
graph.add_node("web_summary", web_summary_node)

# Conectamos los nodos
graph.add_edge(START, "ner")
graph.add_edge("ner", "summary")
graph.add_edge("summary", "web_download")
graph.add_edge("web_download", "web_summary")
graph.add_edge("web_summary", END)

# Compilamos
app = graph.compile()

if __name__ == "__main__":

    import json
    description_path = "./data/tiktok_data_20250913_005000.json"
    with open(description_path, "r", encoding="utf-8") as f:
        description = json.load(f)["basic_info"]["description"]

    transcript_path = "./transcripts/tiktok_video_20250913_005000.txt"
    with open(transcript_path, "r", encoding="utf-8") as f:
        transcript = f.read()
    example = {
        "text": f"Descripción: {description}\nTranscripción: {transcript}"
    }
    result = app.invoke(example)
    print("Resumenes generados:")
    pprint.pp(result["entities"])
    pprint.pp(result["summaries"])
    pprint.pp(result["entities_web_content"])
    pprint.pp(result["entities_web_summaries"])