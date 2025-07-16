# airflow-etl-project
+
 Projet complet permettant de créer des pipelines de données.
+
+## Services
+
+Chaque service défini dans `docker-compose.yml` a un rôle précis :
+
+- **postgres** : base de données PostgreSQL utilisée par Airflow et pour stocker les données de l'ETL.
+- **streamlit** : application Streamlit (dossier `affichage`) permettant de visualiser les résultats, exposée sur le port `8501`.
+- **etl** : conteneur chargé d'exécuter les scripts d'extraction, de transformation et de chargement présents dans `scripts_etl`.
+- **airflow-webserver** : interface web d'Airflow disponible sur le port `8080`.
+- **airflow-scheduler** : service planifiant l'exécution des tâches définies dans les DAGs.
+- **airflow-triggerer** : gère les triggers asynchrones d'Airflow.
+- **airflow-init** : initialise la base de métadonnées et crée l'utilisateur par défaut.
+
+Un bloc `x-airflow-common` est utilisé pour partager la configuration entre les services Airflow.
+
+## Construction et démarrage
+
+Assurez-vous d'avoir Docker et Docker Compose installés, puis exécutez :
+
+```bash
+cd airflow-etl-project
+docker compose up --build -d
+```
+
+Les services seront alors accessibles sur les ports définis dans le fichier compose. Pour arrêter l'ensemble :
+
+```bash
+docker compose down
+```
+
+## Lancer les tests
+
+Les tests unitaires se trouvent dans `airflow-etl-project/tests` et utilisent `pytest`. Pour les exécuter dans le conteneur ETL :
+
+```bash
+docker compose run --rm etl pytest
+```
