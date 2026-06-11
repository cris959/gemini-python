import socket
import json

# Forzar IPv4
orig_getaddrinfo = socket.getaddrinfo
def filtered_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
    return orig_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)
socket.getaddrinfo = filtered_getaddrinfo

# IMPORTS COMPLETAMENTE SEGUROS
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

# COMPONENTES LOCALES
from herramienta_analisis_imagen import HerramientaAnalisisImagen
from herramienta_explicar import HerramientaExplicar  # Nueva herramienta integrada
from my_models import GEMINI_FLASH
from my_keys import GEMINI_API_KEY


class AgenteOrquestador:
    def __init__(self):
        # Cerebro orquestador y clasificador
        self.llm = ChatGoogleGenerativeAI(
            api_key=GEMINI_API_KEY, 
            model=GEMINI_FLASH, 
            temperature=0
        )
        
        # Diccionario de herramientas registradas
        self.tool_imagen = HerramientaAnalisisImagen()
        self.tool_explicar = HerramientaExplicar()

    def ejecutar(self, consulta: str) -> dict:
        """
        Bucle ReAct con Enrutamiento Manual basado en el LLM.
        """
        print(f"\n🤔 [Pensamiento]: Analizando la intención del usuario...")
        
        # 1. Clasificación de la intención usando Gemini
        prompt_clasificador = ChatPromptTemplate.from_messages([
            ("system", (
                "Eres un enrutador de tareas experto. Tu trabajo es analizar la consulta del usuario "
                "e identificar cuál es la herramienta adecuada para responder.\n\n"
                "Opciones de herramientas disponibles:\n"
                "- 'HerramientaAnalisisImagen': Úsala si el usuario pide analizar, mirar o procesar un gráfico o imagen.\n"
                "- 'HerramientaExplicar': Úsala si el usuario te pide explícitamente que le expliques un tema pedagógicamente, como un profesor.\n\n"
                "Debes responder ESTRICTAMENTE en formato JSON plano con la siguiente estructura, sin rodeos, markdown o texto adicional:\n"
                '{{"herramienta": "NombreDeLaHerramienta", "parametro": "valor_de_entrada"}}'
            )),
            ("human", "{consulta_usuario}")
        ])
        
        cadena_clasificadora = prompt_clasificador | self.llm
        decision_raw = cadena_clasificadora.invoke({"consulta_usuario": consulta}).content
        
        # Intentamos parsear la decisión del LLM
        try:
            # Limpieza por si Gemini agrega bloques de código json ```json
            if "```" in decision_raw:
                decision_raw = decision_raw.split("```json")[-1].split("```")[0].strip()
            decision = json.loads(decision_raw)
        except Exception:
            # Fallback seguro en caso de error de parsing
            decision = {"herramienta": "HerramientaAnalisisImagen", "parametro": "datos/ejemplo_grafico.jpg"}

        herramienta_elegida = decision.get("herramienta")
        parametro_extrayido = decision.get("parametro")

        # 2. Ejecución dinámica de la herramienta seleccionada
        if herramienta_elegida == "HerramientaExplicar":
            print(f"🛠️ [Acción]: Invocando a 'HerramientaExplicar' (Cohere) para el tema: '{parametro_extrayido}'...")
            
            # Pasamos el formato JSON string esperado por ast.literal_eval
            arg_input = f"{{'tema': '{parametro_extrayido}'}}"
            resultado_final = self.tool_explicar._run(datos_entrada=arg_input)
            
            print("📝 [Observación]: Explicación didáctica generada por Cohere exitosamente.")
            return {"output": resultado_final}
            
        else:
            # Por defecto ejecuta la herramienta de imágenes
            print(f"🛠️ [Acción]: Invocando a 'HerramientaAnalisisImagen' (Gemini Vision)...")
            
            # Mantenemos tu ruta fija de desarrollo por seguridad
            ruta_imagen = "datos/ejemplo_grafico.jpg"
            resultado_herramienta_json = self.tool_imagen._run(nombre_imagen=ruta_imagen)
            
            print("📝 [Observación]: Datos estructurados de la imagen obtenidos correctamente.")
            print(f"🤖 [Pensamiento]: Procesando el informe final con Gemini...")
            
            prompt_final = ChatPromptTemplate.from_messages([
                ("system", "Asume el rol de un asistente analítico experto. Integra el JSON visual en tu respuesta."),
                ("human", "Solicitud original: {consulta_original}\n\nDatos de la herramienta:\n{datos_json}")
            ])
            
            cadena_final = prompt_final | self.llm
            respuesta_llm = cadena_final.invoke({
                "datos_json": resultado_herramienta_json,
                "consulta_original": consulta
            })
            
            return {"output": respuesta_llm.content}