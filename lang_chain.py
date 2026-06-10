import socket
import requests

# Forzar a Python a usar únicamente IPv4 para las conexiones salientes
orig_getaddrinfo = socket.getaddrinfo

def filtered_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
    return orig_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)

socket.getaddrinfo = filtered_getaddrinfo

from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain_cohere import ChatCohere # Comentado
from langchain_core.messages import HumanMessage
from my_models import GEMINI_FLASH
from my_keys import GEMINI_API_KEY
from my_helper import encode_image
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough  
from langchain_core.globals import set_debug
from detalles_imagen import DetallesImagen  # Tu modelo Pydantic

set_debug(True)

# ---------------------------------------------------------------------
# 1. CONFIGURACIÓN DE MODELOS (Solo Gemini)
# ---------------------------------------------------------------------
llm_gemini = ChatGoogleGenerativeAI(
     api_key=GEMINI_API_KEY,
     model=GEMINI_FLASH,      
) 

# ---------------------------------------------------------------------
# 2. ANÁLISIS MULTIMODAL MANUAL (Gemini - Prueba Inicial de Texto Libre)
# ---------------------------------------------------------------------
imagen_base64 = encode_image('datos/ejemplo_grafico.jpg')
pregunta_usuario = "Describa la imagen de forma detallada." 

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

# Formateamos manualmente para la primera prueba de Gemini
prompt_formateado = template_analisis.format_messages(
     pregunta=pregunta_usuario, 
     imagen_b64=imagen_base64
)

print("Analizando imagen con Gemini de forma manual (Texto)...")
respuesta_imagen = llm_gemini.invoke(prompt_formateado)
print("\nResultado del análisis manual:\n", respuesta_imagen.content)
print("-" * 50)

# ---------------------------------------------------------------------
# 3. EXTRACCIÓN ESTRUCTURADA DIRECTA CON PYDANTIC (Modo Recomendado)
# ---------------------------------------------------------------------
# Obligamos a Gemini a mapear los datos usando el esquema de DetallesImagen
llm_estructurado = llm_gemini.with_structured_output(DetallesImagen)

# Construimos la cadena LCEL limpia pasando el prompt al modelo estructurado
cadena_estructurada = template_analisis | llm_estructurado

print("Iniciando pipeline estructurado con Gemini...")

# Ejecución de la cadena pasando las llaves exactas que exige tu template_analisis
resultado_objeto = cadena_estructurada.invoke({
    "pregunta": "Analiza este gráfico y extrae el título, descripción y 3 palabras clave.",
    "imagen_b64": imagen_base64
})

# ---------------------------------------------------------------------
# 4. IMPRESIÓN DEL RESULTADO (Acceso directo a Pydantic)
# ---------------------------------------------------------------------
print("\n" + "="*50)
print("¡ANÁLISIS ESTRUCTURADO COMPLETADO POR GEMINI!")
print("="*50)

# Al ser un objeto nativo de Pydantic extraído por LangChain, accedes directo a sus campos:
print(f"📌 TÍTULO: {resultado_objeto.titulo}")
print(f"📝 DESCRIPCIÓN: {resultado_objeto.descripcion}")
print(f"🏷️ ETIQUETAS (Exactamente 3): {resultado_objeto.etiquetas}")

print("\nJSON Crudo Generado:")
print(resultado_objeto.model_dump_json(indent=4))