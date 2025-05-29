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

    # The response_content from Mistral for this route is expected to be a direct JSON string
    # representing a list of movies, e.g., "[{'title': 'Movie A', 'id_imdb': 'tt1234567'}]"
    # Therefore, we should parse it directly.
    try:
        movies_list = json.loads(response_content)
    except json.JSONDecodeError as e:
        print(f"Erreur lors du décodage JSON de la réponse de Mistral AI: {e}")
        # Return an error response or an empty list, depending on desired behavior
        return jsonify({"error": "Failed to parse AI response", "details": str(e)}), 500
    
    return jsonify(movies_list)


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
        f"Je vais te donner aussi une reqete en language naturel : {requete}. "
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
    json_string = extract_json_from_text(response_content)
    print("Rsuktat=", json_string) 

    # Supposons que la réponse est déjà au format JSON
    # movies_list = json.loads(response_content)
    
    # If json_string is None, returning it directly might cause issues
    # or not match test expectations for the body to be the string "None".
    return str(json_string)


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

def extract_json_from_text(text):
    print("extract_json_from_text : debut")
    
    # Determine block type ('json' or 'javascript') more reliably
    found_block_type = None
    idx_json = text.find("```json")
    idx_js = text.find("```javascript")

    # Prioritize the block that appears first in the text
    if idx_json != -1 and (idx_js == -1 or idx_json < idx_js):
        found_block_type = 'json'
    elif idx_js != -1 and (idx_json == -1 or idx_js < idx_json):
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
        print("extract_json_from_text : match content from ``` block")
        
        processed_json_string = convert_films_to_lowercase(json_string_from_block)
        
        find_keyword = "db.getCollection('films').find("
        find_keyword_start_index = processed_json_string.find(find_keyword)
        
        if find_keyword_start_index != -1:
            actual_content_start_index = find_keyword_start_index + len(find_keyword)
            
            open_paren_count = 1 
            correct_content_end_index = -1
            
            # Check if the character immediately preceding actual_content_start_index is indeed '('
            # This is implied by find_keyword ending in '('
            # We are looking for the matching ')' for this '('

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
                # This case means the find() part is malformed, e.g. db.getCollection('films').find({'actor': 'Test' 
                # (missing closing parenthesis)
                # Based on original tests, this should likely return what it can, even if malformed.
                # However, if we strictly need a balanced parenthesis, this should be None.
                # The previous failing tests (e.g. test_extract_json_from_text_malformed_json_block)
                # expected the malformed part.
                # Let's try to match that: if no closing paren for find() is found, return from start to end of string.
                # This is risky. A safer bet is to return None if structure is compromised.
                # The test 'test_extract_json_from_text_malformed_json_block' had expected: "{'name': 'test'"}".
                # The original code `end_index = len(json_string)-1` achieved this by chance.
                # For now, returning None for unclosed find() seems more robust.
                # If a test like test_extract_json_from_text_malformed_json_block expects partial recovery,
                # that test's expectation needs to be revisited.
                # For now, if find() is not properly closed, consider it unextractable.
                return None 
        else:
            print(f"extract_json_from_text : '{find_keyword}' not found in the extracted {found_block_type} block.")
            return None
    else:
        # This case should be caught by the initial check for found_block_type if it's working correctly
        print("Aucun JSON/JavaScript ``` bloc trouvé avec regex (devrait être impossible ici).")
        return None

def convert_films_to_lowercase(text):
    """
    Convertit toutes les occurrences de 'FILMS' (insensible à la casse) en 'films'.
    
    :param text: La chaîne d'entrée.
    :return: La chaîne avec 'FILMS' remplacé par 'films'.
    """
    return re.sub(r'\bFILMS\b', 'films', text, flags=re.IGNORECASE)




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000,debug=True)
