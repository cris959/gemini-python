import socket
import requests

# Forzar a Python a usar únicamente IPv4 para las conexiones salientes
orig_getaddrinfo = socket.getaddrinfo

def filtered_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
    return orig_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)

socket.getaddrinfo = filtered_getaddrinfo

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_cohere import ChatCohere
from langchain_core.messages import HumanMessage
from my_models import GEMINI_FLASH
from my_keys import GEMINI_API_KEY, COHERE_API_KEY
from my_helper import encode_image
from langchain_core.prompts import ChatPromptTemplate # Actualizado #


# ---------------------------------------------------------------------
# 1. EJECUCIÓN CON GEMINI (Texto)
# ---------------------------------------------------------------------
llm_gemini = ChatGoogleGenerativeAI(
    api_key= GEMINI_API_KEY,
    model= GEMINI_FLASH,      
) 

consulta = "Cuales canales colombianos de youtube me recomiendas para saber mas sobre telefonos inteligentes"
respuesta_gemini = llm_gemini.invoke(consulta) 
print("Gemini: ", respuesta_gemini.content)
print("-" * 50)

# ---------------------------------------------------------------------
# 2. EJECUCIÓN CON COHERE (Texto)
# ---------------------------------------------------------------------
llm_cohere = ChatCohere(
    cohere_api_key=COHERE_API_KEY
)

respuesta_cohere = llm_cohere.invoke([HumanMessage(content=consulta)])
print("Cohere: ", respuesta_cohere.content)
print("-" * 50)

# ---------------------------------------------------------------------
# 3. ANÁLISIS MULTIMODAL CON PROMPT TEMPLATE (Gemini)
# ---------------------------------------------------------------------
# Codificamos la imagen local
imagen_base64 = encode_image('datos/ejemplo_grafico.jpg')
pregunta_usuario = "Describa la imagen de forma detallada."

# Definimos la plantilla respetando el formato multimodal de LangChain
template_analisis = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Asume que eres analista de imagenes. Tu principal tarea consiste en: analizar una imagen para extraer las informaciones mas relevantes de manera objetiva."
        ),
        (
            "human",
            [
                {"type": "text", "text": "{pregunta}"},
                {
                    "type": "image_url",
                    "image_url": {"url": "data:image/jpeg;base64,{imagen_b64}"}
                }
            ]
        )
    ]
)

# Formateamos la plantilla pasando las variables correspondientes
prompt_formateado = template_analisis.format_messages(
    pregunta=pregunta_usuario,
    imagen_b64=imagen_base64
)

# Invocamos a Gemini pasando el prompt final estructurado
print("Analizando imagen con Gemini...")
respuesta_imagen = llm_gemini.invoke(prompt_formateado)
print("\nResultado del análisis:\n", respuesta_imagen.content)