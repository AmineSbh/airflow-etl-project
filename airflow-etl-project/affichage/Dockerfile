FROM python:3.9-slim

WORKDIR /app

# Installation des dépendances système nécessaires
RUN apt-get update && apt-get install -y \
    libpq-dev gcc && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copie des fichiers requis
COPY requirements.txt .
COPY app.py .

# Installation des dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Exposition du port Streamlit
EXPOSE 8501

# Commande pour démarrer l'application
CMD ["streamlit", "run", "app.py", "--server.address", "0.0.0.0"]