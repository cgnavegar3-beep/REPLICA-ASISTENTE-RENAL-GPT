from openai import OpenAI

# Sustituye con tu clave real de OpenAI
API_KEY = "TU_API_KEY_AQUI"

# Conectamos con OpenAI
client = OpenAI(api_key=API_KEY)

# Listamos todos los modelos disponibles
modelos = client.models.list()

print("=== Modelos disponibles ===")
for m in modelos.data:
    print(m.id)
