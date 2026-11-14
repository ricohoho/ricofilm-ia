import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.environ.get("OPENROUTER_API_KEY")
model = os.environ.get("MODEL_IA", "openrouter/free")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
)

print(f"Testing model '{model}' via OpenRouter...")
response = client.chat.completions.create(
    model=model,
    messages=[
        {"role": "user", "content": "Peux-tu me donner le titre et l'année du film Matrix ?"}
    ],
)
print("Réponse reçue :")
print(response.choices[0].message.content)
