# Utiliser une image Python officielle
FROM python:3.9-slim

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Dépendances système pour psycopg2
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       libpq-dev \
       gcc \
    && rm -rf /var/lib/apt/lists/*

# Copier le fichier requirements de Streamlit
# (Assurez-vous d'avoir un requirements.txt dans le dossier ./affichage)
COPY requirements.txt /app/requirements.txt

# Installer les dépendances Python pour Streamlit
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r /app/requirements.txt

# Copier le reste des fichiers de l'application Streamlit
COPY . /app

# Variables d'environnement utiles
ENV PYTHONUNBUFFERED=1

# --- CORRECTION ---
# Commande par défaut pour LANCER STREAMLIT
# Remplacez "votre_app.py" par le nom de votre script Python (ex: dashboard.py, app.py)
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
