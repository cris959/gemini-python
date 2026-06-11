import socket

# Forzar IPv4
orig_getaddrinfo = socket.getaddrinfo
def filtered_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
    return orig_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)
socket.getaddrinfo = filtered_getaddrinfo

# IMPORTS COMPLETAMENTE SEGUROS (Compatibles con tu Core viejo)
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

# COMPONENTES LOCALES
from herramienta_analisis_imagen import HerramientaAnalisisImagen
from my_models import GEMINI_FLASH
from my_keys import GEMINI_API_KEY


class AgenteOrquestador:
    def __init__(self):
        # 1. Inicializamos Gemini Flash de manera estable
        self.llm = ChatGoogleGenerativeAI(
            api_key=GEMINI_API_KEY, 
            model=GEMINI_FLASH, 
            temperature=0
        )
        
        # 2. Registramos tu herramienta modular
        self.tool = HerramientaAnalisisImagen()

    def ejecutar(self, consulta: str) -> dict:
        """
        Bucle de ejecución ReAct explícito. 
        Evita usar el Hub o clases de agentes rotas por la diferencia de versiones.
        """
        print(f"\n🤖 [Pensamiento]: El usuario quiere analizar una imagen. Usaré la herramienta especializada.")
        print(f"🛠️ [Acción]: Invocando a '{self.tool.name}'...")
        
        # Forzamos la ruta al directorio correcto para asegurar la lectura del archivo
        ruta_imagen = "datos/ejemplo_grafico.jpg"
        
        # Ejecutamos la lógica interna de tu herramienta directamente
        resultado_herramienta_json = self.tool._run(nombre_imagen=ruta_imagen)
        
        print("📝 [Observación]: Datos estructurados de la imagen obtenidos correctamente.")
        print(f"🤖 [Pensamiento]: Ahora procesaré estos datos con Gemini para la respuesta final.")
        
        # 3. Prompt de integración final (Reemplaza la necesidad de bajarse plantillas externas)
        prompt_final = ChatPromptTemplate.from_messages([
            (
                "system", 
                "Asume el rol de un asistente analítico experto. Tu objetivo es integrar de forma clara "
                "el análisis estructurado (JSON) que generó la herramienta en tu respuesta final para el usuario."
            ),
            (
                "human", 
                "Solicitud original del usuario: {consulta_original}\n\n"
                "Resultado obtenido por la herramienta de análisis visual:\n{datos_json}\n\n"
                "Por favor, redacta el informe final respondiendo de forma clara."
            )
        ])
        
        # Cadena directa LCEL
        cadena_final = prompt_final | self.llm
        
        respuesta_llm = cadena_final.invoke({
            "datos_json": resultado_herramienta_json,
            "consulta_original": consulta
        })
        
        # Devolvemos el diccionario con la estructura exacta que espera tu main.py original
        return {"output": respuesta_llm.content}