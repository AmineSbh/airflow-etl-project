import pytest
from bs4 import BeautifulSoup
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
