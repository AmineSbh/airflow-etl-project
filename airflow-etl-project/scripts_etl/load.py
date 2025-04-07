from sqlalchemy import create_engine
import pandas as pd

# Configuration de la base de données PostgreSQL
DB_HOST = "postgres"  # Nom du service PostgreSQL dans Docker Compose
DB_PORT = "5432"
DB_NAME = "finance_db"
DB_USER = "admin"
DB_PASSWORD = "password"


def load_to_postgresql(dataframe, table_name):
    """
    Charge un DataFrame pandas dans une table PostgreSQL.
    """
    try:
        # Connexion à PostgreSQL avec SQLAlchemy
        engine = create_engine(
            f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        )
        with engine.connect() as connection:
            # Charger les données dans PostgreSQL
            dataframe.to_sql(table_name, connection, if_exists="append", index=False)
            print(
                f"Les données ont été chargées dans la table '{table_name}' avec succès."
            )
    except Exception as e:
        print(f"Erreur lors du chargement des données : {e}")


if __name__ == "__main__":
    # Exemple de données transformées
    data = {
        "symbol": ["AAPL", "GOOGL", "MSFT"],
        "date": ["2023-04-01", "2023-04-01", "2023-04-01"],
        "price": [150.0, 2800.0, 300.0],
    }
    df = pd.DataFrame(data)

    # Charger les données dans PostgreSQL
    load_to_postgresql(df, "stock_prices")
