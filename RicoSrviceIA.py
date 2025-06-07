import os
import json
import re
from flask import Flask, request, jsonify
from mistralai import Mistral

app = Flask(__name__)

# Remplacez par votre clé API Mistral
api_key = os.environ["MISTRAL_API_KEY"]
model = "mistral-large-latest"

client = Mistral(api_key=api_key)

@app.route('/search_movies', methods=['POST'])
def search_movies():
    # Récupérer la requête utilisateur
    actor_name = request.json.get('actor', '')
    print("actor_name="+actor_name)

    # Construire la requête pour Mistral AI
    user_query1 = (
        f"Je veux une liste de tous les films avec l'acteur {actor_name}. "
        "Renvoie la réponse au format JSON avec les champs 'title' et 'id_imdb'. "
        "Par exemple : [{'title': 'Film A', 'id_imdb': 'tt1234567'}, {'title': 'Film B', 'id_imdb': 'tt7654321'}]."
    )

    user_query = (
        f"Paux tu me donner la liste des films ayant pour caractéristique :  {actor_name}. "
        "Renvoie la réponse au format JSON avec les champs 'title' et 'id_imdb'. "
        "Par exemple : [{'title': 'Film A', 'id_imdb': 'tt1234567'}, {'title': 'Film B', 'id_imdb': 'tt7654321'}]."
    )

    print("user_query="+user_query)

    # Interroger Mistral AI
    chat_response = client.chat.complete(
        model=model,
        messages=[
            {
                "role": "user",
                "content": user_query,
            },            
        ],
        stream=False
    )

    # Extraire et traiter la réponse
    response_content = chat_response.choices[0].message.content

    print("Réponse de Mistral AI :", response_content) 


    # First, extract content from ```json ... ``` block if present.
    # Mistral is prompted for raw JSON, but it might sometimes wrap it.
    extracted_json_string = extract_json_from_text(response_content, is_mongo_query=False)

    movies_list_final = None
    ai_response_error = False
    if extracted_json_string is not None:
        try:
            movies_list_final = json.loads(extracted_json_string)
        except json.JSONDecodeError as e_block:
            print(f"Erreur lors du décodage JSON du bloc extrait: {e_block}. Tentative de décodage direct de la réponse originale.")
            try:
                movies_list_final = json.loads(response_content)
            except json.JSONDecodeError as e_direct:
                print(f"Erreur lors du décodage JSON direct de response_content: {e_direct}")
                ai_response_error = True
    else:
        try:
            print("Aucun bloc JSON extrait (ou bloc vide), tentative de décodage JSON direct de response_content.")
            movies_list_final = json.loads(response_content)
        except json.JSONDecodeError as e_direct:
            print(f"Erreur lors du décodage JSON direct de response_content (aucun bloc valide trouvé): {e_direct}")
            ai_response_error = True

    if ai_response_error:
        return json.dumps({"error": "Failed to parse AI response"})

    imdb_ids = []
    if isinstance(movies_list_final, list):
        for movie in movies_list_final:
            if isinstance(movie, dict) and 'id_imdb' in movie and movie['id_imdb']:
                imdb_ids.append(movie['id_imdb'])

    query = {"imdb_id": {"$in": imdb_ids}}
    return json.dumps(query)



@app.route('/search_movies_sql', methods=['POST'])
def search_moviesSQL():  
    print(" search_moviesSQL Debut")
    # Récupérer la requête utilisateur
    requete = request.json.get('requete', '')
    print("requete="+requete)


	
    modeleDeRrequete = """db.getCollection('films').find(\{\{
    $and: [
    { \"credits.cast.name\": \"Keanu Reeves\" },
    { \"credits.cast.name"\: \"Ana de Armas\" },
    { \"release_date"\: { $gt: 2000-12-31 } }
    ]
    }"""
	

    # Construire la requête pour Mistral AI
    strure_doc_ricofilm = get_strure_doc_ricofilm();
    user_query = (
        f"J'ai une base MongoDb avec une collection FILMS."
        "je vais te donner la structure d'un document de cette collection : "
        f"La structure de document est celle ci : \"{strure_doc_ricofilm}\""
        f"Je vais te donner aussi une reqete en language naturel de recherche de films : {requete}. "
		f"Donne mois une requete de type :\"{modeleDeRrequete}\"."
        "Peux tu générer la requete pour MongoSQL qui répond aux exigencces de la requete"        
    )

    print("user_query="+user_query)

    # Interroger Mistral AI
    chat_response = client.chat.complete(
        model=model,
        messages=[
            {
                "role": "user",
                "content": user_query,
            },
        ]
    )

    response_content = chat_response.choices[0].message.content
    print("[----------------------------------------") 
    print("Réponse de Mistral AI :", response_content) 
    print("----------------------------------------]") 
    
    # json_string = extract_requete_mongi(response_content)    
    json_string = extract_json_from_text(response_content, is_mongo_query=True) # MODIFIED CALL
    print("Rsuktat=", json_string) 

    # Supposons que la réponse est déjà au format JSON
    # movies_list = json.loads(response_content)
    
    # If json_string is None, returning it directly might cause issues
    # or not match test expectations for the body to be the string "None".
    return str(json_string)


