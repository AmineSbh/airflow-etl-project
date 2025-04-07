import pytest
from bs4 import BeautifulSoup
import pandas as pd
from playwright.async_api import async_playwright
from scripts_etl.extract import CompanyScraper, get_stock_prices

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
