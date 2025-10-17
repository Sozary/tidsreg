# Guide : Utiliser Tidsreg avec ChatGPT Online

Ce guide explique comment configurer votre serveur Tidsreg pour l'utiliser avec ChatGPT online via un GPT personnalisé.

## Étape 1 : Déployer le serveur HTTP

Vous avez **deux options** pour rendre votre API accessible à ChatGPT :

### Option A : Localtunnel (Développement/Test rapide)

C'est la méthode la plus rapide pour tester, mais l'URL change à chaque redémarrage.

1. Démarrez le serveur HTTP :
```bash
python3 http_server.py
```

2. Dans un autre terminal, installez et lancez localtunnel :
```bash
npm install -g localtunnel
lt --port 8000
```

3. Vous recevrez une URL comme : `https://xyz-abc-123.loca.lt`
4. **Important** : La première fois que vous visitez l'URL, vous devrez accepter l'avertissement de sécurité

**Avantages** :
- Configuration ultra-rapide (2 minutes)
- Gratuit

**Inconvénients** :
- L'URL change à chaque redémarrage
- Moins stable pour une utilisation prolongée
- Nécessite de mettre à jour l'Action GPT à chaque nouveau démarrage

### Option B : ngrok (Meilleure alternative pour tests prolongés)

Similaire à localtunnel mais avec une URL stable sur un compte gratuit.

