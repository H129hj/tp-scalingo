# Procedure de deploiement (reproductible)

Remplacer `hugo-tp-api` et `hugo-tp-client` par des noms uniques (les noms d'apps Scalingo sont globaux). Region : `osc-fr1` (Paris).

## 0. Prerequis (a faire toi-meme, une seule fois)
1. Voucher : partners.learn.ynov.com (compte Ynov) -> recuperer le voucher.
2. Compte sur scalingo.com, puis Billing -> Voucher (mettre fin a l'essai avec le bouton propose pour l'activer). Un profil de facturation et un moyen de paiement valides sont exiges.
3. CLI : https://doc.scalingo.com/platform/cli/start puis `scalingo login`, et ajouter ta cle SSH (`scalingo keys-add me ~/.ssh/id_ed25519.pub`).
4. Depot GitHub : `git init && git add . && git commit -m "feat: projet initial" && git branch -M main`, puis `gh repo create tp-scalingo --public --source=. --push` (ou depot cree a la main).

## 1. API + base
```bash
scalingo create hugo-tp-api --region osc-fr1
scalingo --app hugo-tp-api env-set PROJECT_DIR=api
scalingo --app hugo-tp-api env-set SECRET_KEY="$(python3 -c 'import secrets;print(secrets.token_urlsafe(48))')"
scalingo --app hugo-tp-api addons-add postgresql postgresql-starter-512
scalingo --app hugo-tp-api env-set CORS_ORIGINS=http://localhost:5173   # provisoire
scalingo --app hugo-tp-api git-setup && git push scalingo main
scalingo --app hugo-tp-api scale web:1:S
```
Controle : `curl https://hugo-tp-api.osc-fr1.scalingo.io/health` -> 200 et `/docs` affiche Swagger. Les migrations tournent via `postdeploy` (voir `scalingo --app hugo-tp-api logs --lines 100`).

> Monorepo : `git-setup` ajoute le remote `scalingo` ; si tu deploies deux apps depuis le meme depot, nomme les remotes : `git remote add scalingo-api git@ssh.osc-fr1.scalingo.com:hugo-tp-api.git` et `git remote add scalingo-client ...`, puis `git push scalingo-api main`.

## 2. Client
```bash
scalingo create hugo-tp-client --region osc-fr1
scalingo --app hugo-tp-client env-set PROJECT_DIR=client
scalingo --app hugo-tp-client env-set VITE_API_URL=https://hugo-tp-api.osc-fr1.scalingo.io   # AVANT le deploiement
git push scalingo-client main
scalingo --app hugo-tp-client scale web:1:S
# autoriser le client cote API
scalingo --app hugo-tp-api env-set CORS_ORIGINS=https://hugo-tp-client.osc-fr1.scalingo.io
```
Controle : ouvrir l'URL du client, creer un compte, ajouter une note, rafraichir `/notes` (pas de 404), recharger : la note est toujours la.

## 3. CI/CD
1. Les workflows `.github/workflows/api.yml` et `client.yml` lancent lint + tests + build, uniquement sur le dossier modifie.
2. Dashboard Scalingo de chaque app -> Deploy -> Automatic deployment : lier le depot GitHub, branche `main`, cocher **Wait for CI to succeed**.
3. Proteger `main` sur GitHub (Settings -> Branches : exiger les checks verts).
4. Test : ouvrir une PR qui casse un test (jamais en prod), la corriger, fusionner : deploiement automatique.
5. Bonus : activer les Review Apps (Deploy -> Review Apps).

## 4. Exploitation
- Logs : `scalingo --app hugo-tp-api logs --lines 200` (base : ajouter `--addon <id>`, id via `scalingo --app hugo-tp-api addons`).
- Panne volontaire a documenter : `scalingo --app hugo-tp-api env-unset SECRET_KEY` puis appeler `/auth/login` -> 500 ; les logs montrent `RuntimeError: SECRET_KEY est requis` ; correction : `env-set`.
- Rollback : `scalingo --app hugo-tp-api deployments` puis redeployer un ancien commit (`git push scalingo-api <sha>:main --force` ou depuis le dashboard : Deploy -> Deployments -> Redeploy).
- Sauvegarde/restauration : sauvegardes automatiques de l'addon (dashboard -> addon -> Backups) ; manuelle : `scalingo --app hugo-tp-api backups-create`, telechargement `backups-download`, restauration via `scalingo --app hugo-tp-api --addon <id> db-tunnel` + `pg_restore`.
- Metriques : dashboard -> Metrics (memoire, CPU, temps de reponse), ajuster la taille de conteneur ; couper en pause : `scalingo --app hugo-tp-api scale web:0`.
- Couts : Billing -> Consumption ; renseigner le reel dans le README.
