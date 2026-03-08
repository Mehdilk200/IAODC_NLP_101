# RAGISO AI - Chatbot NLP RAG

> Assistant documentaire intelligent basé sur la technologie RAG (Retrieval-Augmented Generation)

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![MongoDB](https://img.shields.io/badge/MongoDB-6.0+-green.svg)](https://www.mongodb.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Description du projet

**RAGISO AI** est un chatbot intelligent basé sur la technologie RAG (Retrieval-Augmented Generation) conçu pour interagir avec vos documents personnels. Contrairement aux LLMs standards, ce bot utilise une base de données vectorielle pour "lire" vos fichiers et fournir des réponses précises et contextuelles sans hallucinations.

Le système implémente un contrôle d'accès basé sur les rôles (RBAC) permettant de gérer finement les permissions d'accès aux documents selon trois niveaux : administrateur, manager et utilisateur.

### Problème résolu

Les modèles de langage traditionnels (LLMs) ont tendance à inventer des informations lorsqu'ils ne connaissent pas la réponse. Ce projet résout ce problème en :

1. **Indexant vos documents** dans une base de données vectorielle (Chroma)
2. **Récupérant le contexte pertinent** lors de chaque question
3. **Générant des réponses factuelles** basées uniquement sur vos documents
4. **Citant les sources** utilisées pour répondre

## Fonctionnalités principales

### Chatbot Intelligent
- Interaction en langage naturel avec vos documents
- Réponses contextuelles basées sur le contenu de vos fichiers
- Support multilingue (détection automatique de la langue)
- Mise en évidence des termes techniques importants

### 📁 Gestion des Documents
- Upload de fichiers (PDF, TXT, DOCX)
- Traitement automatique des documents (chunking)
- Support des fichiers contenant du code
- Métadonnées enrichies (sections, sources)

### 🔐 Sécurité et Permissions
- Authentification JWT (JSON Web Tokens)
- Hachage sécurisé des mots de passe (PBKDF2)
- Contrôle d'accès basé sur les rôles (RBAC)
- Routes protégées avec garde-middleware

### 💬 Gestion des Conversations
- Création et gestion de conversations multiples
- Historique complet des échanges
- Persistance des messages dans MongoDB

### 🔍 Recherche Sémantique
- Embeddings Gemini pour la recherche vectorielle
- Récupération des k documents les plus pertinents
- Filtrage par rôle utilisateur

## Technologies utilisées

### Backend
| Technologie | Version | Description |
|-------------|---------|-------------|
| **FastAPI** | 0.100+ | Framework web Python moderne et rapide |
| **Motor** | - | Driver MongoDB asynchrone pour Python |
| **LangChain** | - | Framework pour construire des applications LLM |
| **LangChain Classic** | - | Composants LangChain pour le RAG |
| **LangChain Chroma** | - | Intégration Chroma avec LangChain |
| **Google Generative AI** | - | Gemini pour embeddings et génération |
| **Pydantic** | - | Validation des données Python |

### Base de données
| Technologie | Description |
|-------------|-------------|
| **MongoDB** | Base de données NoSQL pour le stockage |
| **Chroma** | Base de données vectorielle pour les embeddings |

### Frontend
| Technologie | Description |
|-------------|-------------|
| **HTML5** | Structure des pages |
| **CSS3** | Stylage moderne avec animations |
| **JavaScript** | Logique côté client |
| **Font Awesome** | Icônes |

### DevOps
| Technologie | Description |
|-------------|-------------|
| **Docker** | Conteneurisation de l'application |
| **Docker Compose** | Orchestration des services |

## Architecture du projet

```
Chatbot_NLP_RAG/
├── docker/                          # Configuration Docker
│   ├── Dockerfile                   # Image Docker de l'application
│   ├── docker-compose.yml           # Orchestration des services
│   ├── cmd.txt                      # Commandes Docker utiles
│   └── data/                        # Données persistantes (Chroma)
├── RAG/                             # Configuration RAG
│   └── script.py                    # Script de configuration
├── data/                            # Stockage des données
│   └── chroma/                      # Base de données vectorielle
│       └── [collections]            # Collections Chroma
└── src/                             # Code source principal
    ├── script.py                    # Point d'entrée FastAPI
    ├── countroller/                 # Contrôleurs métier
    │   ├── RetrievalController.py   # Contrôleur RAG (recherche + génération)
    │   ├── data.py                  # Contrôleur de données
    │   ├── procces.py               # Contrôleur de traitement des fichiers
    │   ├── project.py               # Contrôleur de projet
    │   └── base.py                  # Classe de base des contrôleurs
    ├── database/                    # Couche d'accès aux données
    │   ├── deps.py                  # Dépendances FastAPI pour MongoDB
    │   └── db_schema/               # Schémas de base de données
    │       ├── chunk_rag.py          # Schéma des chunks de documents
    │       ├── project_s.py         # Schéma des projets
    │       ├── user_s.py            # Schéma des utilisateurs
    │       ├── files.py             # Schéma des fichiers
    │       ├── conversation_s.py    # Schéma des conversations
    │       └── message_s.py         # Schéma des messages
    ├── helpers/                     # Utilitaires
    │   └── config.py                # Configuration de l'application
    ├── interface/                   # Interface utilisateur (Frontend)
    │   ├── login.html               # Page de connexion
    │   ├── chat_t.html              # Interface de chat
    │   ├── knowledge_base.html      # Gestion de la base de connaissances
    │   ├── css/                     # Fichiers CSS
    │   │   ├── login.css
    │   │   ├── chatbot.css
    │   │   └── base.css
    │   ├── main/                    # Scripts JavaScript
    │   │   ├── login.js
    │   │   ├── app.js
    │   │   └── knowledge.js
    │   └── assets/                 # Ressources statiques
    ├── middlewares/                # Middlewares FastAPI
    │   └── auth_guard.py           # Garde d'authentification JWT
    ├── models/                     # Modèles de données Pydantic
    │   ├── UserModel.py            # Modèle utilisateur
    │   ├── ProjectModel.py         # Modèle projet
    │   ├── ConversationModel.py    # Modèle conversation
    │   ├── MessageModel.py         # Modèle message
    │   ├── chunkModel.py           # Modèle chunk de document
    │   ├── FileAssetModel.py       # Modèle fichier
    │   ├── BaseDataModel.py        # Classe de base des modèles
    │   └── enums/                  # Énumérations
    │       ├── roles.py            # Rôles (admin, manager, user)
    │       ├── DataBaseEnum.py     # Énumérations base de données
    │       ├── extenctionEnum.py   # Extensions de fichiers supportées
    │       └── const.py            # Constantes globales
    ├── routes/                     # Routes API FastAPI
    │   ├── auth/                   # Authentification
    │   │   ├── auth.py             # Endpoints d'authentification
    │   │   └── schema.py           # Schémas de requêtes/réponses
    │   ├── conversation.py         # Gestion des conversations
    │   ├── data_load.py            # Upload et traitement des fichiers
    │   ├── chain.py                # Pipeline RAG
    │   ├── users/                  # Gestion des utilisateurs
    │   └── schema/                 # Schémas communs
    ├── startup/                    # Scripts de démarrage
    │   └── checkpoints.py          # Vérifications au démarrage
    └── assets/                     # Fichiers uploadés par les utilisateurs
        └── upload_file/            # Répertoire de stockage des fichiers
            ├── admin/
            ├── manager/
            └── user/
```

## Installation

### Prérequis

- Python 3.10 ou supérieur
- Docker et Docker Compose
- MongoDB (inclus dans Docker Compose)

### Étape 1 : Cloner le repository

```bash
git clone <repository-url>
cd Chatbot_NLP_RAG
```

### Étape 2 : Configuration des variables d'environnement

Créez un fichier `.env` dans le répertoire `src/` avec les variables suivantes :

```env
# Configuration Application
APP_NAME=RAGISO_AI
APP_VERSION=1.0.0

# Clé API Google Gemini
KEY_GEMINI=your_google_gemini_api_key_here

# Configuration LLM
MAX_TOKENS=2000

# Configuration fichiers
MAX_FILE_SIZE=10485760
FILE_ALLOWED_EXTNSIONS=["pdf", "txt", "docx"]
FILE_UPLOAD_CHANK_SIZE=1048576

# Configuration MongoDB
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB_NAME=ragiso_db
MONGODB_COLLECTION_NAME=files_metadata
MONGODB_PROJECT_COLLECTION=projects

# Clé secrète JWT
JWT_SECRET=your_super_secret_key_change_in_production
```

### Étape 3 : Lancer avec Docker

```bash
# Construire et lancer les conteneurs
docker compose -f docker/docker-compose.yml up --build

# OU lancer MongoDB uniquement
sudo docker start mongodb-stable
```

### Alternative : Installation locale sans Docker

```bash
# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Installer les dépendances
pip install -r src/requirements.txt

# Lancer l'application
cd src
uvicorn script:app --host 0.0.0.0 --port 8000 --reload
```

## Utilisation

### Démarrage de l'application

Une fois l'application démarrée, accédez à :

- **Interface Web** : http://localhost:8000
- **API Documentation** : http://localhost:8000/docs

### Flux de travail typique

#### 1. Authentification

Connectez-vous avec vos identifiants via l'interface de login. Trois rôles sont disponibles :

- **Admin** : Accès complet à tous les documents
- **Manager** : Accès aux documents de niveau manager
- **User** : Accès aux documents de niveau utilisateur

#### 2. Upload de documents

Utilisez l'interface de gestion de la base de connaissances pour :

1. Téléverser un fichier (PDF, TXT, DOCX)
2. Spécifier la taille des chunks et le chevauchement
3. Lancer le traitement

#### 3. Interaction avec le chatbot

Posez des questions sur vos documents. Le système va :

1. Rechercher les chunks pertinents dans la base vectorielle
2. Générer une réponse basée sur le contexte trouvé
3. Citer les sources utilisées

### Exemple d'API

#### Connexion

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "your_password"
  }'