1. Inscrivez-vous sur [ngrok.com](https://ngrok.com) (gratuit)
2. Installez ngrok :
```bash
# macOS
brew install ngrok

# Ou téléchargez depuis https://ngrok.com/download
```

3. Authentifiez ngrok avec votre token :
```bash
ngrok config add-authtoken VOTRE_TOKEN
```

4. Démarrez le serveur HTTP :
```bash
python3 http_server.py
```

5. Dans un autre terminal, lancez ngrok :
```bash
ngrok http 8000
```

6. Vous recevrez une URL stable comme : `https://abc123.ngrok-free.app`

**Avantages** :
- URL stable (ne change pas)
- Plus fiable que localtunnel
- Gratuit pour un usage basique

**Inconvénients** :
- Nécessite une inscription
- Limite de bande passante sur le plan gratuit

### Option C : Déploiement Cloud (Production)

Pour une utilisation en production, déployez sur un serveur cloud :

#### Railway.app (Recommandé - Facile)

1. Inscrivez-vous sur [railway.app](https://railway.app)
2. Créez un nouveau projet
3. Connectez votre repo GitHub ou déployez directement
4. Railway détectera automatiquement Python et installera les dépendances
5. Configurez les variables d'environnement si nécessaire
6. Vous obtiendrez une URL HTTPS permanente

#### Autres options
- **Heroku** : Facile mais payant depuis 2022
- **DigitalOcean App Platform** : $5/mois minimum
- **AWS EC2** : Plus de contrôle mais configuration plus complexe
- **Google Cloud Run** : Paiement à l'usage

Pour toutes ces options, vous devrez :
1. Créer un `Procfile` ou configurer la commande de démarrage : `python3 http_server.py`
2. S'assurer que `requirements.txt` est à jour
3. Configurer le port (certains services utilisent la variable `PORT`)

## Étape 2 : Créer un GPT personnalisé

1. Allez sur [ChatGPT](https://chat.openai.com)
2. Cliquez sur votre nom en haut à droite
3. Sélectionnez "Mes GPTs" puis "Créer un GPT"
4. Cliquez sur "Configurer" (Configure)

### Configuration de base

**Nom** : `Tidsreg Assistant`

**Description** :
```
Assistant pour gérer et consulter les données Tidsreg - clients, projets, phases, activités et types.
```

**Instructions** :
```
Tu es un assistant spécialisé dans la gestion du système Tidsreg.

IMPORTANT - AUTHENTIFICATION :
- AVANT toute autre action, tu DOIS appeler l'action "login" avec les identifiants fournis par l'utilisateur
- Si l'utilisateur ne fournit pas ses identifiants, demande-les lui
- Après le login, confirme que l'authentification a réussi avant de continuer

WORKFLOW TYPIQUE :
1. Authentifier l'utilisateur avec login
2. Lister les clients disponibles avec listCustomers
3. Pour un client spécifique, lister ses projets avec listProjects
4. Pour un projet, lister ses phases avec listPhases
5. Pour une phase, lister ses activités avec listActivities
6. Pour une combinaison projet/activité, lister les types avec listKinds

RÈGLES :
- Toujours utiliser le format de date YYYY-MM-DD
- Si l'utilisateur demande "aujourd'hui", utilise la date du jour
- Présente les résultats de manière claire et structurée
- Si une erreur d'authentification survient, demande à l'utilisateur de se reconnecter
- Sois proactif : propose des actions suivantes logiques

TONALITÉ :
- Professionnel mais amical
- Clair et concis
- En français par défaut (sauf si l'utilisateur parle une autre langue)
```

**Starter Prompts** (suggestions de conversation) :
```
- "Connecte-toi à mon compte Tidsreg"
- "Montre-moi mes clients"
- "Quels projets ai-je pour le client X ?"
- "Liste les activités de la phase Y"
```

## Étape 3 : Configurer les Actions

1. Dans la section "Actions" de votre GPT, cliquez sur "Créer une nouvelle action"

2. Dans le champ "Schéma", collez le contenu du fichier `openapi.yaml`

3. **IMPORTANT** : Remplacez l'URL du serveur :
   - Trouvez la ligne : `url: https://your-url-here.loca.lt`
   - Remplacez par votre URL réelle (localtunnel, ngrok ou serveur cloud)
   - Exemple : `url: https://abc123.ngrok-free.app`

4. Configurez l'authentification :
   - Pour la plupart des cas : "None" (l'authentification se fait via l'endpoint `/api/login`)
   - Si vous ajoutez une authentification API supplémentaire plus tard, configurez-la ici

5. Définissez la politique de confidentialité :
   - URL : Vous pouvez laisser vide ou mettre une URL si vous en avez une
   - Cochez "Only me" si c'est pour votre usage personnel

6. Cliquez sur "Enregistrer"

## Étape 4 : Tester votre GPT

1. Dans le panneau de droite, commencez une conversation :
```
Connecte-toi avec le nom d'utilisateur "votre_username" et le mot de passe "votre_password"
```

2. Si tout fonctionne, le GPT devrait confirmer la connexion

3. Ensuite testez :
```
Montre-moi la liste de mes clients
```

4. Et continuez à naviguer dans la hiérarchie :
```
Quels projets ai-je pour le client [nom] ?
```

## Étape 5 : Publier votre GPT

1. Cliquez sur "Enregistrer" en haut à droite
2. Choisissez qui peut accéder à votre GPT :
   - **Moi uniquement** : Recommandé pour commencer
   - **Avec un lien** : Partager avec des collègues
   - **Public** : Disponible pour tous (nécessite un serveur de production sécurisé)

## Dépannage

### L'action échoue avec une erreur 401
- Vérifiez que vous avez appelé `/api/login` avec les bons identifiants
- Le serveur maintient une session, donc le login doit être fait en premier

### L'URL localtunnel ne fonctionne pas
- Visitez d'abord l'URL dans votre navigateur pour accepter l'avertissement
- Essayez de redémarrer localtunnel
- Vérifiez que le serveur HTTP tourne toujours

### Le GPT ne voit pas mes actions
- Vérifiez que le schéma OpenAPI est valide (pas d'erreurs JSON/YAML)
- Assurez-vous que l'URL du serveur est correcte dans le schéma
- Sauvegardez et rafraîchissez la page

### Erreur CORS
- Le serveur Flask a déjà CORS activé (`flask-cors`)
- Si vous utilisez un reverse proxy, assurez-vous qu'il autorise CORS

## Améliorations possibles

### Ajouter l'authentification à la configuration
Pour éviter de saisir le username/password à chaque fois, vous pouvez :

1. Modifier `http_server.py` pour utiliser un token API
2. Stocker le token dans les "Actions" du GPT sous "Authentication"
3. Implémenter une validation de token dans le serveur

### Ajouter plus de fonctionnalités
- Enregistrement du temps (POST endpoint)
- Statistiques et rapports
- Recherche avancée

### Sécurité pour la production
- Ajouter une authentification API avec tokens
- Implémenter des limites de taux (rate limiting)
- Utiliser HTTPS obligatoire
- Logger toutes les requêtes
- Chiffrer les mots de passe

## Ressources

- [Documentation OpenAI GPT Actions](https://platform.openai.com/docs/actions)
- [Spécification OpenAPI](https://swagger.io/specification/)
- [Documentation localtunnel](https://theboroer.github.io/localtunnel-www/)
- [Documentation ngrok](https://ngrok.com/docs)

## Support

Pour toute question ou problème, consultez :
- Le README.md du projet
- Les logs du serveur HTTP (ils s'affichent dans le terminal)
- L'onglet "Logs" dans votre GPT pour voir les erreurs d'API
