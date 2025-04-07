from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import httpx
import asyncio
import requests
import yfinance as yf
import pandas as pd

from load import load_to_postgresql

from transform import transform

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

    async def scrape_playwright(self):
        """Méthode utilisant Playwright (version asynchrone)"""
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=True)
            page = await browser.new_page()

            try:
                await page.goto(self.url)
                html_content = await page.content()
                soup = BeautifulSoup(html_content, "html.parser")
                table = soup.find("table", {"class": "wikitable"})
                companies = self._parse_table(table)
                return companies
            finally:
                await browser.close()

    def scrape_requests(self):
        """Méthode utilisant Requests"""
        try:
            response = requests.get(self.url, headers=self.headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            table = soup.find("table", {"class": "wikitable"})
            return self._parse_table(table)
        except requests.RequestException as e:
            print(f"Erreur lors de la requête: {e}")
            return []

    async def scrape_httpx(self):
        """Méthode utilisant HTTPX"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.url, headers=self.headers)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, "html.parser")
                table = soup.find("table", {"class": "wikitable"})
                return self._parse_table(table)
        except httpx.RequestError as e:
            print(f"Erreur lors de la requête: {e}")
            return []


####################
#                  #
#  Valeur bourse   #
#                  #
####################


async def get_stock_prices(companies):
    """Obtenir les prix des actions de manière asynchrone"""
    stock_data = []

    for company in companies:
        try:
            ticker = yf.Ticker(f"{company['name']}.PA")
            info = ticker.info
            stock_data.append(
                {
                    "name": company["name"],
                    "price": info.get("regularMarketPrice", "N/A"),
                    "change": info.get("regularMarketChangePercent", "N/A"),
                    # Ajoute le prix d'ouverture et une date a laquelle il a été pris
                    "open": info.get("regularMarketOpen", "N/A"),
                    # Ajoute une date a laquelle il a été pris
                    "date": info.get("regularMarketTime", "N/A"),
                }
            )
        except Exception as e:
            print(f"Erreur pour {company['name']}: {e}")
            stock_data.append(
                {
                    "name": company["name"],
                    "price": "N/A",
                    "change": "N/A",
                }
            )

    return stock_data


async def main():
    """Fonction principale"""
    scraper = CompanyScraper()

    print("\n=== Scraping des entreprises du CAC 40 ===")
    # Utiliser la méthode Playwright par défaut
    companies = await scraper.scrape_playwright()

    if not companies:
        print("Échec du scraping avec Playwright, tentative avec Requests...")
        companies = scraper.scrape_requests()

    if not companies:
        print("Échec du scraping avec Requests, tentative avec HTTPX...")
        companies = await scraper.scrape_httpx()

    if not companies:
        print("Échec de toutes les méthodes de scraping. Arrêt du programme.")
        return

    print(f"\nSuivi des cours en temps réel pour {len(companies)} entreprises")
    print("Mise à jour toutes les 10 secondes. Ctrl+C pour arrêter.\n")

    try:
        while True:
            stock_prices = await get_stock_prices(companies)

            # Transformation des données
            transformed_data = transform(stock_prices)

            # Chargement des données dans PostgreSQL
            load_to_postgresql(transformed_data, "stock_prices")

            # # Affichage des résultats
            # print("\033[2J\033[H")  # Clear screen
            # print(transformed_data)
            # print("\nDétails des cours:")
            # for stock in stock_prices:
            #     if stock["price"] != "N/A":
            #         print(f"{stock['name']}: {stock['price']}€ ({stock['change']}%)")
            #     else:
            #         print(f"{stock['name']}: Données non disponibles")

            await asyncio.sleep(10)

    except KeyboardInterrupt:
        print("\nArrêt du programme...")
    except Exception as e:
        print(f"\nErreur inattendue: {e}")


if __name__ == "__main__":
    asyncio.run(main())
