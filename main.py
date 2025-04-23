import os
import json
import re

print("Bonjour, monde !")

def extract_json_from_text(text,atrouver):
    print("extract_json_from_text : debut:"+atrouver)
    """
    Extrait et décode une chaîne JSON intégrée dans un texte.
    :param text: Texte contenant du JSON intégré.
    :return: Structure Python décodée à partir du JSON.
    """
    # Expression régulière pour extraire le JSON
    if (atrouver=='javascript'):
        json_pattern = re.compile(r'```javascript(.*?)```', re.DOTALL)
    else :
        json_pattern = re.compile(r'```json(.*?)```', re.DOTALL)

    # Rechercher le JSON dans le texte
    match = json_pattern.search(text)

    if match:
        print("extract_json_from_text : match")
        json_string = match.group(1).strip()  # Extraire et nettoyer la chaîne JSON
        print("json_string:"+json_string)
        try:
            # Décoder la chaîne JSON en une structure Python
            # data = json.loads(json_string)
            #return data
            start_index = json_string.find("db.getCollection('films').find(") + len("db.getCollection('films').find(")+1
            end_index = len(json_string)-1
            json_string = json_string[start_index:end_index].strip()
            return json_string
        except json.JSONDecodeError as e:
            print("Erreur lors du décodage JSON :", e)
            return None
    else:
        print("Aucun JSON trouvé dans le texte.")
        return None


result = extract_json_from_text("```json {hoho:hoho} ```","json")
print("resultat ="+str(result))

stest=(f"Réponse de Mistral AI : Bien sûr, je peux vous aider à générer la requête MongoDB pour trouver les films avec l'acteur ""Stalonne"" (je suppose que vous vouliez dire ""Sylvester Stallone"") et les autres conditions spécifiées. Voici la requête MongoDB correspondante :"
"```javascript"
"db.getCollection('FILMS').find({"
"    $and: ["
"        { ""credits.cast.name"": ""Sylvester Stallone"" },"
"        { ""release_date"": { $gt: ""2000-12-31"" } }"
"    ]"
"})"
"```"
""
"Cette requête recherche les documents dans la collection `FILMS` où :"
"1. L'acteur 'Sylvester Stallone' est présent dans le casting (`credits.cast.name`)."
"2. La date de sortie (`release_date`) est postérieure au 31 décembre 2000."
""
"Assurez-vous que les champs et les valeurs dans votre base de données correspondent exactement à ceux utilisés dans la requête. Par exemple, si les noms des acteurs sont stockés avec des variations de casse ou des espaces, vous devrez peut-être ajuster la requête en conséquence."
)
print("test ="+stest)
result = extract_json_from_text(stest,"javascript")
print("resultat ="+str(result))