@app.route('/search_movies_web', methods=['POST'])
def search_movies_web():
    # Récupérer la requête utilisateur
    requete = request.json.get('requete', '')
    print("requete="+requete)

    # Construire la requête pour Mistral AI
    user_query = (
        f"la liste des films qui répondent à la requete: {requete}, la liste retour étant formatés au format json, ayant comme attribut : title, son numéro imbd. "
        "Par exemple : [{'title': 'Film A', 'id_imdb': 'tt1234567'}, {'title': 'Film B', 'id_imdb': 'tt7654321'}]."
    )

    print("user_query="+user_query)

    # Interroger Mistral AI
    chat_response = client.chat.complete(
        model=model,
        messages=[
            {
                "role": "user",
                "content": user_query,
            },
        ],
        stream=False
    )

    # Extraire et traiter la réponse
    response_content = chat_response.choices[0].message.content

    print("Réponse de Mistral AI :", response_content)


    # First, extract content from ```json ... ``` block if present.
    # Mistral is prompted for raw JSON, but it might sometimes wrap it.
    extracted_json_string = extract_json_from_text(response_content, is_mongo_query=False)

    movies_list_final = None
    if extracted_json_string is not None:
        try:
            movies_list_final = json.loads(extracted_json_string)
        except json.JSONDecodeError as e_block:
            print(f"Erreur lors du décodage JSON du bloc extrait: {e_block}. Tentative de décodage direct de la réponse originale.")
            # Fallback: if block parsing fails, try parsing original response_content directly
            try:
                movies_list_final = json.loads(response_content)
            except json.JSONDecodeError as e_direct:
                print(f"Erreur lors du décodage JSON direct de response_content: {e_direct}")
                return jsonify({"error": "Invalid AI response", "details": "JSON parsing failed for both extracted block and direct content."}), 500
    else:
        # If no ``` block was found by extract_json_from_text, try parsing response_content directly
        try:
            print("Aucun bloc JSON extrait (ou bloc vide), tentative de décodage JSON direct de response_content.")
            movies_list_final = json.loads(response_content)
        except json.JSONDecodeError as e_direct:
            print(f"Erreur lors du décodage JSON direct de response_content (aucun bloc valide trouvé): {e_direct}")
            return jsonify({"error": "Invalid AI response format", "details": "No valid JSON block found and direct parsing failed."}), 500

    return jsonify(movies_list_final)


def get_strure_doc_ricofilm():
    doc_ricofilm=(
    {
		"_id" : "",
		"adult" : "false",
		"backdrop_path" : "",
		"belongs_to_collection" : {
			"id" : "2344",
			"name" : "Matrix - Saga",
			"poster_path" : "a.jpg",
			"backdrop_path" : "b.jpg"
		},
		"budget" : "150000000",
		"genres" : [ 
			{
				"id" : "12",
				"name" : "Aventure"
			}
		],
		"homepage" : "",
		"id" : "604",
		"imdb_id" : "tt0234215",
		"original_language" : "en",
		"original_title" : "The Matrix Reloaded",
		"overview" : " résumé ... ",
		"popularity" : "26.855",
		"poster_path" : "c.jpg",
		"production_companies" : [ 
			{
				"id" : "79",
				"logo_path" : "e.png",
				"name" : "Village Roadshow Pictures",
				"origin_country" : "US"
			}
		],
		"production_countries" : [ 
			{
				"iso_3166_1" : "AU",
				"name" : "Australia"
			}
		],
		"release_date" : "2003-05-15",
		"revenue" : "738599701",
		"runtime" : "138",
		"spoken_languages" : [ 
			{
				"iso_639_1" : "en",
				"name" : "English"
			}
		],
		"status" : "Released",
		"tagline" : "Libérez votre esprit.",
		"title" : "Matrix Reloaded",
		"video" : "false",
		"vote_average" : "6.9",
		"vote_count" : "6995",
		"credits" : {
			"cast" : [ 
				{
					"cast_id" : "24",
					"character" : "Thomas A. Anderson / Neo",
					"credit_id" : "z",
					"gender" : "2",
					"id" : "6384",
					"name" : "Keanu Reeves",
					"order" : "0",
					"profile_path" : "f.jpg"
				}
			],
			"crew" : [ 
				{
					"credit_id" : "y",
					"department" : "Production",
					"gender" : "2",
					"id" : "1091",
					"job" : "Producer",
					"name" : "Joel Silver",
					"profile_path" : "null"
				}
			]
		},
		"videos" : {
			"results" : [ 
				{
					"id" : "x",
					"iso_639_1" : "fr",
					"iso_3166_1" : "FR",
					"key" : "0ha2XYVC7_s",
					"name" : "MATRIX RELOADED - Bande Annonce Officielle (VF) - Keanu Reeves / Laurence Fishburne / Wachowski",
					"site" : "YouTube",
					"size" : "480",
					"type" : "Trailer"
				}
			]
		},
		"RICO_FICHIER" : [ 
			{
				"serveur_name" : "NOS-RICO",
				"insertDate" : "2020-07-17T22:34:39.511Z",
				"path" : "/volume1/video/Films/2019/201903/",
				"file" : "The.Matrix.Reloaded.2003-1080p.FR.EN.x264.ac3.mHDgz.mkv",
				"size" : "3730300042.0",
				"fileDate" : "2019-03-23T17:52:14.000Z"
			}
		],
		"UPDATE_DB_DATE" : "2021-04-23T19:18:12.385Z"
	})
    return doc_ricofilm ;

