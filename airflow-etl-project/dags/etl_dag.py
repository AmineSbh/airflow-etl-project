from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from datetime import datetime, timedelta

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    "etl_pipeline",
    default_args=default_args,
    description="Pipeline ETL pour exécuter extract.py",
    schedule_interval="@daily",  # Exécuter tous les jours
    start_date=datetime(2023, 1, 1),
    catchup=False,
) as dag:

    etl_task = DockerOperator(
        task_id="run_etl",
        image="etl_image",  # Nom de l'image Docker pour votre script ETL
        command="python /app/extract.py",  # Commande à exécuter dans le conteneur
        docker_url="unix://var/run/docker.sock",  # URL Docker
        network_mode="airflow_network",  # Réseau Docker
        auto_remove="success"
    )

