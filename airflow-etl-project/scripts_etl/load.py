from sqlalchemy import create_engine, text
import pandas as pd
import os
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Construction de l'URL de connexion depuis les variables d'environnement
DB_HOST = os.getenv("DB_HOST", "postgres")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "airflow")
DB_USER = os.getenv("DB_USER", "airflow")
DB_PASSWORD = os.getenv("DB_PASSWORD", "airflow")

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
)


def load_to_postgresql(dataframe: pd.DataFrame, table_name: str) -> bool:
    """Charge un DataFrame pandas dans une table PostgreSQL en utilisant SQLAlchemy.

    - Nettoie les valeurs 'N/A'
    - Convertit les dates si présentes
    - Utilise to_sql avec un engine SQLAlchemy (nécessite pandas < 2.2.0)
    """
    try:
        # Ne pas logguer le mot de passe en clair
        safe_url = DATABASE_URL.replace(f"://{DB_USER}:{DB_PASSWORD}@", f"://{DB_USER}:****@")
        logger.info(f"Tentative de connexion à : {safe_url}")
        logger.info(f"DataFrame à charger (extrait) : \n{dataframe.head()}")

        # Remplacer les strings N/A par des vrais NA et inférer les types
        dataframe = dataframe.replace({"N/A": pd.NA}).infer_objects(copy=False)

        # Si une colonne 'date' existe, forcer en datetime
        if "date" in dataframe.columns:
            dataframe["date"] = pd.to_datetime(dataframe["date"], errors="coerce", unit=None)

        # Créer un engine SQLAlchemy (pool_pre_ping évite les erreurs de connexion stale)
        engine = create_engine(DATABASE_URL, pool_pre_ping=True)

        # Filtrer les lignes vides (ex: nom absent)
        dataframe = dataframe.dropna(subset=[c for c in ["name"] if c in dataframe.columns], how="any")

        # --- CORRECTION ---
        # Revenir à la méthode standard (con=engine) qui fonctionne
        # parfaitement avec pandas 2.1.4 et les versions antérieures.
        
        logger.info("Tentative d'écriture dans la base de données avec l'engine SQLAlchemy...")
        
        # Ecrire dans la base en chunks
        dataframe.to_sql(
            name=table_name,
            con=engine,  # <-- C'est la méthode correcte avec pandas < 2.2.0
            if_exists="replace",
            index=False,
            method="multi",
            chunksize=1000,
        )
        
        logger.info("Données chargées, vérification du nombre de lignes...")
        
        # Vérification rapide du nombre de lignes
        with engine.connect() as connection_check:
            result = connection_check.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
            count = result.scalar()
            logger.info(f"Nombre de lignes dans la table (après insert): {count}")
            
        logger.info("Opération terminée avec succès.")
        # --- FIN DE LA CORRECTION ---

        return True

    except Exception as e:
        logger.error(f"Erreur lors du chargement des données : {e}")
        logger.error(f"Type d'erreur : {type(e).__name__}")
        raise

