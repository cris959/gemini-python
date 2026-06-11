import socket

# Forzar a Python a usar únicamente IPv4 para las conexiones salientes (Evita bloqueo regional)
orig_getaddrinfo = socket.getaddrinfo
def filtered_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
    return orig_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)
socket.getaddrinfo = filtered_getaddrinfo

# Importamos únicamente tu orquestador modular
from orquestador import AgenteOrquestador

def main():
    # 1. Inicializamos el agente orquestador (él ya configura internamente el AgentExecutor y las herramientas)
    orquestador = AgenteOrquestador()
    
    # 2. Definimos la consulta apuntando explícitamente a la carpeta y extensión correctas
    # pregunta = "Por favor, realiza el análisis de la imagen ubicada en 'datos/ejemplo_grafico.jpg' y muéstrame el resultado estructurado."
    
    pregunta = "Explícame de forma didáctica qué es la programación orientada a objetos"
    
    print("🚀 Iniciando el Agente Orquestador ReAct...")
    print(f"Pregunta: {pregunta}\n" + "-"*50)
    
    # 3. Invocamos al agente a través de su método público encapsulado
    respuesta = orquestador.ejecutar(pregunta)
    
    # 4. Imprimimos el resultado final limpio en la consola
    print("\n" + "="*50)
    print("🏁 RESPUESTA FINAL DEL AGENTE")
    print("="*50)
    print(respuesta["output"])

# CORRECCIÓN: El bloque de entrada principal debe ir al mismo nivel que la función, sin sangría (fuera de main)
if __name__ == '__main__':
    main()