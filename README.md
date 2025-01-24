# Automatisation Spotify

Projet pour automatiser la création de comptes Proton, en utilisant ces comptes pour générer des profils Spotify et écouter des playlists complètes de manière automatisée.

Pour activer le tempmail, vous devez configurer cette [API](https://rapidapi.com/tempmailso-tempmailso-default/api/tempmail-so) depuis [Rapid API](https://rapidapi.com/tempmailso-tempmailso-default/api/tempmail-so).

# Démarrage

1. Créez un environnement
```bash
python -m venv .venv
```

2. Activez l'environnement
Sur Linux/MacOS :
```bash
source .venv/bin/activate
```
Sur Windows :
```bash
.\.venv\Scripts\activate
```

3. Installez les dépendances
```bash
pip install -r requirements.txt
```

4. Exécutez l'automatisation Proton
```bash
python app_proton.py
```

5. Exécutez l'automatisation Spotify
```bash
python app_spotify.py
```