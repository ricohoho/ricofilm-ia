# CLAUDE.md — ricofilm-ia

## Vue d'ensemble

**ricofilm-ia** est un microservice IA de recherche de films. Il reçoit des requêtes en langage naturel, les traite via l'API Mistral AI, et retourne des résultats de films (titre + IMDB ID). Il s'insère dans l'architecture RicoFilm :

```
Nginx:80 → Frontend (4200) → Backend (3000) → ricofilm-ia (5000) → MongoDB
```

---

## Stack technique

- **Python / Flask 3.1.0** — framework web
- **Mistral AI SDK (mistralai==1.5.0)** — LLM pour interpréter les requêtes
- **Gunicorn 21.0.0** — serveur WSGI de production
- **python-dotenv** — gestion des variables d'environnement
- **flask-cors** — CORS autorisé pour `https://ricofilm.ricohoho.fr`
- **Docker** — conteneurisation
- **GitHub Actions** — CI/CD (tests → build image → déploiement SSH)

---

## Fichiers principaux

| Fichier | Rôle |
|---------|------|
| `RicoSrviceIA.py` | Application Flask principale, endpoints, intégration Mistral AI |
| `main.py` | Point d'entrée secondaire / tests d'extraction JSON |
| `requirements.txt` | Dépendances Python |
| `Dockerfile` | Image Docker, expose le port 5000, lance gunicorn |
| `go.sh` | Script de lancement via gunicorn |
| `.env` | `MISTRAL_API_KEY` et `MODEL_IA` (non versionné) |
| `.github/workflows/ci.yml` | Pipeline CI/CD |

---

## Endpoints API

### `GET /`
Health check.
```json
{"message": "Service is live"}
```

### `POST /search_movies`
Recherche par acteur → retourne une requête MongoDB.
```json
// Input
{"actor": "Tom Hanks"}
// Output
{"imdb_id": {"$in": ["tt0000001", ...]}}
```

### `POST /search_movies_sql`
Langage naturel → requête MongoDB string.
```json
// Input
{"requete": "films d'action des années 90"}
// Output
{"query": "db.getCollection('films').find({...})"}
```

### `POST /search_movies_web` *(endpoint principal)*
Langage naturel → liste de films.
```json
// Input
{"requete": "films de science-fiction avec Keanu Reeves"}
// Output
[
  {"title": "Matrix", "imdb_id": "tt0133093"},
  ...
]
```

---

## Variables d'environnement

```env
MISTRAL_API_KEY=<clé API Mistral>
MODEL_IA=mistral-small-latest   # optionnel, valeur par défaut
```

---

## Lancer le projet

```bash
# Installer les dépendances
pip install -r requirements.txt

# Lancer en développement
python RicoSrviceIA.py

# Lancer en production
./go.sh
# ou
gunicorn RicoSrviceIA:app --bind 0.0.0.0:5000
```

### Docker

```bash
docker build -t ricofilm-ia .
docker run -d --name ricofilm-iac -p 5000:5000 --env-file .env ricofilm-ia
```

---

## Notes d'implémentation

- **Extraction JSON robuste** : logique regex multi-fallback pour parser les réponses Mistral (blocs JSON, JS, etc.)
- **Logging des temps de réponse** : chaque appel Mistral est chronométré
- **Gestion d'erreurs** : messages d'erreur détaillés retournés en JSON
