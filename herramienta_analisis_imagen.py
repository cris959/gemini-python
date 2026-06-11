from langchain_core.tools import BaseTool
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

# Módulos locales de tu proyecto
from my_models import GEMINI_FLASH
from my_keys import GEMINI_API_KEY
from my_helper import encode_image
from detalles_imagen import DetallesImagen

class HerramientaAnalisisImagen(BaseTool):
    name: str = "HerramientaAnalisisImagen"
    description: str = """
    Utiliza esta herramienta siempre que te sea solicitado realizar un analisis de imagen. 
    
    # ENTRADAS REQUERIDAS
    - 'nombre_imagen' (str) : Nombre o ruta relativa del archivo de imagen a ser analizada con extension JPG o JPEG.
    Ejemplo: datos/ejemplo_grafico.jpg
    """
    return_direct: bool = False    
    
    def _run(self, nombre_imagen: str) -> str:
        """
        Lógica interna que ejecuta la herramienta cuando el Agente la invoca.
        Procesa la imagen de forma multimodal y devuelve la estructura Pydantic en formato JSON.
        """
        try:
            # 1. Limpiar el argumento de posibles comillas que el LLM agregue por error
            ruta_limpia = nombre_imagen.strip("'\"")
            
            # 2. Inicializar el modelo con salida estructurada (Pydantic)
            llm_gemini = ChatGoogleGenerativeAI(
                api_key=GEMINI_API_KEY, 
                model=GEMINI_FLASH
            )
            llm_estructurado = llm_gemini.with_structured_output(DetallesImagen)
            
            # 3. Codificar la imagen local a Base64
            imagen_base64 = encode_image(ruta_limpia)
            
            # 4. Estructurar el prompt multimodal para LangChain 3.x
            template_analisis = ChatPromptTemplate.from_messages([
                (
                    "system", 
                    "Asume que eres un analista de imagenes estrictamente objetivo. Tu tarea es extraer la informacion visual clave."
                ),
                (
                    "human", 
                    [
                        {"type": "text", "text": "Analiza detalladamente este gráfico por completo."},
                        {
                            "type": "image_url", 
                            "image_url": {"url": f"data:image/jpeg;base64,{imagen_base64}"}
                        }
                    ]
                )
            ])
            
            # 5. Construir y ejecutar la mini-cadena LCEL interna
            cadena = template_analisis | llm_estructurado
            resultado = cadena.invoke({"imagen_b64": imagen_base64})
            
            # 6. Devolver el resultado serializado como string JSON para la observación del agente
            return resultado.model_dump_json(indent=2)
            
        except Exception as e:
            # Si el archivo no existe o falla la API, se le informa textualmente al agente para que decida qué hacer
            return f"Error al ejecutar HerramientaAnalisisImagen: No se pudo procesar el archivo '{nombre_imagen}'. Detalle del error: {str(e)}"