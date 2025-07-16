import os
import pandas as pd
import pytest
from sqlalchemy import create_engine, text

from scripts_etl.load import load_to_postgresql


@pytest.fixture(scope="module")
def pg_engine():
    """Return a SQLAlchemy engine connected to a test PostgreSQL database.

    The fixture expects the environment variable ``TEST_DATABASE_URL`` to be
    defined. If it is not present the tests relying on PostgreSQL are skipped.
    """
    db_url = os.environ.get("TEST_DATABASE_URL")
    if not db_url:
        pytest.skip("TEST_DATABASE_URL not configured")
    engine = create_engine(db_url)

    # Ensure table is clean before running tests
    with engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS stock_prices"))

    yield engine

    # Cleanup after tests
    with engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS stock_prices"))

    engine.dispose()


def test_load_to_postgresql(pg_engine, monkeypatch):
    """Verify that ``load_to_postgresql`` inserts rows in PostgreSQL."""
    db_url = str(pg_engine.url)
    monkeypatch.setenv("DATABASE_URL", db_url)

    data = {
        "name": ["AAPL", "GOOGL", "MSFT"],
        "price": [150.0, 2800.0, 300.0],
        "change": [1.5, -0.5, 0.8],
        "open": [148.0, 2820.0, 298.0],
        "date": ["2023-04-01", "2023-04-01", "2023-04-01"],
    }
    df = pd.DataFrame(data)

    assert load_to_postgresql(df, "stock_prices") is True

    with pg_engine.begin() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM stock_prices")).scalar()
    assert result == len(df)