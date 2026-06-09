

[![Visitor Badge](https://api.visitorbadge.io/api/VisitorHit?user=cris959&repo=gemini-python&countColor=linear-gradient(to%20right%2C%20%23a8ff00%200%25%2C%20%23933eff%20100%25))](https://www.github.com/cris959/gemini-python)

## Configuración e Integración de Gemini con LangChain
Este proyecto implementa orquestación de modelos de lenguaje independientes (Multi-Model Orchestration) utilizando LangChain, conectando de forma simultánea las APIs de Google Gemini y Cohere.

Debido a actualizaciones recientes en la arquitectura de las librerías y restricciones estrictas de infraestructura por parte del proveedor de Google, se debieron efectuar los siguientes cambios críticos para garantizar el correcto funcionamiento del entorno.

## 🛠️ Cambios y Correcciones Efectuadas
1. Migración de Imports a la Arquitectura Moderna
La estructura antigua de LangChain (langchain.prompts) generaba advertencias de deprecación o fallos de reconocimiento en el IDE. Se actualizaron los módulos hacia los paquetes independientes oficiales:

**Antes**: from langchain.prompts import ChatPromptTemplate

**Ahora**: from langchain_core.prompts import ChatPromptTemplate

2. Resolución del Bloqueo Regional de Cuota (**RESOURCE_EXHAUSTED 429**)
Al operar desde regiones con restricciones para el Free Tier de la API de Gemini (como Argentina), Google asigna por defecto una cuota de **limit: 0** peticiones, arrojando errores constantes de recursos agotados. Para solucionarlo sin pasar a un plan de pago obligatorio, se implementó un flujo de enmascaramiento:

* Fuga de IPv6 Mitigada: Se añadió un parche de red con el módulo **socket** nativo de Python al inicio del script para forzar que todo el tráfico saliente utilice estrictamente IPv4. Esto evita que los proveedores locales expongan la ubicación real por fuera del túnel.

* Túnel VPN Global: Se requiere la ejecución del script bajo una conexión VPN global apuntando a Estados Unidos (u otra región con la capa gratuita internacional habilitada que permite hasta 15 RPM).

* Nacionalidad de la API Key: La API Key de desarrollo debió ser generada dentro de un proyecto limpio en Google AI Studio iniciado desde una sesión de incógnito con la VPN activa, permitiendo que la clave herede los permisos del plan gratuito global.

3. Reestructuración de Prompts Multimodales en LangChain 3.x
Para el análisis de imágenes locales (conversión Base64), el formato del mensaje del usuario dentro del **ChatPromptTemplate** debió estructurarse explícitamente siguiendo el nuevo estándar de mensajes estructurados de LangChain:

* El bloque **"human"** ahora recibe un arreglo compuesto por un objeto estructurado de tipo **"text"** para la consulta y un objeto **"image_url"** que contiene el mapeo explícito de la clave interna **{"url": ...}** con el prefijo **data:image/jpeg;base64,**.

4. Consistencia en la Nomenclatura y Variables
Se aislaron las instancias de los modelos modificando variables genéricas por **llm_gemini** y **llm_cohere**. Esto previene colisiones o sobreescrituras accidentales en ejecuciones consecutivas y asegura que el análisis de imágenes sea derivado únicamente al motor de Google (Gemini 2.5 Flash / Lite), que cuenta con soporte multimodal nativo.

🚀 Flujo de Ejecución Local
Cada vez que se requiera probar o ejecutar el script **lang_chain.py**, se debe seguir este checklist:

1- Conectar el cliente **VPN** a un nodo de **Estados Unidos**.

2- Abrir una consola limpia y activar el entorno virtual correspondiente **(.venv-gemini-3\Scripts\activate)**.

3- Lanzar el comando: **python lang_chain.py**.

La VPN: es una extension de Google ==> UrbanVPN(gratuita)

P.D.: Le agradezco mucho las bases y la estructura brindadas en el curso, al Profesor **Álvaro Hernando Camacho Diaz**. Actualizar el código a las últimas versiones de LangChain y sortear las cuotas de las APIs fue un excelente desafío práctico para consolidar lo aprendido.

___
___

# Título del proyecto

2199 - Python y Gemini: Orquestando LLMs con LangChain

## 🔨 Funcionalidades del proyecto

En este proyecto, utilizaremos LangChain como framework principal para orquestar una solución integrada de análisis y organización de imágenes enriquecidas con anotaciones inteligentes. LangChain será empleado debido a su capacidad para conectar y gestionar flujos complejos que combinan IA multimodal y modelos de lenguaje, lo que permite un desarrollo más modular y escalable.

![](img/amostra.gif)

## ✔️ Técnicas y tecnologías utilizadas

Las técnicas y tecnologías utilizadas son:

- Programación en Python  
- Uso de la API Gemini  
- Uso del framework LangChain  
- Cadenas simples  
- Agente orquestador  
- Agente como herramientas  

## 🛠️ Abrir y ejecutar el proyecto

Después de descargar el proyecto, puedes abrirlo con Visual Studio Code. A continuación, es necesario preparar tu entorno. Para ello:

### venv en Windows:

```bash
python -m venv .venv-gemini-3
.\.venv-gemini-3\Scripts\activate
````

### venv en Mac/Linux:

```bash
python3 -m venv .venv-gemini-3
source .venv-gemini-3/bin/activate
```

Después, instala los paquetes utilizando:

```bash
pip install -r requirements.txt
```

## 🔑 Generar API\_KEYs y asociarlas al archivo .env

```python
GEMINI_API_KEY = "TU_API_KEY_AQUÍ"
COHERE_API_KEY = "TU_API_KEY_AQUÍ"
```