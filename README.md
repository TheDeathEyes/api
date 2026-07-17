# Anime Explorer Web

Une interface de streaming d'animes légère et performante, permettant de rechercher des animes, de consulter les détails (synopsis, trailers) et de visionner les épisodes via une architecture hybride.

## Fonctionnalités

- Recherche d'animes via l'API.
- Extraction automatique des métadonnées (synopsis, images de couverture, trailers).
- Intégration de streaming via iframe avec support de plusieurs lecteurs.
- Système de mise en cache (Proxy PHP) pour réduire les appels API et accélérer le chargement.
- Interface utilisateur minimaliste et réactive.

## Architecture Technique

- **Backend (API) :** Python (Flask) avec BeautifulSoup4 et Requests.
- **Frontend :** HTML5, CSS3, Vanilla JavaScript.
- **Proxy/Cache :** PHP pour la gestion des requêtes et le stockage local des données en JSON.

## Installation

### 1. Backend (API Flask)

1. S'assurer d'avoir Python installé.
2. Installer les dépendances :
   ```bash
   pip install flask requests beautifulsoup4 flask-cors
