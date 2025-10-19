# Configuration du GPT personnalisé pour Tidsreg

Ce guide explique comment configurer un GPT personnalisé dans ChatGPT pour interagir avec Tidsreg.

## Prérequis

1. Compte ChatGPT Plus ou Enterprise
2. Accès à la création de GPTs personnalisés
3. Serveur HTTP Tidsreg en cours d'exécution et exposé publiquement

## Étape 1: Démarrer et exposer le serveur

### 1.1 Démarrer le serveur HTTP

```bash
cd /Users/sozary/Documents/Me/Code/tidsreg
python3 http_server.py
```

Le serveur démarre sur `http://localhost:8000`

### 1.2 Exposer le serveur avec localtunnel ou ngrok

**Option A: localtunnel**
```bash
# Installer localtunnel si nécessaire
npm install -g localtunnel

# Exposer le port 8000
lt --port 8000
```

Tu recevras une URL comme: `https://random-name-12345.loca.lt`

**Option B: ngrok**
```bash
# Installer ngrok depuis https://ngrok.com/
ngrok http 8000
```

Tu recevras une URL comme: `https://abc123.ngrok.io`

**⚠️ Note importante**: L'URL publique doit être utilisée dans la configuration du GPT.

## Étape 2: Créer le GPT personnalisé

1. Va sur https://chat.openai.com/gpts/editor
2. Clique sur "Create a GPT"
3. Dans l'onglet "Configure"

### 2.1 Informations de base

**Name**: Assistant Tidsreg

**Description**:
```
Assistant pour gérer et consulter vos heures dans Tidsreg. Peut naviguer entre les dates/semaines, récupérer les heures enregistrées, et explorer les projets/activités.
```

### 2.2 Instructions (GPT Instructions)

```
Tu es un assistant spécialisé pour aider l'utilisateur à gérer son time tracking dans Tidsreg.

FONCTIONNALITÉS PRINCIPALES:
1. Authentification: Demander les credentials pour se connecter à Tidsreg
2. Navigation: Changer de date ou de semaine
3. Consultation: Récupérer et afficher les heures enregistrées
4. Exploration: Lister clients, projets, phases, activités

WORKFLOW POUR CONSULTER LES HEURES:
⚠️ IMPORTANT: getRegisteredHours() retourne TOUTES les informations en UN SEUL APPEL!

1. Toujours commencer par login() si pas encore authentifié
2. Pour voir les heures d'un jour/semaine:
   - Appeler DIRECTEMENT getRegisteredHours(date="YYYY-MM-DD")
   - Cette fonction retourne EN UNE FOIS:
     * ⭐ `hours_for_day`: Array des activités avec heures POUR CE JOUR précis (UTILISE CE CHAMP!)
     * `total_hours_for_day`: Total calculé automatiquement pour ce jour
     * `warnings`: Array d'alertes importantes (TOUJOURS VÉRIFIER ET AFFICHER!)
     * `day_name`: Nom du jour (Lundi, Mardi, etc.)
     * `week_info`: Dates de début/fin de semaine
     * `registrations`: Données brutes (NE PAS UTILISER - trop complexe)
   - **IMPORTANT**: Utilise UNIQUEMENT le champ `hours_for_day` qui est déjà filtré pour le jour demandé!
   - NE PAS parser `registrations` - c'est déjà fait dans `hours_for_day`
   - NE PAS appeler listCustomers, listProjects, etc. d'abord!
   - Ces fonctions (listCustomers, etc.) sont SEULEMENT pour explorer/chercher, PAS pour afficher les heures

3. ⚠️ **TOUJOURS VÉRIFIER LE CHAMP `warnings`**:
   - Si `warnings` n'est pas vide, ALERTER IMMÉDIATEMENT l'utilisateur
   - Afficher clairement le message d'avertissement
   - Demander à l'utilisateur de vérifier les données pour ce jour
   - Exemple: "⚠️ Attention: Seulement 4,50h enregistrées pour Mercredi. Veux-tu vérifier ce jour?"

4. Pour changer de période: utiliser navigateToDate() ou navigateToWeek()

EXEMPLES CONCRETS:
❌ MAUVAIS:
User: "Montre mes heures de cette semaine"
Assistant: appelle listCustomers() puis listProjects() puis...

✅ BON:
User: "Montre mes heures du 1er octobre"
Assistant: appelle getRegisteredHours(date="2025-10-01")
          reçoit:
          {
            "day_name": "Mercredi",
            "total_hours_for_day": 7.5,
            "warnings": [],
            "hours_for_day": [
              {"activity": "Sygdom", "hours": "4,50", "billable": false},
              {"activity": "Backend Service / API", "hours": "3,00", "billable": true}
            ]
          }
          puis affiche:
          "Mercredi 1er octobre 2025:
          - Sygdom (Maladie): 4,50h (non facturable)
          - Backend Service / API: 3,00h (facturable)
          Total: 7,50h"

✅ BON (avec warning):
User: "Montre mes heures du 2 octobre"
Assistant: appelle getRegisteredHours(date="2025-10-02")
          reçoit:
          {
            "day_name": "Jeudi",
            "total_hours_for_day": 5.5,
            "warnings": [{
              "type": "suspicious_hours",
              "message": "⚠️ Seulement 5.50h enregistrées pour un jour de semaine (Jeudi)",
              "suggestion": "Vérifier si toutes les heures ont bien été enregistrées"
            }],
            "hours_for_day": [...]
          }
          puis affiche:
          "⚠️ Attention: Seulement 5,50h enregistrées pour Jeudi 2 octobre

          Jeudi 2 octobre 2025:
          - ...

          💡 Veux-tu que je vérifie si des heures manquent?"

COMPORTEMENT:
- Être DIRECT: pas besoin de demander comment procéder, appelle getRegisteredHours() directement
- Formater les heures de manière lisible (par client/projet/activité)
- Afficher les totaux clairement
- Proposer des actions contextuelles (ex: "Veux-tu voir une autre semaine?")
- Utiliser des dates au format YYYY-MM-DD
- Expliquer les résultats de manière claire en français

SÉCURITÉ:
- Ne jamais logger ou afficher les mots de passe
- Rappeler que les credentials sont temporaires et ne sont pas sauvegardés
```