def extract_requete_mongi(text):
    start_index = text.find("```json") + len("```json")
    print('extract_requete_mongi start_index='+str(start_index))
    if (start_index<0) : 
        start_index = text.find("```javascript") + len("```javascript")
    end_index = text.find("```", start_index)

    print("start_index ="+str(start_index))
    print("end_index ="+str(end_index))
    #Extraire et nettoyer la requête MongoDB
    mongo_query = text[start_index:end_index].strip()

    return mongo_query


def extract_json_from_text(text, is_mongo_query=False): # MODIFIED SIGNATURE
    print("extract_json_from_text : debut, is_mongo_query =", is_mongo_query)

    
    # Determine block type ('json' or 'javascript') more reliably
    found_block_type = None
    idx_json = text.find("```json")
    idx_js = text.find("```javascript")
    print("idx_json="+str(idx_json))
    print("idx_js="+str(idx_js))


    # Prioritize the block that appears first in the text
    if idx_json != -1 and (idx_js == -1 or idx_json > idx_js):
        found_block_type = 'json'
    elif idx_js != -1 and (idx_json == -1 or idx_js > idx_json):
        found_block_type = 'javascript'

    if not found_block_type:
        print("Aucun JSON/JavaScript ``` bloc trouvé dans le texte.")
        return None

    # Build pattern based on the determined block type
    pattern_str = r"```" + found_block_type + r"([\s\S]*?)```"
    pattern = re.compile(pattern_str, re.DOTALL)
    match = pattern.search(text)

    if match:
        json_string_from_block = match.group(1).strip()
        print("extract_json_from_text : extracted content from ``` block")

        if not is_mongo_query:
            return json_string_from_block # Return raw content if not a mongo query

        # Continue with MongoDB query parsing logic only if is_mongo_query is True
        print("extract_json_from_text : processing as MongoDB query")
        # Apply case conversion for 'films' collection name, specific to mongo query path
        processed_json_string = convert_films_to_lowercase(json_string_from_block)

        find_keyword = "db.getCollection('films').find("
        find_keyword_start_index = processed_json_string.find(find_keyword)

        if find_keyword_start_index != -1:
            actual_content_start_index = find_keyword_start_index + len(find_keyword)

            open_paren_count = 1
            correct_content_end_index = -1

            for i in range(actual_content_start_index, len(processed_json_string)):
                if processed_json_string[i] == '(':
                    open_paren_count += 1
                elif processed_json_string[i] == ')':
                    open_paren_count -= 1
                    if open_paren_count == 0:
                        correct_content_end_index = i
                        break

            if correct_content_end_index != -1:
                extracted_query_content = processed_json_string[actual_content_start_index:correct_content_end_index].strip()
                return extracted_query_content
            else:
                print("extract_json_from_text : No matching closing parenthesis found for find()")
                return None
        else:
            print(f"extract_json_from_text : '{find_keyword}' not found in the processed {found_block_type} block (after ``` extraction).")
            return None # If the specific find() structure isn't there, it's not a valid mongo query for this function.

    else:
        # This case should ideally be caught by the initial check for found_block_type
        print("Aucun JSON/JavaScript ``` bloc contenu trouvé avec regex (devrait être impossible ici).")
        return None

def convert_films_to_lowercase(text):
    """
    Convertit toutes les occurrences de 'FILMS' (insensible à la casse) en 'films'.
    
    :param text: La chaîne d'entrée.
    :return: La chaîne avec 'FILMS' remplacé par 'films'.
    """
    return re.sub(r'\bFILMS\b', 'films', text, flags=re.IGNORECASE)


def remove_trailing_parenthesis(text):
    """
    Supprime le caractère ')' si la chaîne se termine par ')'.
    
    :param text: La chaîne d'entrée.
    :return: La chaîne sans le caractère ')' à la fin.
    """
    if text.endswith(")"):
        return text[:-1]  # Supprime le dernier caractère
    return text


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000,debug=True)
