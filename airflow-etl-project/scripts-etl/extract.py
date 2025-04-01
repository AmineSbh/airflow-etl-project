from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

import httpx
import asyncio

import requests
import yfinance as yf
import pandas as pd


####################
#                  #
# Classe scrapping #
#                  #
####################

# Constants
URL = "https://fr.wikipedia.org/wiki/CAC_40"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}


class CompanyScraper:
    """Classe pour gérer le scraping des entreprises du CAC 40"""

    def __init__(self):
        self.url = URL
        self.headers = HEADERS

    def _extract_company_info(self, columns):
        """Extrait les informations d'une entreprise depuis les colonnes"""
        return {
            "name": columns[1].text.strip(),
            "sector": columns[2].text.strip() if len(columns) > 2 else "N/A",
        }

    def _parse_table(self, table):
        """Parse le tableau et extrait les informations des entreprises"""
        companies = []
        for row in table.find_all("tr")[1:]:
            columns = row.find_all("td")
            if columns:
                companies.append(self._extract_company_info(columns))
        return companies

    def display_results(self, companies):
        """Affiche les résultats du scraping"""
        print(f"{len(companies)} entreprises trouvées:")
        for company in companies:
            print(f"Nom: {company['name']}, Secteur: {company['sector']}")

    def scrape_playwright(self):
        """Méthode utilisant Playwright"""
        with sync_playwright() as playwright:
            # Lancement du navigateur
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page()

            try:
                # Navigation
                url = "https://fr.wikipedia.org/wiki/CAC_40"
                page.goto(url)

                # Extraction du contenu
                html_content = page.content()
                soup = BeautifulSoup(html_content, "html.parser")

                # Recherche du tableau
                table = soup.find("table", {"class": "wikitable"})

                # Extraction des données
                companies = self._parse_table(table)

                return companies

            finally:
                browser.close()

    def scrape_requests(self):
        """Méthode utilisant Requests"""
        try:
            # Envoi de la requête
            response = requests.get(URL, headers=HEADERS)
            response.raise_for_status()

            # Parsing du HTML
            soup = BeautifulSoup(response.text, "html.parser")
            table = soup.find("table", {"class": "wikitable"})

            # Extraction des données
            companies = self._parse_table(table)

            return companies

        except requests.RequestException as e:
            print(f"Erreur lors de la requête: {e}")
            return []

    async def scrape_httpx(self):
        """Méthode utilisant HTTPX"""
        try:
            # Configuration de la requête
            url = "https://fr.wikipedia.org/wiki/CAC_40"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }

            # Envoi de la requête asynchrone
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()

                # Parsing du HTML
                soup = BeautifulSoup(response.text, "html.parser")
                table = soup.find("table", {"class": "wikitable"})

                # Extraction des données
                companies = companies = self._parse_table(table)

                return companies

        except httpx.RequestError as e:
            print(f"Erreur lors de la requête: {e}")
            return []


####################
#                  #
#  Valeur bourse   #
#                  #
####################


def get_stock_prices(companies):
    stock_data = []

    for company in companies:
        # Obtenir le symbole Yahoo Finance (à adapter selon les entreprises)
        ticker = yf.Ticker(f"{company['name']}.PA")  # .PA pour Paris

        try:
            # Obtenir les données en direct
            info = ticker.info
            stock_data.append(
                {
                    "name": company["name"],
                    "price": info.get("regularMarketPrice", "N/A"),
                    "change": info.get("regularMarketChangePercent", "N/A"),
                }
            )
        except Exception as e:
            print(f"Erreur pour {company['name']}: {e}")

    return stock_data


def main():
    """Fonction principale"""
    scraper = CompanyScraper()

    # Test des différentes méthodes
    print("\n=== Playwright ===")
    companies = scraper.scrape_playwright()
    # scraper.display_results(companies)

    # print("\n=== Requests ===")
    # companies = scraper.scrape_requests()
    # scraper.display_results(companies)

    # print("\n=== HTTPX ===")
    # companies = asyncio.run(scraper.scrape_httpx())
    # scraper.display_results(companies)

    # Bourse
    # # Ensuite obtenir les cours
    while 1:
        stock_prices = get_stock_prices(companies)

        # Afficher les résultats
        for stock in stock_prices:
            print(f"{stock['name']}: {stock['price']}€ ({stock['change']}%)")

        asyncio.sleep(10)


if __name__ == "__main__":
    main()
