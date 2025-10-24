# --- IMPORTATIONS DES BIBLIOTHÈQUES ---
# Playwright: Pour le scraping web asynchrone (moderne, gère le JavaScript)
from playwright.async_api import async_playwright
# BeautifulSoup: Pour parser (analyser) le code HTML
from bs4 import BeautifulSoup
# Httpx: Un client HTTP asynchrone moderne (pour le scraping de repli)
import httpx

# Asyncio: Nécessaire pour gérer les fonctions asynchrones (async/await)
import asyncio

# Requests: Un client HTTP synchrone simple (pour le scraping de repli)
import requests

# Yfinance: Bibliothèque de Yahoo Finance pour récupérer les données boursières
import yfinance as yf

# Pandas: Pour la manipulation des données (DataFrames)
import pandas as pd

# Importations de vos propres modules (scripts dans le même dossier)
from load import load_to_postgresql  # Votre script pour charger les données
from transform import transform      # Votre script pour transformer les données

# Logging: Pour afficher des informations pendant l'exécution
import logging

# Configuration de base du logging pour afficher les messages de niveau INFO
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# --- CONSTANTES ---
URL = "https://fr.wikipedia.org/wiki/CAC_40"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}


# --- CLASSE DE SCRAPING ---

class CompanyScraper:
    """
    Une classe qui regroupe toutes les méthodes de scraping
    pour récupérer la liste des entreprises du CAC 40 depuis Wikipedia.
    """
    def __init__(self):
        """Constructeur de la classe."""
        self.url = URL
        self.headers = HEADERS

    def _extract_company_info(self, columns):
        """Méthode privée pour extraire les infos d'une ligne <tr> du tableau."""
        return {
            "name": columns[1].text.strip(),
            "sector": columns[2].text.strip() if len(columns) > 2 else "N/A"
        }

    def _parse_table(self, table):
        """Méthode privée pour analyser l'objet table BeautifulSoup."""
        companies = []
        if table is None:
            return companies
        
        # Itère sur toutes les lignes <tr> du tableau, en sautant la première (l'en-tête)
        for row in table.find_all("tr")[1:]:
            columns = row.find_all("td")  # Récupère toutes les colonnes <td>
            if columns:
                companies.append(self._extract_company_info(columns))
        return companies

    def display_results(self, companies):
        """Méthode utilitaire pour afficher les résultats (non utilisée dans main)."""
        logger.info(f"{len(companies)} entreprises trouvées:")
        for company in companies:
            logger.info(f"Nom: {company['name']}, Secteur: {company['sector']}")

    # --- MÉTHODES DE SCRAPING (AVEC FALLBACKS) ---

    async def scrape_playwright(self):
        """
        STRATÉGIE 1 (Principale): Utilise Playwright.
        Lance un vrai navigateur (headless) pour charger la page.
        Garantit que le JavaScript est exécuté s'il y en a.
        """
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=True)
            page = await browser.new_page()
            try:
                await page.goto(self.url)
                # Récupère le contenu HTML *après* exécution du JavaScript
                html_content = await page.content()
                soup = BeautifulSoup(html_content, "html.parser")
                table = soup.find("table", {"class": "wikitable"})
                companies = self._parse_table(table)
                return companies
            finally:
                # Assure que le navigateur est fermé même en cas d'erreur
                await browser.close()

    def scrape_requests(self):
        """
        STRATÉGIE 2 (Repli): Utilise Requests.
        Beaucoup plus rapide, mais ne gère pas le JavaScript.
        Pour Wikipedia, c'est suffisant.
        """
        try:
            response = requests.get(self.url, headers=self.headers)
            response.raise_for_status()  # Lève une erreur si le statut HTTP est 4xx ou 5xx
            soup = BeautifulSoup(response.text, "html.parser")
            table = soup.find("table", {"class": "wikitable"})
            return self._parse_table(table)
        except requests.RequestException as e:
            logger.error(f"Erreur lors de la requête avec requests: {e}")
            return []

    async def scrape_httpx(self):
        """
        STRATÉGIE 3 (Repli): Utilise HTTPX (version asynchrone de Requests).
        """
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


# --- PARTIE TÉLÉCHARGEMENT DES DONNÉES BOURSIÈRES ---

async def get_stock_prices(companies):
    """
    Prend la liste des noms d'entreprises et utilise yfinance
    pour récupérer leurs cours de bourse actuels.
    """
    stock_data = []
    for company in companies:
        name = company.get("name")
        try:
            # yfinance a besoin du "ticker". Pour les actions du CAC 40 (Euronext Paris),
            # le ticker est souvent suivi de ".PA".
            ticker = yf.Ticker(f"{name}.PA")
            info = ticker.info  # Fait l'appel API

            # Utilise .get() pour éviter les erreurs si une clé n'existe pas
            price = info.get("regularMarketPrice")
            change = info.get("regularMarketChangePercent")
            open_ = info.get("regularMarketOpen")
            market_time = info.get("regularMarketTime")

            # yfinance peut retourner un timestamp (int) ou une date (str)
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
            # Si le ticker n'est pas trouvé (ex: yfinance ne trouve pas "Total.PA"),
            # on log l'erreur mais on continue la boucle.
            logger.error(f"Erreur pour {name}: {e}")
            stock_data.append(
                {"name": name, "price": "N/A", "change": "N/A", "open": "N/A", "date": "N/A"}
            )
    return stock_data


# --- FONCTION PRINCIPALE (PIPELINE ETL) ---

async def main():
    """
    Orchestre l'ensemble du pipeline ETL :
    1. Extract (Scraping)
    2. Extract (API yfinance)
    3. Transform
    4. Load
    """
    scraper = CompanyScraper()
    logger.info("\n=== Scraping des entreprises du CAC 40 ===")
    companies = []
    
    # Etape 1: EXTRACT (Scraping) - avec 3 niveaux de repli
    try:
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
        # Etape 2: EXTRACT (API)
        stock_prices = await get_stock_prices(companies) # C'est une liste de dictionnaires
        
        # Etape 3: TRANSFORM
        # Le script transform.py prend la liste, la convertit en DataFrame
        # et la nettoie (gère les 'N/A', convertit les types).
        transformed_data = transform(stock_prices)
        
        # Etape 4: LOAD
        # Le script load.py prend le DataFrame transformé et le charge dans PostgreSQL.
        load_to_postgresql(transformed_data, "stock_prices")
        
        logger.info("\nPipeline ETL terminé avec succès.")

    except Exception as e:
        logger.error(f"\nErreur inattendue: {e}")
        # On "relève" l'exception pour qu'Airflow (ou Docker)
        # voie que le script a échoué.
        raise


# --- POINT D'ENTRÉE ---

if __name__ == "__main__":
    # Lance la fonction principale asynchrone
    asyncio.run(main())