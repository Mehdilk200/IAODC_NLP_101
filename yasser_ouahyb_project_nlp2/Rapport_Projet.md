# Rapport de Projet : Assistant Virtuel NLP (project_nlp2)

## 1. Présentation Générale
Ce projet est une plateforme web intégrant un Chatbot intelligent basé sur le Traitement du Langage Naturel (NLP). Le système est conçu pour être multilingue et a pour objectif d'accompagner les utilisateurs pour tout ce qui concerne l'orientation, les formations (ex: CMC), et le suivi des événements via une interface moderne et intuitive.

## 2. Architecture Technique et Stack Utilisée

### Backend & Modèle d'Intelligence Artificielle
- **Serveur Web :** L'application est propulsée par **Flask** (Python), assurant le rendu des pages (`templates/`) et la mise à disposition des points d'accès API pour le chatbot.
- **Moteur NLP (Natural Language Processing) :**
  - **Sentence-Transformers :** Utilisé pour transformer les textes en vecteurs sémantiques afin de comprendre l'intention derrière le message de l'utilisateur.
  - **Scikit-Learn & Numpy :** Utilisés pour la classification et le traitement mathématique des prédictions.
  - **Langdetect :** Intégré pour détecter avec précision la langue de l'input (Arabe/Darija, Français, Anglais) et forcer le bot à répondre dans cette même langue.
  - **Joblib :** Utilisé pour sérialiser et charger le modèle d'IA entraîné (`model.joblib`).

### Frontend (Interface Client)
- **Technologies Standards :** HTML5, CSS3 natif et JavaScript (Vanilla).
- **Architecture des Fichiers :** 
  - `templates/` (ex: `index.html`, `bot.html`, `orientation.html`) pour la structure.
  - `static/` (ex: `events.css`, `translations.js`, `events.js`) pour le style, la dynamique et la traduction côté client (système bilingue natif).

### Base de Données & Maintenance
- **Fichiers JSON :** Le cerveau explicite du bot repose sur `data/intents.json` (les intentions et mots-clés) et `responses.json` (les réponses formatées).
- **Scripts Utilitaires :**
  - `train_model.py` : Script pour ré-entraîner de zéro le modèle NLP à chaque mise à jour du fichier `intents.json`.
  - `update_formations.py` : Script dédié à la mise à jour (probablement via parsing ou API) de la liste des formations proposées.

## 3. Synthèse des Dernières Fonctionnalités Implémentées

Au cours de nos sessions de travail, le projet a connu des améliorations majeures tant sur le plan algorithmique que visuel :

1. **Amélioration du Moteur de Rendu Linguistique :**
   - Mise en place d'une vérification stricte : le bot détecte si l'utilisateur parle en Arabe (ou Darija) et répond obligatoirement en Arabe, bloquant ainsi les réponses erronées en Français. Même chose pour l'Anglais.
2. **Refonte de l'Expérience Utilisateur (UI/UX) :**
   - **Historique de Chat :** Ajout d'une fonctionnalité premium permettant à l'utilisateur de supprimer des historiques de discussion spécifiques depuis la Sidebar (avec mise à jour en direct via `localStorage`).
   - **Design de la Page d'Accueil (`index.html`) :** Alignement strict sur la maquette cible avec un "Hero section" retravaillé (fond bleu uni, style dashboard full-width).
   - **Section "Les CMC en chiffres" :** Simplification du design (suppression des effets "glassmorphism" très lourds) pour un rendu d'entreprise plus clair, minimaliste et professionnel.
   - **Témoignages (`orientation.html`) :** Création d'une toute nouvelle section de témoignages sous forme de cartes, incluant notations par étoiles, titres bilingues et design aéré.
3. **Correction des Bugs d'Affichage :**
   - **Calendrier des Événements :** Correction de la grille CSS du calendrier (`events.css`) pour s'assurer que les 7 jours de la semaine s'affichent correctement sans être rognés, tout en restant parfaitement alignés avec la liste des événements.

## 4. Conclusion
Le projet `project_nlp2` est aujourd'hui une application solide, alliant un backend robuste propulsé par de l'Intelligence Artificielle précise et un frontend soigné, pensé pour offrir une expérience utilisateur (UX) haut de gamme.
