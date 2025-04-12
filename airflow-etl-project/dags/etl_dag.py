from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from datetime import datetime

# Définir le DAG
with DAG(
    dag_id="etl_pipeline",
    start_date=datetime(2023, 1, 1),
    schedule_interval="@daily",
    catchup=False,
) as dag:

    # Tâche : Extraction des données
    extract = DockerOperator(
        task_id="extract_data",
        image="etl_image",  # Image Docker contenant vos scripts ETL
        command="python /app/scripts_etl/extract.py",
        docker_url="unix://var/run/docker.sock",
        network_mode="airflow_network",
    )

    # Tâche : Transformation des données
    transform = DockerOperator(
        task_id="transform_data",
        image="etl_image",
        command="python /app/scripts_etl/transform.py",
        docker_url="unix://var/run/docker.sock",
        network_mode="airflow_network",
    )

    # Tâche : Chargement des données
    load = DockerOperator(
        task_id="load_data",
        image="etl_image",
        command="python /app/scripts_etl/load.py",
        docker_url="unix://var/run/docker.sock",
        network_mode="airflow_network",
    )

    # Définir les dépendances
    extract >> transform >> load
