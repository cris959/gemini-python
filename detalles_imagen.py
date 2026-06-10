from pydantic import BaseModel, Field
from typing import List


class DetallesImagen(BaseModel):
    titulo:str = Field(
        description= "Define el titulo adecuado para la imagen analizada."
    )
    
    descripcion: str = Field(
        description= "Coloca aqui una descripcion del analisis de la imagen."
    )  
    # Añadimos restricciones de tamaño mínimo y máximo para obligar al LLM a cumplir las  "3" palabras clave
    etiquetas:List[str] = Field(
        min_items=3,
        max_items=3,
        description= "Define 3 palabras-clave para la imagen analizada."
    )