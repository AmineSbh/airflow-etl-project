import pandas as pd
import numpy as np


def transform(dict_bourse: dict) -> pd.DataFrame:
    """
    Transforme un dictionnaire en DataFrame Pandas.

    Args:
        dict (dict): Dictionnaire à transformer.

    Returns:
        pd.DataFrame: DataFrame contenant les données du dictionnaire.
    """
    # Créer un DataFrame à partir du dictionnaire
    df = pd.DataFrame(dict_bourse)
    df["date"] = pd.to_datetime(df["date"], unit="s")

    # Remplace "N/A" par NaN dans tout le DataFrame
    df = df.replace("N/A", np.nan)

    # Convertit les colonnes numériques au bon type (float)
    for col in ["price", "change", "open"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    # Ajoute une colonne pour le prix d'ouverture
    df

    # Réinitialiser l'index
    df.reset_index(drop=True, inplace=True)

    return df
