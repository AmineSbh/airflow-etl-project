from sqlalchemy import create_engine, text
import pandas as pd
import os
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration de la base de données
DB_HOST = "localhost"
DB_PORT = "5433"
DB_NAME = "airflow"  # Changé de airflow_db à airflow
DB_USER = "airflow"  # Changé de airflow_user à airflow
DB_PASSWORD = "airflow"  # Changé de airflow_password à airflow

# Construction de l'URL de connexion
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
)


def load_to_postgresql(dataframe, table_name):
    """Charge un DataFrame pandas dans une table PostgreSQL."""
    try:
        # Log les informations de connexion
        logger.info(
            f"Tentative de connexion à : {DATABASE_URL.replace('airflow:airflow', 'airflow:****')}"
        )
        logger.info(f"DataFrame à charger : \n{dataframe.head()}")

        # Création du moteur SQLAlchemy
        engine = create_engine(DATABASE_URL)

        # Création de la table
        create_table_query = text(
            """
            CREATE TABLE IF NOT EXISTS stock_prices (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100),
                price FLOAT,
                change FLOAT,
                open FLOAT,
                date TIMESTAMP
            )
        """
        )

        with engine.begin() as connection:
            # Crée la table
            connection.execute(create_table_query)

            # Charge les données
            dataframe.to_sql(
                name=table_name, con=connection, if_exists="append", index=False
            )

            # Vérifie le nombre de lignes
            result = connection.execute(
                text(f"SELECT COUNT(*) FROM {table_name}")
            ).scalar()
            logger.info(f"Nombre de lignes dans la table : {result}")

        return True

    except Exception as e:
        logger.error(f"Erreur lors du chargement des données : {e}")
        logger.error(f"Type d'erreur : {type(e).__name__}")
        return False
