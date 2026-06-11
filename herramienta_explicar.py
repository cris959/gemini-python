from langchain.tools import BaseTool
from langchain_cohere import ChatCohere
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from my_keys import COHERE_API_KEY
import ast

class HerramientaExplicar(BaseTool):
    name: str = "HerramientaExplicar"
    description: str = """
    Utiliza esta herramienta siempre que sea solicitada la explicación de un contenido a las personas. 
    
    # ENTRADA REQUERIDA
    - 'tema' (str) : Tema principal informado en la pregunta del usuario.
    """
    return_direct: bool = True    
    
    def _run(self, datos_entrada: str) -> str:
        # Parseamos el string del argumento que envía el LLM/Orquestador
        try:
            datos_dict = ast.literal_eval(datos_entrada)
        except (ValueError, SyntaxError):
            # Por si el LLM envía el texto plano en lugar de un diccionario estructurado
            datos_dict = {"tema": datos_entrada}
            
        tema_parametro = datos_dict.get("tema", datos_entrada)
        
        # Inicializamos Cohere de forma correcta
        llm_cohere = ChatCohere(cohere_api_key=COHERE_API_KEY)
        
        # Usamos ChatPromptTemplate que es el que importaste y es compatible con LCEL
        template_respuesta = ChatPromptTemplate.from_template("""
            Asume el papel de un profesor experto en pedagogía y didáctica.  
            
            1. Elabora una explicación sobre el tema {tema} que sea de fácil comprensión para estudiantes de secundaria. 
            
            2. Utiliza ejemplos cotidianos para volver la explicación más sencilla.
            
            3. En caso de que surja algún recurso para apoyar la explicación, contextualízalo en el escenario del contexto colombiano.
            
            4. En caso de que presentes algún script de código, sé didáctico y utiliza Python.    
            
            Tema a explicar: {tema}
        """) 
        
        # Cadena LCEL pura (Funciona perfecto en tu Core 1.4.2)
        cadena = template_respuesta | llm_cohere | StrOutputParser()
        
        # Invocación pasando el parámetro limpio
        respuesta = cadena.invoke({"tema": tema_parametro})
        
        return respuesta