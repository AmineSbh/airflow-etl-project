# import pytest
# from ..scripts_etl.load import *


# def test_load_to_postgresql():
#     """Test de la fonction load_to_postgresql"""
#     # Exemple de données transformées
#     data = {
#         "symbol": ["AAPL", "GOOGL", "MSFT"],
#         "date": ["2023-04-01", "2023-04-01", "2023-04-01"],
#         "price": [150.0, 2800.0, 300.0],
#     }
#     df = pd.DataFrame(data)

#     # Charger les données dans PostgreSQL
#     load_to_postgresql(df, "stock_prices")
