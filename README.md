# Projet de Pipeline de Données : Suivi du CAC 40

Ce projet est une application de pipeline de données complète, conçue pour automatiser la collecte, le stockage et la visualisation des cours de la bourse pour les entreprises du CAC 40.

Le pipeline s'exécute de manière entièrement automatisée grâce à Apache Airflow et est entièrement conteneurisé avec Docker. Les données sont ensuite affichées sur un tableau de bord interactif construit avec Streamlit.

[Image d'un schéma d'architecture de données simple]

## 🎯 Objectif

L'objectif est de créer un système robuste et automatisé qui :

Extrait les noms des entreprises du CAC 40 depuis Wikipédia.

Récupère les données boursières (prix, variation, etc.) pour chaque entreprise via l'API yfinance.

Transforme et nettoie ces données.

Charge les données propres dans une base de données PostgreSQL.

Affiche ces données sur un tableau de bord en temps réel.

## 🛠️ Architecture

Ce projet est orchestré par docker-compose et se compose de trois piliers principaux :

Orchestration (Apache Airflow)

Un Scheduler Airflow planifie et déclenche notre tâche ETL à intervalles réguliers (par exemple, 3 fois par jour).

Le Webserver Airflow (accessible sur localhost:8080) vous permet de surveiller, de déclencher manuellement et de déboguer vos pipelines (DAGs).

Pipeline ETL (Docker & Python)

Airflow utilise le DockerOperator pour lancer un conteneur basé sur l'image etl_image.

Ce conteneur exécute le script Python (scripts_etl/extract.py) qui effectue le scraping (avec Playwright) et la collecte des données (yfinance).

Les données sont transformées (transform.py) puis chargées (load.py) dans la base de données.

Stockage & Visualisation (PostgreSQL & Streamlit)

Un service PostgreSQL sert de base de données fiable pour stocker toutes les données historiques collectées.

Un service Streamlit (accessible sur localhost:8501) lit en permanence cette base de données et affiche les informations sur un tableau de bord interactif.

Voici un schéma simple du flux de données :

[Airflow]       ->   [Conteneur ETL (Docker)]   ->   [PostgreSQL]   <-   [Streamlit]
(Planifie)           (Extrait & Charge)           (Stocke)         (Lit & Affiche)


## 🚀 Comment l'utiliser ?

Ce projet est conçu pour être lancé avec une seule commande.

Prérequis

Docker

Docker Compose (généralement inclus avec Docker Desktop)

Configuration (Utilisateurs Linux)

Si vous êtes sous Linux, vous devez créer un fichier .env à la racine du projet pour éviter les problèmes de permissions de fichiers avec Airflow.

echo "AIRFLOW_UID=$(id -u)" > .env


(Les utilisateurs macOS et Windows peuvent généralement ignorer cette étape).

Lancement

Clonez ce dépôt.

Ouvrez un terminal à la racine du projet.

Exécutez la commande suivante :

docker-compose up -d --build


--build : Force la reconstruction de vos images (nécessaire si vous modifiez le code Python).

-d : Lance les conteneurs en mode "detached" (en arrière-plan).

C'est tout ! L'ensemble de l'infrastructure est en cours d'exécution.

🖥️ Accéder aux services

Une fois les conteneurs lancés (cela peut prendre une minute ou deux la première fois) :

Tableau de Bord (Streamlit) :

Ouvrez votre navigateur à l'adresse : http://localhost:8501

### Interface Airflow :

Ouvrez votre navigateur à l'adresse : http://localhost:8080

Identifiant : airflow

Mot de passe : airflow

## 📂 Structure du projet

.
├── affichage/            # Contient le code du dashboard Streamlit
│   ├── Dockerfile        # Instructions pour construire l'image Streamlit
│   └── dashboard.py      # Le script Python de l'application Streamlit
│
├── dags/                 # Contient les scripts de définition des DAGs Airflow
│   └── etl_dag.py        # Le DAG qui définit et planifie notre pipeline ETL
│
├── scripts_etl/          # Le cœur de notre pipeline ETL
│   ├── Dockerfile        # Instructions pour construire l'image 'etl_image'
│   ├── requirements.txt  # Dépendances Python pour l'ETL
│   ├── extract.py        # Script principal (Scraping & API)
│   ├── transform.py      # Script de nettoyage des données
│   └── load.py           # Script de chargement en base de données
│
├── tests/                # Tests unitaires pour valider l'ETL
│   ├── test_extract.py
│   └── ...
│
├── docker-compose.yml    # Le fichier chef d'orchestre qui assemble tout
└── README.md             # Ce fichier


## 💻 Pile technologique

Orchestration : Apache Airflow

Conteneurisation : Docker & Docker Compose

Langage : Python

Base de Données : PostgreSQL

Dashboard : Streamlit

Data Scraping : Playwright (principal), Requests (repli)

Data Fetching : Yfinance

Data Processing : Pandas