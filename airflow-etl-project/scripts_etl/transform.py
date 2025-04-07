import pandas as pd


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

    # Ajoute une colonne pour le prix d'ouverture
    df

    # Réinitialiser l'index
    df.reset_index(drop=True, inplace=True)

    return df
