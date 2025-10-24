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
    schedule_interval="@daily",
    start_date=datetime(2023, 1, 1),
    catchup=False,
) as dag:

    etl_task = DockerOperator(
        task_id="run_etl",
        image="etl_image",
        
        # --- CORRECTION ---
        # "python -u" force la sortie non mise en tampon,
        # afin que nous puissions voir les 'print' dans ce log.
        command="python -u /app/extract.py",
        # --- FIN CORRECTION ---
        
        docker_url="unix://var/run/docker.sock",
        auto_remove="success",
        execution_timeout=timedelta(minutes=15),
        network_mode="airflow-etl-project_airflow_network",
        mount_tmp_dir=False,
    )