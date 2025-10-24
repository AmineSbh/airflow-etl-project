import pytest
import pandas as pd
from pandas.testing import assert_frame_equal
import os
import sys

# --- AJOUTEZ CES LIGNES ---
# 1. Obtenir le dossier racine du projet (qui contient 'scripts_etl' et 'tests')
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 2. Ajouter le dossier racine au path
sys.path.append(PROJECT_ROOT)

# 3. Ajouter le dossier 'scripts_etl' au path (pour les imports internes)
sys.path.append(os.path.join(PROJECT_ROOT, "scripts_etl"))
# --- FIN DE L'AJOUT ---

from scripts_etl.transform import transform


def test_transform_basic():
    """Test de base pour la fonction transform"""
    
    # Données de test
    # CORRECTION : Ajout de la colonne 'date' qui manquait
    test_dict = {
        "symbol": ["AAPL", "GOOGL", "MSFT"],
        "price": [150.0, 2800.0, 300.0],
        "change": [1.5, -0.5, 0.8],
        "date": [1678886400, 1678886401, 1678886402] # Timestamps UNIX
    }

    # Résultat attendu
    # CORRECTION : Ajout de la colonne 'date' convertie
    expected_df = pd.DataFrame(
        {
            "symbol": ["AAPL", "GOOGL", "MSFT"],
            "price": [150.0, 2800.0, 300.0],
            "change": [1.5, -0.5, 0.8],
            # La fonction transform convertit les timestamps en objets datetime
            "date": pd.to_datetime([1678886400, 1678886401, 1678886402], unit="s")
        }
    )

    # Appeler la fonction à tester
    result_df = transform(test_dict)

    # Vérifier que le résultat correspond à ce qui est attendu
    assert_frame_equal(result_df, expected_df)