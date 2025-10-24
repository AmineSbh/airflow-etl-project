# Utiliser une image Python officielle
FROM python:3.9-slim

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier les fichiers du projet dans le conteneur
# On copie requirements.txt séparément pour optimiser le cache Docker
COPY requirements.txt .

# Installer les dépendances depuis requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# --- AJOUT ---
# Forcer l'installation de SQLAlchemy et psycopg2-binary
# au cas où l'étape précédente aurait utilisé un cache incorrect
RUN pip install --no-cache-dir SQLAlchemy psycopg2-binary
# --- FIN AJOUT ---

# Copier le reste des fichiers
COPY . .

# Installer les navigateurs Playwright
RUN playwright install --with-deps

# Commande par défaut pour exécuter le script
CMD ["python", "extract.py"]