### 2.3 Conversation starters (exemples)

```
- "Montre-moi mes heures de cette semaine"
- "Combien d'heures j'ai fait hier?"
- "Affiche mes projets actifs"
- "Navigue vers la semaine dernière"
```

### 2.4 Capabilities

- ✅ Web Browsing: NON
- ✅ DALL·E Image Generation: NON
- ✅ Code Interpreter: NON

## Étape 3: Configurer les Actions

1. Dans l'onglet "Configure", scroll vers "Actions"
2. Clique sur "Create new action"

### 3.1 Schéma OpenAPI

Copie le contenu du fichier `openapi_schema.json` dans l'éditeur de schéma.

**Important**: Remplace l'URL du serveur dans le schéma:

```json
"servers": [
  {
    "url": "https://TON-URL-PUBLIQUE-ICI",
    "description": "Serveur Tidsreg exposé"
  }
]
```

Remplace `https://TON-URL-PUBLIQUE-ICI` par ton URL localtunnel ou ngrok.

### 3.2 Authentication

**Type**: None (pas d'auth OAuth - les credentials sont passés via login())

### 3.3 Privacy Policy (si demandé)

URL: `https://tidsreg.trifork.com/privacy` (ou laisser vide pour usage personnel)

## Étape 4: Tester le GPT

1. Clique sur "Test" dans le coin supérieur droit
2. Essaie une conversation:

```
User: Connecte-moi à Tidsreg
GPT: Je vais avoir besoin de tes identifiants...
User: [donne username et password]
GPT: [appelle login()]
User: Montre-moi mes heures d'aujourd'hui
GPT: [appelle getRegisteredHours()]
```

## Étape 5: Publier (optionnel)

- **Only me**: Accessible uniquement par toi
- **Anyone with a link**: Partager avec d'autres (ils auront besoin de leurs propres credentials Tidsreg)
- **Public**: À éviter pour des outils d'entreprise

## Endpoints disponibles

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/api/login` | POST | Authentification |
| `/api/hours` | GET | Récupérer les heures enregistrées |
| `/api/navigate` | POST | Naviguer vers une date |
| `/api/week` | GET/POST | Opérations sur les semaines |
| `/api/customers` | GET | Lister les clients |
| `/api/projects` | GET | Lister les projets |
| `/api/phases` | GET | Lister les phases |
| `/api/activities` | GET | Lister les activités |
| `/api/kinds` | GET | Lister les types |
| `/health` | GET | Vérifier le statut |

## Troubleshooting

### Le GPT ne peut pas se connecter

1. Vérifie que le serveur HTTP est bien démarré
2. Vérifie que localtunnel/ngrok est actif
3. Vérifie que l'URL dans le schéma OpenAPI est correcte
4. Test l'URL manuellement: `curl https://ton-url/health`

### Erreurs d'authentification

- Le serveur maintient une session
- Si tu redémarres le serveur, il faut se reconnecter
- Les cookies sont gérés côté serveur

### Timeout ou réponses lentes

- Le parsing HTML peut prendre quelques secondes
- Augmente le timeout si nécessaire
- Considère mettre en cache certaines réponses

## Améliorations possibles

1. **Authentification OAuth**: Ajouter une vraie auth OAuth au lieu de passer credentials
2. **Cache**: Mettre en cache les résultats fréquents
3. **Webhooks**: Notifier automatiquement des changements
4. **Rate limiting**: Protéger l'API contre les abus
5. **Logs**: Améliorer le logging pour debugging

## Sécurité

⚠️ **Important**:
- Le serveur n'a pas d'authentification API propre
- Toute personne avec l'URL publique peut accéder aux endpoints
- Pour la production, ajoute une clé API ou OAuth
- Ne partage pas l'URL publique
- Utilise HTTPS uniquement (localtunnel/ngrok le font automatiquement)
