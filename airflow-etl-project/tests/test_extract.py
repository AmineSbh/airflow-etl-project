import pytest
from bs4 import BeautifulSoup
import os
import sys

# --- AJOUTEZ CES LIGNES ---
# 1. Obtenir le dossier racine du projet (qui contient 'scripts_etl' et 'tests')
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 2. Ajouter le dossier racine au path
sys.path.append(PROJECT_ROOT)

# 3. Ajouter le dossier 'scripts_etl' au path
# C'est ce qui corrigera "ModuleNotFoundError: No module named 'load'"
sys.path.append(os.path.join(PROJECT_ROOT, "scripts_etl"))
# --- FIN DE L'AJOUT ---

# Maintenant, l'import suivant fonctionnera,
# et quand extract.py importera 'load', il le trouvera.
from scripts_etl.extract import CompanyScraper

# Données de test
SAMPLE_HTML = """
<table class="wikitable">
    <tr>
        <th>Index</th>
        <th>Entreprise</th>
        <th>Secteur</th>
    </tr>
    <tr>
        <td>1</td>
        <td>Total</td>
        <td>Énergie</td>
    </tr>
    <tr>
        <td>2</td>
        <td>BNP Paribas</td>
        <td>Finance</td>
    </tr>
</table>
"""


@pytest.fixture
def scraper():
    """Fixture pour créer une instance de CompanyScraper"""
    return CompanyScraper()


def test_extract_company_info(scraper):
    """Test de l'extraction des informations d'une entreprise"""
    # Créer des colonnes de test
    columns = [
        BeautifulSoup("<td>1</td>", "html.parser").td,
        BeautifulSoup("<td>Total</td>", "html.parser").td,
        BeautifulSoup("<td>Énergie</td>", "html.parser").td,
    ]

    result = scraper._extract_company_info(columns)

    assert isinstance(result, dict)
    assert result["name"] == "Total"
    assert result["sector"] == "Énergie"
