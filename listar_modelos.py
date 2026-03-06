from openai import OpenAI
import os

# Asegúrate de tener tu API Key en la variable de entorno OPENAI_API_KEY
API_KEY = os.getenv("OPENAI_API_KEY")

if not API_KEY:
    print("⚠️ No se ha encontrado la API Key en la variable de entorno.")
    exit(1)

client = OpenAI(api_key=API_KEY)

try:
    modelos = client.models.list()
    print("=== Modelos disponibles ===")
    for modelo in modelos.data:
        print(modelo.id)
except Exception as e:
    print("Error al listar modelos:", e)