```

#### Créer une conversation

```bash
curl -X POST "http://localhost:8000/conversations" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Ma première conversation"
  }'
```

#### Envoyer un message

```bash
curl -X POST "http://localhost:8000/conversations/CONVERSATION_ID/messages/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Quel est le contenu de mon document ?"
  }'
```

#### Upload d'un fichier

```bash
curl -X POST "http://localhost:8000/data-load/admin" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "file=@document.pdf"
```

## Structure des données

### Collections MongoDB

| Collection | Description |
|------------|-------------|
| `users` | Utilisateurs et leurs rôles |
| `projects` | Projets associés aux rôles |
| `conversations` | Historique des conversations |
| `messages` | Messages échangés |
| `files_metadata` | Métadonnées des fichiers uploadés |
| `chunks_rag` |Chunks de documents pour le RAG |

### Rôles et permissions

```
┌─────────┬──────────────────────────────────────────┐
│  Rôle   │              Permissions                 │
├─────────┼──────────────────────────────────────────┤
│  Admin  │ Accès à tous les documents              │
│ Manager │ Accès aux documents manager + user      │
│  User   │ Accès aux documents user uniquement     │
└─────────┴──────────────────────────────────────────┘
```

## Améliorations futures possibles

### Fonctionnalités prévues

1. **Support de nouveaux formats**
   - Tableurs (Excel, CSV)
   - Présentations (PowerPoint)
   - Fichiers Markdown

2. **Amélioration du RAG**
   - HyDE (Hypothetical Document Embeddings)
   - Recherche par permutation
   - Fusion derankers

3. **Interface utilisateur**
   - Thèmes clair/sombre
   - Mode hors-ligne
   - Application mobile

4. **Sécurité**
   - OAuth2 avec Google/GitHub
   - Authentification à deux facteurs (2FA)
   - Chiffrement des données au repos

5. **Monitoring et analytics**
   - Tableau de bord administrateur
   - Statistiques d'utilisation
   - Logs détaillés

### Contributions

Les contributions sont les bienvenues ! Veuillez suivre ces étapes :

1. Fork le projet
2. Créer une branche (`git checkout -b feature/ameliocation`)
3. Commit vos changements (`git commit -m 'Ajouter une fonctionnalité'`)
4. Pusher la branche (`git push origin feature/ameliocation`)
5. Ouvrir une Pull Request

## Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## Auteur

Développé avec ❤️ par l'équipe RAGISO

---

*Ce projet utilise la technologie RAG (Retrieval-Augmented Generation) pour fournir des réponses précises basées sur vos documents personnels.*

