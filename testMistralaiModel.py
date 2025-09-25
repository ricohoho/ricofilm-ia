import os
from mistralai import Mistral

API_KEY = os.environ["MISTRAL_API_KEY"]
client = Mistral(api_key=API_KEY)

# Liste des modèles disponibles (à adapter selon ta documentation)
models_to_test = ["mistral-tiny", "mistral-small", "mistral-small-latest", "mistral-large-latest"]    

for model in models_to_test:
    try:
        response = client.chat.complete(
            model=model,
            messages=[{"role": "user", "content": "Test de disponibilité"}],
        )
        print(f"✅ {model} fonctionne : {response.choices[0].message.content[:20]}...")
    except Exception as e:
        print(f"❌ {model} ne fonctionne pas : {e}")