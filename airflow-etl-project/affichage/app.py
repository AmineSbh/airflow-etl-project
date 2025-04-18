import psycopg2
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine
import time
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration de la connexion à la base de données
DB_CONFIG = {
    "host": "localhost",
    "port": "5433",
    "database": "airflow",
    "user": "airflow",
    "password": "airflow",
}


def get_database_url():
    """Construit l'URL de connexion à la base de données."""
    return f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"


def wait_for_database():
    """Attend que la base de données soit disponible."""
    max_retries = 30
    retry_interval = 2

    for i in range(max_retries):
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            conn.close()
            logger.info("Base de données connectée avec succès!")
            return True
        except psycopg2.OperationalError as e:
            logger.warning(
                f"Tentative {i+1}/{max_retries}: La base de données n'est pas encore prête. Nouvelle tentative dans {retry_interval} secondes..."
            )
            time.sleep(retry_interval)

    logger.error(
        "Impossible de se connecter à la base de données après plusieurs tentatives."
    )
    return False


def get_available_tables():
    """Récupère la liste des tables disponibles dans la base de données."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        # Requête pour obtenir toutes les tables publiques
        cur.execute(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
        """
        )

        tables = [table[0] for table in cur.fetchall()]

        cur.close()
        conn.close()

        return tables
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des tables : {e}")
        return []


def fetch_data(table_name):
    """Récupère les données d'une table spécifique."""
    try:
        engine = create_engine(get_database_url())
        query = f"SELECT * FROM {table_name}"
        df = pd.read_sql_query(query, engine)
        return df
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des données : {e}")
        return pd.DataFrame()


def main():
    st.set_page_config(page_title="Dashboard Finance", page_icon="📊", layout="wide")

    st.title("📊 Dashboard Finance")

    # Attendre que la base de données soit prête
    if not wait_for_database():
        st.error(
            "Impossible de se connecter à la base de données. Veuillez vérifier la configuration."
        )
        return

    # Récupérer la liste des tables
    tables = get_available_tables()

    if not tables:
        st.warning("Aucune table n'a été trouvée dans la base de données.")
        return

    # Sélecteur de table
    selected_table = st.selectbox("Sélectionnez une table à afficher:", tables)

    if selected_table:
        # Récupérer et afficher les données
        with st.spinner("Chargement des données..."):
            df = fetch_data(selected_table)

            if df.empty:
                st.error("Erreur lors de la récupération des données.")
            else:
                st.success(f"Données chargées avec succès! ({len(df)} lignes)")

                # Afficher les statistiques de base
                st.subheader("Aperçu des données")
                st.dataframe(df)

                # Afficher les informations sur les colonnes
                st.subheader("Informations sur les colonnes")
                st.write(df.dtypes)

                # Si la table contient des données numériques, afficher des statistiques
                numeric_cols = df.select_dtypes(include=["float64", "int64"]).columns
                if not numeric_cols.empty:
                    st.subheader("Statistiques descriptives")
                    st.write(df[numeric_cols].describe())


if __name__ == "__main__":
    main()
