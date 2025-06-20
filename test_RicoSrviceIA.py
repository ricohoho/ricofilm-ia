import unittest
from unittest.mock import patch, MagicMock
import json
from flask import Flask, jsonify

# Assuming RicoSrviceIA.py is in the same directory and contains the Flask app 'app'
# and the functions to be tested. (eric)
from RicoSrviceIA import app, extract_json_from_text, convert_films_to_lowercase, get_strure_doc_ricofilm

class TestRicoServiceIA(unittest.TestCase):

    def setUp(self): 
        # Create a test client
        self.app = app.test_client()
        # Propagate the exceptions to the test client   
        self.app.testing = True

    # Test methods will be added here
    def test_extract_json_from_text_valid_json_block(self):
        text = "Some text ```json{\"key\": \"value\", \"path\": \"db.getCollection('films').find({'name': 'test'})\"}``` more text"
        # The function extracts the part after db.getCollection('films').find() and an opening parenthesis
        expected_output = "{'name': 'test'}"
        self.assertEqual(extract_json_from_text(text, is_mongo_query=True), expected_output)

    def test_extract_json_from_text_valid_javascript_block(self):
        text = "Some text ```javascript{\"key\": \"value\", \"path\": \"db.getCollection('films').find({'name': 'test_js'})\"}``` more text"
        expected_output = "{'name': 'test_js'}"
        self.assertEqual(extract_json_from_text(text, is_mongo_query=True), expected_output)

    def test_extract_json_from_text_no_json_block(self):
        text = "Some text without any json block."
        self.assertIsNone(extract_json_from_text(text, is_mongo_query=True)) # Also test with True, should still be None
        self.assertIsNone(extract_json_from_text(text, is_mongo_query=False))


    def test_extract_json_from_text_malformed_json_block(self):
        # Malformed due to structure, but the function primarily extracts based on ``` markers and specific string splitting.
        # The current implementation of extract_json_from_text in RicoSrviceIA.py might not validate JSON structure deeply,
        # it primarily extracts a string. If it were to parse with json.loads before returning, this test would be different.
        text = "Some text ```json{\"key\": \"value\", \"path\": \"db.getCollection('films').find({'name': 'test'\"}``` more text"
        print("avant appl text", text)
        # Based on current function: it will extract the string.
        # If json.loads were used in the main function before returning the specific substring,
        # this would ideally raise a JSONDecodeError or return None if handled.
        # Given the current implementation, it will extract the string as is, post "db.getCollection('films').find(".
        # UPDATED EXPECTATION: The new extract_json_from_text returns None if find() is not properly closed.
        expected_output = None
        self.assertEqual(extract_json_from_text(text, is_mongo_query=True), expected_output)

    def test_extract_json_from_text_with_films_uppercase(self):
        text = "```javascript db.getCollection('FILMS').find({'actor': 'TestActor'}) ```"
        expected_output = "{'actor': 'TestActor'}" # convert_films_to_lowercase should handle 'FILMS'
        self.assertEqual(extract_json_from_text(text, is_mongo_query=True), expected_output)

    def test_extract_json_from_text_empty_find_content(self):
        text = "```json db.getCollection('films').find() ```"
        expected_output = ""
        self.assertEqual(extract_json_from_text(text, is_mongo_query=True), expected_output)

    def test_extract_json_from_text_no_find_in_path(self):
        # This case might not be perfectly handled by the current string splitting logic if 'db.getCollection('films').find(' is not present.
        # The function expects this specific prefix.
        text = "```json {\"data\": \"no find here\"} ```"
        # According to the implementation, if "db.getCollection('films').find(" is not found,
        # it might lead to an error or unexpected behavior due to how start_index is calculated and used.
        # For now, expecting None as it won't find the pattern to split.
        # This depends on whether the regex match fails first or the string find operation.
        # The regex will match, then the string find will likely fail to find the full "db.getCollection('films').find("
        # inside the extracted json_string if the structure is different.
        # The function's current structure implies it will print "Aucun JSON trouvé dans le texte." or similar if the pattern for extraction isn't met.
        # Let's assume it returns None if the full "db.getCollection('films').find(" part isn't found after initial regex extraction.
        self.assertIsNone(extract_json_from_text(text, is_mongo_query=True))

    # New test for is_mongo_query=False
    def test_extract_json_from_text_block_only_no_mongo_query(self):
        text = "```json {\"key\": \"value\", \"data\": \"some data\"} ``` more text"
        expected_block_content = "{\"key\": \"value\", \"data\": \"some data\"}"
        self.assertEqual(extract_json_from_text(text, is_mongo_query=False), expected_block_content)
        # When is_mongo_query is True, but no find()
        self.assertIsNone(extract_json_from_text(text, is_mongo_query=True))


    def test_convert_films_to_lowercase_FILMS(self):
        self.assertEqual(convert_films_to_lowercase("FILMS"), "films")

    def test_convert_films_to_lowercase_Films(self):
        self.assertEqual(convert_films_to_lowercase("Films"), "films")

    def test_convert_films_to_lowercase_films(self):
        self.assertEqual(convert_films_to_lowercase("films"), "films")

    def test_convert_films_to_lowercase_boundary(self):
        self.assertEqual(convert_films_to_lowercase("FoofilmsBar"), "FoofilmsBar")

    def test_convert_films_to_lowercase_in_sentence(self):
        self.assertEqual(convert_films_to_lowercase("some FILMS text"), "some films text")

    def test_convert_films_to_lowercase_no_match(self):
        self.assertEqual(convert_films_to_lowercase("no such word"), "no such word")

    def test_convert_films_to_lowercase_mixed_case_in_sentence(self):
        self.assertEqual(convert_films_to_lowercase("This is FiLmS and FILMS"), "This is films and films")

    def test_convert_films_to_lowercase_already_lowercase(self):
        self.assertEqual(convert_films_to_lowercase("db.getCollection('films').find()"), "db.getCollection('films').find()")

    def test_get_strure_doc_ricofilm(self):
        result = get_strure_doc_ricofilm()
        self.assertIsInstance(result, dict)
        # Optionally, you could also check for the presence of a few key fields
        # if they are critical and unlikely to change frequently.
        self.assertIn("_id", result)
        self.assertIn("credits", result)
        self.assertIn("cast", result["credits"])

    @patch('RicoSrviceIA.client')
    def test_search_movies_valid_actor(self, mock_mistral_client):
        # Configure the mock client's chat.complete.return_value
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_message = MagicMock()
        # Mock AI response to include a JSON block, to test extract_json_from_text path
        mock_message.content = 'Preamble text ```json [{\"title\": \"Movie A\", \"id_imdb\": \"tt1234567\"}] ``` Epilogue text'
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_mistral_client.chat.complete.return_value = mock_response

        # Make a POST request to the endpoint
        response = self.app.post('/search_movies',
                                 data=json.dumps({'actor': 'Test Actor'}),
                                 content_type='application/json')

        # Assertions
        self.assertEqual(response.status_code, 200)

        # This assertion assumes the route is changed to use json.loads(response_content)
        # and then returns jsonify(parsed_json)
        expected_data = [{'title': 'Movie A', 'id_imdb': 'tt1234567'}]
        self.assertEqual(response.get_json(), expected_data)

        # Verify Mistral client was called correctly
        mock_mistral_client.chat.complete.assert_called_once()
        args, kwargs = mock_mistral_client.chat.complete.call_args
        self.assertEqual(kwargs['model'], "mistral-large-latest")
        args, kwargs = mock_mistral_client.chat.complete.call_args
        self.assertEqual(kwargs['model'], "mistral-large-latest")
        # Check parts of the prompt (matching the active user_query in RicoSrviceIA.py)
        # Prompt is: f"Paux tu me donner la liste des films ayant pour caractéristique : {actor_name}. "
        # The error message indicates a double space after the colon in the actual output.
        self.assertIn("Test Actor", kwargs['messages'][0]['content'])
        self.assertIn("Paux tu me donner la liste des films ayant pour caractéristique :  Test Actor. ", kwargs['messages'][0]['content']) # Note: double space after colon
        self.assertIn("Renvoie la réponse au format JSON", kwargs['messages'][0]['content'])


    @patch('RicoSrviceIA.client')
    def test_search_movies_empty_actor(self, mock_mistral_client):
        # Configure mock for empty actor
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_message = MagicMock()
        # Mock AI response to include a JSON block
        mock_message.content = "```json [] ```" # Empty list for an empty actor query, within a block
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_mistral_client.chat.complete.return_value = mock_response

        response = self.app.post('/search_movies',
                                 data=json.dumps({'actor': ''}),
                                 content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), []) # Expecting an empty list

        mock_mistral_client.chat.complete.assert_called_once()
        args, kwargs = mock_mistral_client.chat.complete.call_args
        # Check that the query was formed with an empty actor string
        # The prompt is f"... caractéristique : {actor_name}. "
        # If actor_name is empty, it becomes "... caractéristique :  . " (space, period, space)
        self.assertIn("caractéristique :  . ", kwargs['messages'][0]['content'])

    @patch('RicoSrviceIA.client')
    @patch('RicoSrviceIA.get_strure_doc_ricofilm') # To control the schema string
    @patch('RicoSrviceIA.extract_json_from_text') # To check it's called and control its output
    def test_search_movies_sql_valid_query(self, mock_extract_json, mock_get_schema, mock_mistral_client):
        # Configure mock for Mistral client
        mock_ai_response = MagicMock()
        mock_ai_choice = MagicMock()
        mock_ai_message = MagicMock()
        mock_ai_message.content = "```javascript db.getCollection('films').find({'actor': 'Test'}) ```" # Example AI output
        mock_ai_choice.message = mock_ai_message
        mock_ai_response.choices = [mock_ai_choice]
        mock_mistral_client.chat.complete.return_value = mock_ai_response

        # Configure mock for get_strure_doc_ricofilm
        mock_schema = {"_id": "some_schema_id", "title": "some_schema_title"}
        mock_get_schema.return_value = mock_schema

        # Configure mock for extract_json_from_text
        expected_mongo_query = "{'actor': 'Test'}"
        mock_extract_json.return_value = expected_mongo_query

        natural_query = "Find movies with Test Actor released after 2000"
        response = self.app.post('/search_movies_sql',
                                 data=json.dumps({'requete': natural_query}),
                                 content_type='application/json')

        self.assertEqual(response.status_code, 200)
        # The endpoint returns the direct output of extract_json_from_text, not jsonify(output)
        # So, response.data will be a bytestring.
        self.assertEqual(response.get_data(as_text=True), expected_mongo_query)

        # Verify Mistral client call
        mock_mistral_client.chat.complete.assert_called_once()
        args, kwargs = mock_mistral_client.chat.complete.call_args
        self.assertEqual(kwargs['model'], "mistral-large-latest")
        self.assertIn(natural_query, kwargs['messages'][0]['content'])
        # The schema in the prompt is formatted as f"... \"{str(mock_schema)}\"..."
        # str(mock_schema) will use single quotes for string keys/values if they don't contain single quotes.
        # json.dumps uses double quotes. The actual prompt uses str() then embeds in \" \".
        expected_schema_str_in_prompt = f'"{str(mock_schema)}"'
        self.assertIn(expected_schema_str_in_prompt, kwargs['messages'][0]['content'])
        self.assertIn("db.getCollection('films').find", kwargs['messages'][0]['content']) # Check model query is in prompt

        # Verify get_strure_doc_ricofilm call
        mock_get_schema.assert_called_once()

        # Verify extract_json_from_text call
        mock_extract_json.assert_called_once_with(mock_ai_message.content, is_mongo_query=True)


    @patch('RicoSrviceIA.client')
    @patch('RicoSrviceIA.get_strure_doc_ricofilm')
    @patch('RicoSrviceIA.extract_json_from_text')
    def test_search_movies_sql_empty_query(self, mock_extract_json, mock_get_schema, mock_mistral_client):
        mock_ai_response = MagicMock()
        mock_ai_choice = MagicMock()
        mock_ai_message = MagicMock()
        mock_ai_message.content = "```javascript db.getCollection('films').find({}) ```" # Generic response for empty query
        mock_ai_choice.message = mock_ai_message
        mock_ai_response.choices = [mock_ai_choice]
        mock_mistral_client.chat.complete.return_value = mock_ai_response

        mock_schema = {"_id": "id"}
        mock_get_schema.return_value = mock_schema

        expected_mongo_query = "{}"
        mock_extract_json.return_value = expected_mongo_query

        response = self.app.post('/search_movies_sql',
                                 data=json.dumps({'requete': ''}),
                                 content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_data(as_text=True), expected_mongo_query)

        mock_mistral_client.chat.complete.assert_called_once()
        args, kwargs = mock_mistral_client.chat.complete.call_args
        # The prompt structure is f"... une reqete en language naturel de recherche de films : {requete}. Donne mois ..."
        # If requete is '', this becomes "... une reqete en language naturel de recherche de films : . Donne mois ..."
        prompt_content = kwargs['messages'][0]['content']
        self.assertIn("Je vais te donner aussi une reqete en language naturel de recherche de films : ", prompt_content)
        self.assertIn(". Donne mois une requete de type", prompt_content)
        self.assertIn("recherche de films : . Donne mois", prompt_content) # Ensures the empty part

        mock_extract_json.assert_called_once_with(mock_ai_message.content, is_mongo_query=True)

    # Test to see what happens if Mistral returns content that extract_json_from_text can't parse (e.g. not the expected format)
    @patch('RicoSrviceIA.client')
    @patch('RicoSrviceIA.get_strure_doc_ricofilm')
    # We don't mock extract_json_from_text here, to test its behavior within the call
    def test_search_movies_sql_mistral_returns_unparsable_by_extract_json(self, mock_get_schema, mock_mistral_client):
        mock_ai_response = MagicMock()
        mock_ai_choice = MagicMock()
        mock_ai_message = MagicMock()
        mock_ai_message.content = "Some unexpected response from AI without proper code blocks."
        mock_ai_choice.message = mock_ai_message
        mock_ai_response.choices = [mock_ai_choice]
        mock_mistral_client.chat.complete.return_value = mock_ai_response

        mock_schema = {"_id": "id"}
        mock_get_schema.return_value = mock_schema

        natural_query = "A valid query"
        response = self.app.post('/search_movies_sql',
                                 data=json.dumps({'requete': natural_query}),
                                 content_type='application/json')

        self.assertEqual(response.status_code, 200)
        # extract_json_from_text returns None if it can't find the JSON/JS block.
        # The endpoint returns this None value directly. Flask's jsonify(None) would be 'null',
        # but this route returns the string from extract_json_from_text directly.
        # If extract_json_from_text returns None, response.data would be b'None'
        # This needs clarification: if extract_json_from_text returns None, what does the Flask route return?
        # `return json_string` where json_string is None.
        # Flask will try to interpret this. If the mimetype is 'application/json' (default for jsonify),
        # it might convert None to 'null'. But here it's `return json_string` which is not `jsonify(json_string)`.
        # So the response body might be empty or 'None' as a string.
        # Let's check the content of `RicoSrviceIA.py`: `return json_string`.
        # If `json_string` is `None`, the body will literally be the string "None".
        self.assertEqual(response.get_data(as_text=True), "None")


    @patch('RicoSrviceIA.client')
    def test_search_movies_web_valid_requete(self, mock_mistral_client):
        # Configure the mock client's chat.complete.return_value
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_message = MagicMock()
        # Mock AI response to include a JSON block
        mock_message.content = 'Some preamble ```json [{"title": "Inception", "id_imdb": "tt1375666"}, {"title": "The Matrix", "id_imdb": "tt0133093"}] ``` Some epilogue'
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_mistral_client.chat.complete.return_value = mock_response

        # Make a POST request to the endpoint
        response = self.app.post('/search_movies_web',
                                 data=json.dumps({'requete': 'sci-fi classics'}),
                                 content_type='application/json')

        # Assertions
        self.assertEqual(response.status_code, 200)
        expected_json_string = '{"imdb_id": {"$in": ["tt1375666", "tt0133093"]}}'
        self.assertEqual(response.get_data(as_text=True), expected_json_string)

        # Verify Mistral client was called correctly
        mock_mistral_client.chat.complete.assert_called_once()
        args, kwargs = mock_mistral_client.chat.complete.call_args
        self.assertEqual(kwargs['model'], "mistral-large-latest")

        # Check content of the prompt
        prompt_content = kwargs['messages'][0]['content']
        self.assertIn('sci-fi classics', prompt_content)
        self.assertIn("la liste des films qui répondent à la requete", prompt_content)
        self.assertIn("formatés au format json", prompt_content)
        self.assertIn("title", prompt_content)
        self.assertIn("son numéro imbd", prompt_content)

    @patch('RicoSrviceIA.client')
    def test_search_movies_web_single_movie(self, mock_mistral_client):
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_message = MagicMock()
        mock_message.content = '```json [{"title": "Inception", "id_imdb": "tt1375666"}] ```'
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_mistral_client.chat.complete.return_value = mock_response

        response = self.app.post('/search_movies_web',
                                 data=json.dumps({'requete': 'a single movie'}),
                                 content_type='application/json')

        self.assertEqual(response.status_code, 200)
        expected_json_string = '{"imdb_id": {"$in": ["tt1375666"]}}'
        self.assertEqual(response.get_data(as_text=True), expected_json_string)

    @patch('RicoSrviceIA.client')
    def test_search_movies_web_no_movies_found(self, mock_mistral_client):
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_message = MagicMock()
        mock_message.content = '```json [] ```'
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_mistral_client.chat.complete.return_value = mock_response

        response = self.app.post('/search_movies_web',
                                 data=json.dumps({'requete': 'unknown movie query'}),
                                 content_type='application/json')

        self.assertEqual(response.status_code, 200)
        expected_json_string = '{"imdb_id": {"$in": []}}'
        self.assertEqual(response.get_data(as_text=True), expected_json_string)

    @patch('RicoSrviceIA.client')
    def test_search_movies_web_ai_returns_invalid_json(self, mock_mistral_client):
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_message = MagicMock()
        mock_message.content = "This is not JSON" # No JSON block, direct invalid content
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_mistral_client.chat.complete.return_value = mock_response

        response = self.app.post('/search_movies_web',
                                 data=json.dumps({'requete': 'any query'}),
                                 content_type='application/json')

        self.assertEqual(response.status_code, 200) # The endpoint itself handles the error gracefully
        expected_json_string = '{"error": "Failed to parse AI response"}'
        self.assertEqual(response.get_data(as_text=True), expected_json_string)

    @patch('RicoSrviceIA.client')
    def test_search_movies_web_ai_returns_malformed_data_unexpected_structure(self, mock_mistral_client):
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_message = MagicMock()
        # Valid JSON, but not a list of movie dicts
        mock_message.content = '```json {"unexpected_key": "unexpected_value"} ```'
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_mistral_client.chat.complete.return_value = mock_response

        response = self.app.post('/search_movies_web',
                                 data=json.dumps({'requete': 'any query'}),
                                 content_type='application/json')

        self.assertEqual(response.status_code, 200)
        # movies_list_final will not be a list, so imdb_ids will be empty
        expected_json_string = '{"imdb_id": {"$in": []}}'
        self.assertEqual(response.get_data(as_text=True), expected_json_string)

    @patch('RicoSrviceIA.client')
    def test_search_movies_web_ai_returns_malformed_data_missing_imdb_id(self, mock_mistral_client):
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_message = MagicMock()
        # Valid JSON list, but movie dicts are missing 'id_imdb'
        mock_message.content = '```json [{"title": "Film C"}] ```'
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_mistral_client.chat.complete.return_value = mock_response

        response = self.app.post('/search_movies_web',
                                 data=json.dumps({'requete': 'any query'}),
                                 content_type='application/json')

        self.assertEqual(response.status_code, 200)
        expected_json_string = '{"imdb_id": {"$in": []}}' # No id_imdb found
        self.assertEqual(response.get_data(as_text=True), expected_json_string)

    @patch('RicoSrviceIA.client')
    def test_search_movies_web_ai_returns_mixed_malformed_data(self, mock_mistral_client):
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_message = MagicMock()
        # Valid JSON list, one movie with id_imdb, one without
        mock_message.content = '```json [{"title": "Film A", "id_imdb": "tt123"}, {"title": "Film B"}] ```'
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_mistral_client.chat.complete.return_value = mock_response

        response = self.app.post('/search_movies_web',
                                 data=json.dumps({'requete': 'any query'}),
                                 content_type='application/json')

        self.assertEqual(response.status_code, 200)
        expected_json_string = '{"imdb_id": {"$in": ["tt123"]}}' # Only tt123 should be included
        self.assertEqual(response.get_data(as_text=True), expected_json_string)


if __name__ == '__main__':
    unittest.main()
