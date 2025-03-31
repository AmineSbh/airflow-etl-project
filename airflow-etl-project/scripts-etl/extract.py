import pandas as pd


def get_cac40_data():
    """
    Extract CAC 40 data from Wikipedia.

    :return: Pandas DataFrame containing the CAC 40 data
    """
    try:
        # Lire tous les tableaux HTML de la page Wikipédia
        tables = pd.read_html("https://fr.wikipedia.org/wiki/CAC_40")

        # Le tableau contenant les données du CAC 40 est généralement le premier ou le deuxième
        # Vous pouvez ajuster l'index si nécessaire
        cac40_table = tables[3]  # Vérifiez l'index du tableau si cela ne fonctionne pas

        # Renommer les colonnes pour plus de clarté (facultatif)
        cac40_table.columns = [
            "Entreprise",
            "Secteur",
            "Siège social",
            "ISIN",
            "Date d'entrée",
        ]

        return cac40_table
    except Exception as e:
        print(f"An error occurred while fetching CAC 40 data: {e}")
        return None


if __name__ == "__main__":
    # Exemple d'utilisation
    cac40_data = get_cac40_data()
    if cac40_data is not None:
        print(cac40_data.head())  # Afficher les 5 premières lignes
