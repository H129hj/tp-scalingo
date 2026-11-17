# TP - Deploiement sur Scalingo

Application complete en production : client React/TypeScript, API FastAPI, base PostgreSQL managee, le tout en HTTPS sur Scalingo. Fonctionnalites : inscription, connexion (JWT), CRUD de notes par utilisateur.

## Architecture

```
Navigateur --HTTPS--> App 1 : client React (buildpack Node.js, build Vite, serve -s dist)
Navigateur --HTTPS--> App 2 : API FastAPI (buildpack Python, uvicorn sur $PORT) --SQL--> Addon PostgreSQL Starter 512
```

- Monorepo : `client/` et `api/`. Chaque app Scalingo cible son dossier via `PROJECT_DIR`.
- Le navigateur charge le client, puis appelle l'API directement. Seule l'API parle a la base.
- Conteneurs ephemeres : aucun fichier local n'est persiste, tout est en base.
- `Procfile` de l'API : `web` (uvicorn) et `postdeploy` (`alembic upgrade head`, migrations jouees apres chaque deploiement).

## Lancer en local

```bash
docker compose up -d                              # PostgreSQL
cd api && cp .env.example .env                    # renseigner SECRET_KEY
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head && uvicorn app.main:app --reload     # http://localhost:8000/docs
cd ../client && cp .env.example .env && npm install && npm run dev   # http://localhost:5173
```

## Variables d'environnement (sans valeurs)

| Projet | Variable | Role |
|---|---|---|
| API | `SCALINGO_POSTGRESQL_URL` | Fournie par l'addon, lue automatiquement |
| API | `DATABASE_URL` | Base locale / CI (ignoree si l'addon est present) |
| API | `SECRET_KEY` | Signature des JWT (a generer, jamais commitee) |
| API | `CORS_ORIGINS` | URL publique du client |
| API | `PROJECT_DIR` | `api` (Scalingo, monorepo) |
| API | `ACCESS_TOKEN_MINUTES` | Duree de validite du jeton (defaut 60) |
| Client | `VITE_API_URL` | URL publique de l'API, figee au build |
| Client | `PROJECT_DIR` | `client` (Scalingo, monorepo) |

## Deploiement

Voir [DEPLOY.md](DEPLOY.md) : procedure reproductible pas a pas, CI/CD, exploitation (logs, rollback, sauvegardes).

## Cout mensuel

Estimation (a verifier sur le simulateur de prix Scalingo et a remplacer par le reel) :

| Ressource | Quantite | Estimation |
|---|---|---|
| App API, conteneur S | 1 | ~7 EUR/mois |
| App client, conteneur S | 1 | ~7 EUR/mois |
| PostgreSQL Starter 512 | 1 | 7,2 EUR/mois (prix affiche Scalingo) |
| **Total estime** | | **~21 EUR/mois (< 50 EUR/mois du voucher Ynov)** |

Cout reel releve le : _a completer apres 1 semaine (Billing > Consumption)_.

## Justification des choix

- Deux apps separees (variante de base du sujet) : builds et deploiements independants, CORS limite au client.
- Hash de mot de passe PBKDF2 (stdlib) et JWT HS256 : peu de dependances pour un TP.
- `serve -s dist` : fallback SPA, un rafraichissement sur `/notes` ne renvoie pas 404.
