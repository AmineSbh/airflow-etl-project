from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import httpx
import asyncio
import requests
import yfinance as yf
import pandas as pd
from load import load_to_postgresql
from transform import transform
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

URL = "https://fr.wikipedia.org/wiki/CAC_40"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}


class CompanyScraper:
    def __init__(self):
        self.url = URL
        self.headers = HEADERS

    def _extract_company_info(self, columns):
        return {"name": columns[1].text.strip(), "sector": columns[2].text.strip() if len(columns) > 2 else "N/A"}

    def _parse_table(self, table):
        companies = []
        if table is None:
            return companies
        for row in table.find_all("tr")[1:]:
            columns = row.find_all("td")
            if columns:
                companies.append(self._extract_company_info(columns))
        return companies

    def display_results(self, companies):
        logger.info(f"{len(companies)} entreprises trouvées:")
        for company in companies:
            logger.info(f"Nom: {company['name']}, Secteur: {company['sector']}")

    async def scrape_playwright(self):
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
        try:
            response = requests.get(self.url, headers=self.headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            table = soup.find("table", {"class": "wikitable"})
            return self._parse_table(table)
        except requests.RequestException as e:
            logger.error(f"Erreur lors de la requête avec requests: {e}")
            return []

    async def scrape_httpx(self):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(self.url, headers=self.headers)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, "html.parser")
                table = soup.find("table", {"class": "wikitable"})
                return self._parse_table(table)
        except httpx.RequestError as e:
            logger.error(f"Erreur lors de la requête avec httpx: {e}")
            return []


async def get_stock_prices(companies):
    stock_data = []
    for company in companies:
        name = company.get("name")
        try:
            # Utiliser le ticker en .PA (Euronext Paris). Si introuvable, yfinance lève parfois.
            ticker = yf.Ticker(f"{name}.PA")
            info = ticker.info

            price = info.get("regularMarketPrice")
            change = info.get("regularMarketChangePercent")
            open_ = info.get("regularMarketOpen")
            market_time = info.get("regularMarketTime")

            # Si market_time est un timestamp int, le convertir
            if isinstance(market_time, (int, float)):
                date = pd.to_datetime(market_time, unit="s", origin="unix")
            else:
                date = market_time

            stock_data.append(
                {
                    "name": name,
                    "price": price if price is not None else "N/A",
                    "change": change if change is not None else "N/A",
                    "open": open_ if open_ is not None else "N/A",
                    "date": date if date is not None else "N/A",
                }
            )
        except Exception as e:
            logger.error(f"Erreur pour {name}: {e}")
            stock_data.append(
                {"name": name, "price": "N/A", "change": "N/A", "open": "N/A", "date": "N/A"}
            )
    return stock_data


async def main():
    scraper = CompanyScraper()
    logger.info("\n=== Scraping des entreprises du CAC 40 ===")
    companies = []
    try:
        # Essayer Playwright en premier
        companies = await scraper.scrape_playwright()
    except Exception as e:
        logger.warning(f"Playwright failed: {e}")

    if not companies:
        logger.info("Échec du scraping avec Playwright, tentative avec Requests...")
        companies = scraper.scrape_requests()

    if not companies:
        logger.info("Échec du scraping avec Requests, tentative avec HTTPX...")
        companies = await scraper.scrape_httpx()

    if not companies:
        logger.error("Échec de toutes les méthodes de scraping. Arrêt du programme.")
        return

    logger.info(f"\nSuivi des cours pour {len(companies)} entreprises")

    try:
        stock_prices = await get_stock_prices(companies)
        transformed_data = transform(stock_prices)
        # transformed_data devrait être un DataFrame
        load_to_postgresql(transformed_data, "stock_prices")
        logger.info("\nPipeline ETL terminé avec succès.")

    except Exception as e:
        logger.error(f"\nErreur inattendue: {e}")
        # Renvoyer l'exception pour que Airflow marque la tâche comme failed
        raise


if __name__ == "__main__":
    asyncio.run(main())