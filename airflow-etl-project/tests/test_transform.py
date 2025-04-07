import pytest
import pandas as pd
from pandas.testing import assert_frame_equal
from airflow_etl_project.scripts_etl.transform import transform


def test_transform_basic():
    """Test de base pour la fonction transform"""
    # Données de test
    test_dict = {
        "symbol": ["AAPL", "GOOGL", "MSFT"],
        "price": [150.0, 2800.0, 300.0],
        "change": [1.5, -0.5, 0.8],
    }

    # Résultat attendu
    expected_df = pd.DataFrame(
        {
            "symbol": ["AAPL", "GOOGL", "MSFT"],
            "price": [150.0, 2800.0, 300.0],
            "change": [1.5, -0.5, 0.8],
        }
    )

    # Appeler la fonction
    result_df = transform(test_dict)

    # Vérifier que le résultat correspond à ce qui est attendu
    assert_frame_equal(result_df, expected_df)
