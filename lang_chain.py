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
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate # Actualizado #
from langchain_core.output_parsers import StrOutputParser # NUEVO: Falto importar el parser#
from langchain_core.runnables import RunnablePassthrough  # NUEVO: Para encadenar datos #
# from langchain.globals import set_debug    == bug ==
from langchain_core.globals import set_debug

set_debug(True)

# ---------------------------------------------------------------------
# 1. CONFIGURACIÓN DE MODELOS
# ---------------------------------------------------------------------
llm_gemini = ChatGoogleGenerativeAI(
     api_key=GEMINI_API_KEY,
     model=GEMINI_FLASH,      
) 

llm_cohere = ChatCohere(
    cohere_api_key=COHERE_API_KEY
)

# ---------------------------------------------------------------------
# 2. ANÁLISIS MULTIMODAL MANUAL (Gemini)
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

print("Analizando imagen con Gemini de forma manual...")
respuesta_imagen = llm_gemini.invoke(prompt_formateado)
print("\nResultado del análisis manual:\n", respuesta_imagen.content)
print("-" * 50)

# ---------------------------------------------------------------------
# 3. CADENA DE ANÁLISIS MULTIMODAL (LCEL)
# ---------------------------------------------------------------------
cadena_analisis = template_analisis | llm_gemini | StrOutputParser()

# ---------------------------------------------------------------------
# 4. CADENA DE RESUMEN LOCALIZADO (Cohere)
# ---------------------------------------------------------------------
template_respuesta = PromptTemplate(
    template="""
    Genera un resumen, utilizando un lenguaje claro y objetivo, enfocado en el publico colombiano.
    La idea es que la comunicacion del resultado sea lo mas sencilla posible, priorizando los registros para consultas posteriores.  
    
    # RESULTADO DE LA IMAGEN
    {respuesta_analisis_imagen}
    """,
    input_variables=["respuesta_analisis_imagen"]
)

cadena_resumen = template_respuesta | llm_cohere | StrOutputParser()

# ---------------------------------------------------------------------
# 5. ORQUESTACIÓN: CADENA COMPUESTA GLOBAL
# ---------------------------------------------------------------------
# Mapeamos la salida de la primera cadena para que encaje en la entrada de la segunda
cadena_compuesta = (
    cadena_analisis 
    | {"respuesta_analisis_imagen": RunnablePassthrough()} 
    | cadena_resumen
)

print("Iniciando pipeline compuesto (Gemini + Cohere)...")

# Ejecución final pasando las llaves exactas que exige tu template_analisis
resultado_final = cadena_compuesta.invoke({
    "pregunta": "Identifica los datos clave del gráfico.",
    "imagen_b64": imagen_base64
})

print("\n--- RESUMEN FINAL ADAPTADO (Cohere) ---")
print(resultado_final)